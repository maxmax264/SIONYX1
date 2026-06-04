content = open(r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs', encoding='utf-8').read()
old = '            var result = await _auth.Firebase.ChangePasswordAsync(NewPassword);'
new = '            var result = await _auth.ChangePasswordAsync(NewPassword);'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
