content = open(r'.\src\services\userService.js', encoding='utf-8').read()

old = "import { ref, get, update, remove, getDatabase } from 'firebase/database';"
new = "import { ref, get, update, remove, getDatabase, push, set } from 'firebase/database';"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\services\userService.js', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
