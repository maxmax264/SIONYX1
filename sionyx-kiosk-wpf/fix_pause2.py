path = r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    'var result = await _auth.ChangePasswordAsync(NewPassword);\n            if (result.IsSuccess)\n            {\n                NewPassword = "";\n                ConfirmPassword = "";\n                await ShowSuccessToastAsync("\u05d4\u05e1\u05d9\u05e1\u05de\u05d0 \u05e9\u05d5\u05e0\u05ea\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4 \u2713");',
    '_forceLogout.Pause();\n            var result = await _auth.ChangePasswordAsync(NewPassword);\n            if (result.IsSuccess)\n            {\n                NewPassword = "";\n                ConfirmPassword = "";\n                await ShowSuccessToastAsync("\u05d4\u05e1\u05d9\u05e1\u05de\u05d0 \u05e9\u05d5\u05e0\u05ea\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4 \u2713");\n                await Task.Delay(3000);\n                _forceLogout.Resume();'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
