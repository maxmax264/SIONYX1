path = r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs'
content = open(path, encoding='utf-8').read()

old = '            if (result.IsSuccess)\n            {\n                StatusMessage = "\u05d4\u05e1\u05d9\u05e1\u05de\u05d0 \u05e9\u05d5\u05e0\u05ea\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4";\n                IsSuccess = true;\n                NewPassword = "";\n                ConfirmPassword = "";\n                var uid = _auth.CurrentUser?.Uid;\n                if (uid != null) { await Task.Delay(2000); _forceLogout.StartListening(uid); }\n            }'

new = '            if (result.IsSuccess)\n            {\n                NewPassword = "";\n                ConfirmPassword = "";\n                await ShowSuccessToastAsync("\u05d4\u05e1\u05d9\u05e1\u05de\u05d0 \u05e9\u05d5\u05e0\u05ea\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4 \u2713");\n                var uid = _auth.CurrentUser?.Uid;\n                if (uid != null) { await Task.Delay(2000); _forceLogout.StartListening(uid); }\n            }'

if old in content:
    content = content.replace(old, new)
    open(path, 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
