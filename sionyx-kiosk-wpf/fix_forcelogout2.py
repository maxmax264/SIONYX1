content = open(r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs', encoding='utf-8').read()
old = '''public partial class ProfileViewModel : ObservableObject
{
    private readonly AuthService _auth;'''
new = '''public partial class ProfileViewModel : ObservableObject
{
    private readonly AuthService _auth;
    private readonly ForceLogoutService _forceLogout;'''
content = content.replace(old, new)

old2 = '''    public ProfileViewModel(AuthService auth)
    {
        _auth = auth;
        LoadUser();
    }'''
new2 = '''    public ProfileViewModel(AuthService auth, ForceLogoutService forceLogout)
    {
        _auth = auth;
        _forceLogout = forceLogout;
        LoadUser();
    }'''
content = content.replace(old2, new2)

old3 = '''        IsBusy = true;
        StatusMessage = "";
        try
        {
            var result = await _auth.ChangePasswordAsync(NewPassword);'''
new3 = '''        IsBusy = true;
        StatusMessage = "";
        try
        {
            _forceLogout.StopListening();
            var result = await _auth.ChangePasswordAsync(NewPassword);'''
content = content.replace(old3, new3)

old4 = '''                StatusMessage = "הסיסמה שונתה בהצלחה";
                IsSuccess = true;
                NewPassword = "";
                ConfirmPassword = "";'''
new4 = '''                StatusMessage = "הסיסמה שונתה בהצלחה";
                IsSuccess = true;
                NewPassword = "";
                ConfirmPassword = "";
                var uid = _auth.CurrentUser?.Uid;
                if (uid != null) _forceLogout.StartListening(uid);'''
content = content.replace(old4, new4)

open(r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs', 'w', encoding='utf-8').write(content)
print('OK')
