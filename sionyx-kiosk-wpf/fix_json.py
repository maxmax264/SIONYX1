content = open(r'C:\Users\user\Desktop\sionyx-auth-server\index.js', encoding='utf-8').read()
old = "app.use((req, res, next) => {"
new = "app.use(express.json());\n\napp.use((req, res, next) => {"
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\sionyx-auth-server\index.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
