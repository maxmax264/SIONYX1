f=open(r'.\src\config\firebase.js', encoding='utf-8')
c=f.read()
f.close()

old = "import { getFunctions } from 'firebase/functions';"
new = "import { getFunctions } from 'firebase/functions';\nimport { getStorage } from 'firebase/storage';"

c = c.replace(old, new, 1)

old2 = "export const functions = getFunctions(app, 'us-central1');"
new2 = "export const functions = getFunctions(app, 'us-central1');\nexport const storage = getStorage(app);"

c = c.replace(old2, new2, 1)
open(r'.\src\config\firebase.js', 'w', encoding='utf-8').write(c)
print("OK")
