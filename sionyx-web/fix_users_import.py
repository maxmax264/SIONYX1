content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "import { useOrgId } from '../hooks/useOrgId';"
new = "import { useOrgId } from '../hooks/useOrgId';\nimport { ref, onValue, off } from 'firebase/database';\nimport { database } from '../config/firebase';"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
