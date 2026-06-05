content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
old = '        if (!result.Success)\n            return Error(result.Error ?? '
new = '        if (!result.IsSuccess)\n            return Error(result.Error ?? '
content = content.replace(old, new)

old2 = 'Firebase.ChangePasswordAsync(newPassword);\n        if (!result.IsSuccess)'
new2 = 'Firebase.ChangePasswordAsync(newPassword);\n        if (!result.IsSuccess)'
# just add token save after Success()
old3 = 'Firebase.ChangePasswordAsync(newPassword);\n        if (!result.Success)\n            return Error(result.Error'
idx = content.find('public async Task<ServiceResult> ChangePasswordAsync')
snippet = content[idx:idx+300]
print(repr(snippet))
