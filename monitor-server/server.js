// SIONYX connection monitor. Runs on Render. Uses NO Firebase at all:
// kiosks POST a heartbeat over plain HTTP, state lives in this process's RAM.
const express = require('express');
const crypto = require('crypto');

const PORT = process.env.PORT || 3000;
const REPORT_KEY = process.env.REPORT_KEY || '';
const DASH_PASSWORD = process.env.DASH_PASSWORD || '';
const STALE_MS = 45_000;       // no heartbeat for this long => "offline"
const FORGET_MS = 10 * 60_000; // drop rows silent for this long
const HISTORY_MAX = 480;       // 2h at 15s
const WARN_STREAMS = 6;        // a single process above this is flagged

const app = express();
app.use(express.json({ limit: '16kb' }));

const rows = new Map();   // "machine|process" -> row
const history = [];       // {t,total}

const safeEq = (a, b) => {
  const x = Buffer.from(String(a)), y = Buffer.from(String(b));
  return x.length === y.length && crypto.timingSafeEqual(x, y);
};

function dashAuth(req, res, next) {
  if (!DASH_PASSWORD) return res.status(503).send('DASH_PASSWORD not configured');
  const h = req.headers.authorization || '';
  if (h.startsWith('Basic ')) {
    const pass = Buffer.from(h.slice(6), 'base64').toString().split(':').slice(1).join(':');
    if (safeEq(pass, DASH_PASSWORD)) return next();
  }
  res.set('WWW-Authenticate', 'Basic realm="SIONYX monitor"').status(401).send('Auth required');
}

app.get('/health', (_req, res) => res.send('ok'));

app.post('/report', (req, res) => {
  if (!REPORT_KEY || !safeEq(req.headers['x-report-key'] || '', REPORT_KEY)) return res.sendStatus(401);
  const b = req.body || {};
  const machine = String(b.machine || '').slice(0, 64);
  const proc = String(b.process || '').slice(0, 32);
  if (!machine || !proc) return res.sendStatus(400);
  rows.set(`${machine}|${proc}`, {
    machine, process: proc,
    version: String(b.version || '').slice(0, 32),
    state: String(b.state || '').slice(0, 32),
    sse: Math.max(0, Number(b.sse) | 0),
    paths: Array.isArray(b.paths) ? b.paths.slice(0, 20).map(p => String(p).slice(0, 120)) : [],
    attempts: Math.max(0, Number(b.attempts) | 0),   // SSE connection attempts, cumulative
    uptimeSec: Math.max(0, Number(b.uptimeSec) | 0),
    lastSeen: Date.now(),
    prevAttempts: (rows.get(`${machine}|${proc}`) || {}).attempts,
    prevSeen: (rows.get(`${machine}|${proc}`) || {}).lastSeen,
  });
  res.sendStatus(204);
});

function snapshot() {
  const now = Date.now();
  const list = [];
  for (const [k, r] of rows) {
    const age = now - r.lastSeen;
    if (age > FORGET_MS) { rows.delete(k); continue; }
    let attemptsPerMin = null;
    if (r.prevAttempts != null && r.prevSeen && r.attempts >= r.prevAttempts && r.lastSeen > r.prevSeen)
      attemptsPerMin = Math.round(((r.attempts - r.prevAttempts) * 60_000) / (r.lastSeen - r.prevSeen));
    const online = age <= STALE_MS;
    list.push({
      machine: r.machine, process: r.process, version: r.version, state: r.state,
      sse: online ? r.sse : 0, paths: r.paths, online, ageSec: Math.round(age / 1000),
      attemptsPerMin, uptimeSec: r.uptimeSec,
      warn: online && (r.sse > WARN_STREAMS || (attemptsPerMin != null && attemptsPerMin > 20)),
    });
  }
  list.sort((a, b) => b.sse - a.sse || a.machine.localeCompare(b.machine));
  return { now, total: list.reduce((s, r) => s + r.sse, 0), rows: list, history };
}

