content = open(r'.\src\SionyxKiosk\Infrastructure\IFirebaseClient.cs', encoding='utf-8').read()
old = '    Task<FirebaseResult> DbDeleteAsync(string path);'
new = '    Task<FirebaseResult> ChangePasswordAsync(string newPassword);\n    Task<FirebaseResult> DbDeleteAsync(string path);'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Infrastructure\IFirebaseClient.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
