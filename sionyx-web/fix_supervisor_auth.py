content = open(r'.\src\supervisor\services\supervisorOrgService.js', encoding='utf-8').read()

old = "import { useSupervisorAuthStore } from '../store/supervisorAuthStore';\n\nexport const getSupervisorOrgs = async () => {\n  try {\n    const user = auth.currentUser;\n    if (!user) return { success: false, error: 'Not authenticated', organizations: [] };"

new = "import { useSupervisorAuthStore } from '../store/supervisorAuthStore';\n\nconst waitForAuth = () =>\n  new Promise(resolve => {\n    if (auth.currentUser) return resolve(auth.currentUser);\n    const unsub = auth.onAuthStateChanged(user => { unsub(); resolve(user); });\n  });\n\nexport const getSupervisorOrgs = async () => {\n  try {\n    const user = await waitForAuth();\n    if (!user) return { success: false, error: 'Not authenticated', organizations: [] };"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\supervisor\services\supervisorOrgService.js', 'w', encoding='utf-8').write(content)
    print("OK - file written")
else:
    print("NOT FOUND - stop")
