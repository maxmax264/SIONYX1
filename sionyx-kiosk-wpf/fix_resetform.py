f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old = '    [RelayCommand]\n    private void ToggleMode()'
new = '    public void ResetForm()\n    {\n        Phone = "";\n        Password = "";\n        FirstName = "";\n        LastName = "";\n        Email = "";\n        ErrorMessage = "";\n        ForgotPasswordInfo = "";\n        IsLoginMode = true;\n    }\n\n    [RelayCommand]\n    private void ToggleMode()'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
