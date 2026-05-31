# Fix SessionService - remove organizations/orgId prefix (DbUpdateAsync adds it automatically)
content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()
old = '            await Firebase.DbUpdateAsync($"organizations/{Firebase.OrgId}/sessionLogs/{_userId}/{logKey}"'
new = '            await Firebase.DbUpdateAsync($"sessionLogs/{_userId}/{logKey}"'
count = content.count(old)
print(f"SessionService: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")

# Fix PrintMonitorService
content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()
old = '                    await Firebase.DbUpdateAsync($"organizations/{orgId}/printLogs/{_userId}/{logKey}"'
new = '                    await Firebase.DbUpdateAsync($"printLogs/{_userId}/{logKey}"'
count = content.count(old)
print(f"PrintMonitorService: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
