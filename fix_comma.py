f=open(r'database.rules.json', encoding='utf-8')
c=f.read()
f.close()
old='"kioskRefreshAt": { ".read": true }\n          ".read"'
new='"kioskRefreshAt": { ".read": true },\n          ".read"'
assert c.count(old)==1
c=c.replace(old,new,1)
open(r'database.rules.json','w',encoding='utf-8').write(c)
print('OK')
