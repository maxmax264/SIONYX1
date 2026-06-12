content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()

old = """  const [sending, setSending] = useState(false);"""

new = """  const [sending, setSending] = useState(false);
  const [deletedIds, setDeletedIds] = useState(() => {
    try { return JSON.parse(localStorage.getItem('sup_deleted_ids') || '[]'); } catch { return []; }
  });"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
