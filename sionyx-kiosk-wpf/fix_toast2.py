import re

path = r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs'
content = open(path, encoding='utf-8').read()

# הוסף ShowStatus property
content = content.replace(
    '[ObservableProperty] private bool _isBusy;',
    '[ObservableProperty] private bool _isBusy;\n    [ObservableProperty] private bool _showStatus;'
)

# הוסף ShowSuccessToast helper אחרי LoadUser
helper = '''
    private async Task ShowSuccessToastAsync(string message)
    {
        StatusMessage = message;
        IsSuccess = true;
        ShowStatus = true;
        await Task.Delay(2000);
        ShowStatus = false;
        StatusMessage = "";
    }
'''
content = content.replace(
    'private void LoadUser()',
    helper + '\n    private void LoadUser()'
)

# החלף את הגדרת ההצלחה ב-SaveDetails
content = content.replace(
    'StatusMessage = "\u05d4\u05e4\u05e8\u05d8\u05d9\u05dd \u05e2\u05d5\u05d3\u05db\u05e0\u05d5 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4";\n                IsSuccess = true;',
    'await ShowSuccessToastAsync("\u05d4\u05e4\u05e8\u05d8\u05d9\u05dd \u05e2\u05d5\u05d3\u05db\u05e0\u05d5 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4");'
)

# החלף את הגדרת ההצלחה ב-ChangePassword
content = content.replace(
    'StatusMessage = "\u05d4\u05e1\u05d9\u05e1\u05de\u05d0 \u05e9\u05d5\u05e0\u05ea\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4";\n                IsSuccess = true;',
    'await ShowSuccessToastAsync("\u05d4\u05e1\u05d9\u05e1\u05de\u05d0 \u05e9\u05d5\u05e0\u05ea\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4 \u2713");'
)

open(path, 'w', encoding='utf-8').write(content)
print('ViewModel OK')
