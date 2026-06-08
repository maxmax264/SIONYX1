path = r'.\installer\Package.wxs'
content = open(path, encoding='utf-8').read()

old = 'Condition="NOT Installed AND NOT REMOVE"'
new = 'Condition="NOT REMOVE"'

count = content.count(old)
print(f"Found: {count}")
content = content.replace(old, new)
open(path, 'w', encoding='utf-8').write(content)
print("OK")