setInterval(() => {
  history.push({ t: Date.now(), total: snapshot().total });
  if (history.length > HISTORY_MAX) history.shift();
}, 15_000).unref();

app.get('/api/state', dashAuth, (_req, res) => res.json(snapshot()));

app.get('/events', dashAuth, (req, res) => {
  res.set({ 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', Connection: 'keep-alive' });
  const send = () => res.write(`data: ${JSON.stringify(snapshot())}\n\n`);
  send();
  const iv = setInterval(send, 5000);
  req.on('close', () => clearInterval(iv));
});

app.get('/', dashAuth, (_req, res) => res.type('html').send(PAGE));

const PAGE = `<!doctype html><html lang="he" dir="rtl"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>SIONYX – חיבורים</title>
<style>
body{font-family:system-ui,Arial;margin:0;background:#0f172a;color:#e2e8f0}
header{padding:16px 20px;display:flex;gap:24px;align-items:baseline;flex-wrap:wrap}
h1{font-size:18px;margin:0}.big{font-size:44px;font-weight:700}
.sub{color:#94a3b8;font-size:13px}main{padding:0 20px 24px}
canvas{width:100%;height:140px;background:#111c33;border-radius:8px}
table{width:100%;border-collapse:collapse;margin-top:14px;font-size:14px}
th,td{padding:8px 10px;text-align:right;border-bottom:1px solid #1e293b;vertical-align:top}
th{color:#94a3b8;font-weight:500}.off{opacity:.45}.warn{background:#7f1d1d55}
.paths{color:#94a3b8;font-size:12px;direction:ltr;text-align:left}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-left:6px}
</style>
<header><h1>חיבורים פעילים (לפי דיווח הקיוסקים)</h1><div class="big" id="total">–</div>
<div class="sub">מדווחים בלבד. אם Firebase מראה יותר, ההפרש מגיע ממקור שלא מדווח.</div></header>
<main><canvas id="c" width="1200" height="140"></canvas>
<table><thead><tr><th>מחשב</th><th>תהליך</th><th>גרסה</th><th>זרמים</th><th>התחברויות/דקה</th><th>מצב</th><th>נתיבים</th></tr></thead>
<tbody id="rows"></tbody></table></main>
<script>
const $=id=>document.getElementById(id);
function draw(h){const c=$('c'),x=c.getContext('2d');x.clearRect(0,0,c.width,c.height);if(h.length<2)return;
const max=Math.max(100,...h.map(p=>p.total));x.strokeStyle='#475569';x.beginPath();
const y100=c.height-(100/max)*(c.height-10)-5;x.moveTo(0,y100);x.lineTo(c.width,y100);x.stroke();
x.strokeStyle='#38bdf8';x.lineWidth=2;x.beginPath();
h.forEach((p,i)=>{const px=i/(h.length-1)*c.width,py=c.height-(p.total/max)*(c.height-10)-5;i?x.lineTo(px,py):x.moveTo(px,py)});x.stroke()}
function render(s){$('total').textContent=s.total;draw(s.history);
$('rows').innerHTML=s.rows.map(r=>'<tr class="'+(r.online?'':'off ')+(r.warn?'warn':'')+'"><td>'+r.machine+'</td><td>'+r.process+
'</td><td>'+r.version+'</td><td><b>'+r.sse+'</b></td><td>'+(r.attemptsPerMin??'')+'</td><td><span class="dot" style="background:'+
(r.online?'#22c55e':'#64748b')+'"></span>'+(r.online?r.state:'לא מדווח '+r.ageSec+'ש׳')+'</td><td class="paths">'+r.paths.join('<br>')+'</td></tr>').join('')}
const es=new EventSource('/events');es.onmessage=e=>render(JSON.parse(e.data));
</script></html>`;

app.listen(PORT, () => console.log(`monitor listening on ${PORT}`));
