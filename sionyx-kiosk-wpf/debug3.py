path = r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs'
content = open(path, encoding='utf-8').read()
# הדפס את כל הקובץ עם repr כדי לראות בדיוק
start = content.find('ChangePasswordAsync(NewPassword)')
print(repr(content[start-5:start+400]))
