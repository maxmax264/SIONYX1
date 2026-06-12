content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()

old = """              <List.Item style={{ padding: '6px 16px', border: 'none', justifyContent: isMine ? 'flex-end' : 'flex-start' }}>
                <div style={{ maxWidth: '70%', display: 'flex', flexDirection: 'column', alignItems: isMine ? 'flex-end' : 'flex-start' }}>"""

new = """              <List.Item style={{ padding: '4px 16px', border: 'none', display: 'block' }}>
                <div style={{ display: 'flex', justifyContent: isMine ? 'flex-end' : 'flex-start' }}>
                <div style={{ maxWidth: '70%', display: 'flex', flexDirection: 'column', alignItems: isMine ? 'flex-end' : 'flex-start' }}>"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
