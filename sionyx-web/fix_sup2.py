content = open(r'.\src\supervisor\pages\SupervisorMessagesPage.jsx', encoding='utf-8').read()
old = """import { getOrgMessages, sendSupervisorMessage } from '../services/supervisorMessageService';"""
new = """import { getOrgMessages, sendSupervisorMessage, getOrgUserReplies } from '../services/supervisorMessageService';"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\supervisor\pages\SupervisorMessagesPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
