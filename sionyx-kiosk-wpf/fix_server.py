content = open(r'C:\Users\user\Desktop\sionyx-auth-server\index.js', encoding='utf-8').read()
old = "// Auto-update endpoint\napp.get('/latest-version', async (req, res) => {"
new = """// Auto-update: write (called from upload_release.py)
app.post('/set-latest-version', async (req, res) => {
  try {
    const secret = req.headers['x-sionyx-secret'];
    if (secret !== process.env.SIONYX_ADMIN_SECRET) {
      return res.status(401).json({ error: 'Unauthorized' });
    }
    const { version, downloadUrl, buildNumber, releasedAt } = req.body;
    if (!version || !downloadUrl) return res.status(400).json({ error: 'Missing fields' });
    await admin.database().ref('system/update').set({ version, downloadUrl, buildNumber, releasedAt });
    console.log('[update] set latest version:', version);
    res.json({ ok: true });
  } catch (e) {
    console.error('[update] set error:', e.message);
    res.status(500).json({ error: e.message });
  }
});

// Auto-update endpoint
app.get('/latest-version', async (req, res) => {"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\sionyx-auth-server\index.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
