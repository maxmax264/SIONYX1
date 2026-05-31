content = open(r'.\src\owner\OwnerProtectedRoute.jsx', encoding='utf-8').read()
old = 'import { database } from "../../config/firebase";'
new = 'import { database } from "../config/firebase";'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\owner\OwnerProtectedRoute.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
