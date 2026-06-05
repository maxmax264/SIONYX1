path = r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs'
content = open(path, encoding='utf-8').read()
idx = content.find('ChangePasswordAsync')
# מצא את ה-ChangePassword השני (הפונקציה עצמה)
idx2 = content.find('ChangePasswordAsync', idx+1)
print(repr(content[idx2:idx2+600]))
