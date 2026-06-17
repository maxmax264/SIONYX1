content = open(r'C:\Users\user\Desktop\sionyx-auth-server\index.js', encoding='utf-8').read()

old = '''app.get('/', (req, res) => {
  res.send('SIONYX Auth Server running');
});'''

new = '''app.get('/', (req, res) => {
  res.send('SIONYX Auth Server running');
});

// Auto-update endpoint
app.get('/latest-version', async (req, res) => {
  try {
    const data = await dbGet('system/update');
    if (!data || !data.version) {
      return res.json({ version: null, downloadUrl: null });
    }
    res.json({ version: data.version, downloadUrl: data.downloadUrl });
  } catch (e) {
    console.error('[update] error:', e.message);
    res.status(500).json({ error: e.message });
  }
});'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\sionyx-auth-server\index.js', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
