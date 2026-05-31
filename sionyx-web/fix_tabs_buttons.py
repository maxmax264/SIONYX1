content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = """        {selectedUser && (
          <Tabs activeKey={userHistoryTab} onChange={setUserHistoryTab} centered style={{ marginTop: 48, marginBottom: 16, borderTop: '2px solid #f0f0f0', paddingTop: 24 }} items={[
            { key: 'purchases', label: <span style={{padding:'0 12px'}}>רכישות</span> },
            { key: 'sessions', label: <span style={{padding:'0 12px'}}>שימוש ({userSessions.length})</span> },
            { key: 'prints', label: <span style={{padding:'0 12px'}}>הדפסות ({userPrints.length})</span> },
          ]} />
        )}"""
new = """        {selectedUser && (
          <div style={{ marginTop: 48, borderTop: '2px solid #f0f0f0', paddingTop: 24, display: 'flex', justifyContent: 'space-evenly', marginBottom: 16 }}>
            {['purchases','sessions','prints'].map((tab, i) => {
              const labels = ['רכישות', 'שימוש (' + userSessions.length + ')', 'הדפסות (' + userPrints.length + ')'];
              return <button key={tab} onClick={() => setUserHistoryTab(tab)} style={{ background: 'none', border: 'none', borderBottom: userHistoryTab === tab ? '2px solid #1677ff' : '2px solid transparent', color: userHistoryTab === tab ? '#1677ff' : '#666', fontWeight: userHistoryTab === tab ? 600 : 400, fontSize: 14, padding: '8px 0', cursor: 'pointer', flex: 1, textAlign: 'center' }}>{labels[i]}</button>;
            })}
          </div>
        )}"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
