content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '            await Firebase.DbUpdateAsync($"organizations/{orgId}/sessionLogs/{_userId}/{logKey}"'
new = '            await Firebase.DbUpdateAsync($"sessionLogs/{_userId}/{logKey}"'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
