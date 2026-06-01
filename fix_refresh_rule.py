f=open(r'database.rules.json', encoding='utf-8')
c=f.read()
f.close()

old='"kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true },'
new='"kioskBackgroundEnabled": { ".read": true },\n          "kioskBackgroundUrl": { ".read": true },\n          "kioskRefreshAt": { ".read": true }'

assert c.count(old)==1
c=c.replace(old,new,1)
open(r'database.rules.json','w',encoding='utf-8').write(c)
print("OK")
