path = r'.\src\SionyxKiosk\ViewModels\ProfileViewModel.cs'
new_content = """using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Services;

namespace SionyxKiosk.ViewModels;

public partial class ProfileViewModel : ObservableObject
{
    private readonly AuthService _auth;
    private readonly ForceLogoutService _forceLogout;

    [ObservableProperty] private string _firstName = "";
    [ObservableProperty] private string _lastName = "";
    [ObservableProperty] private string _phoneNumber = "";
    [ObservableProperty] private string _newPassword = "";
    [ObservableProperty] private string _confirmPassword = "";
    [ObservableProperty] private string _statusMessage = "";
    [ObservableProperty] private bool _isSuccess;
    [ObservableProperty] private bool _isBusy;
    [ObservableProperty] private bool _showStatus;

    public ProfileViewModel(AuthService auth, ForceLogoutService forceLogout)
    {
        _auth = auth;
        _forceLogout = forceLogout;
        LoadUser();
    }

    private async Task ShowSuccessToastAsync(string message)
    {
        StatusMessage = message;
        IsSuccess = true;
        ShowStatus = true;
        await Task.Delay(2000);
        ShowStatus = false;
        StatusMessage = "";
    }

    private void LoadUser()
    {
        var user = _auth.CurrentUser;
        if (user == null) return;
        FirstName = user.FirstName ?? "";
        LastName = user.LastName ?? "";
        PhoneNumber = user.PhoneNumber ?? "";
    }

    [RelayCommand]
    private async Task SaveDetailsAsync()
    {
        if (string.IsNullOrWhiteSpace(FirstName) || string.IsNullOrWhiteSpace(LastName))
        {
            StatusMessage = "\u05d9\u05e9 \u05dc\u05de\u05dc\u05d0 \u05e9\u05dd \u05e4\u05e8\u05d8\u05d9 \u05d5\u05e9\u05dd \u05de\u05e9\u05e4\u05d7\u05d4";
            IsSuccess = false;
            return;
        }

        IsBusy = true;
        StatusMessage = "";
        try
        {
            var updates = new Dictionary<string, object>
            {
                ["firstName"] = FirstName,
                ["lastName"] = LastName
            };
            var result = await _auth.UpdateUserDataAsync(updates);
            if (result.IsSuccess)
            {
                await ShowSuccessToastAsync("\u05d4\u05e4\u05e8\u05d8\u05d9\u05dd \u05e2\u05d5\u05d3\u05db\u05e0\u05d5 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4");
            }
            else
            {
                StatusMessage = result.Error ?? "\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05e2\u05d3\u05db\u05d5\u05df \u05d4\u05e4\u05e8\u05d8\u05d9\u05dd";
                IsSuccess = false;
            }
        }
        catch
        {
            StatusMessage = "\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05e2\u05d3\u05db\u05d5\u05df \u05d4\u05e4\u05e8\u05d8\u05d9\u05dd";
            IsSuccess = false;
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task ChangePasswordAsync()
    {
        if (string.IsNullOrWhiteSpace(NewPassword) || string.IsNullOrWhiteSpace(ConfirmPassword))
        {
            StatusMessage = "\u05d9\u05e9 \u05dc\u05de\u05dc\u05d0 \u05e1\u05d9\u05e1\u05de\u05d0 \u05d7\u05d3\u05e9\u05d4 \u05d5\u05d0\u05d9\u05e9\u05d5\u05e8";
            IsSuccess = false;
            return;
        }
        if (NewPassword != ConfirmPassword)
        {
            StatusMessage = "\u05d4\u05e1\u05d9\u05e1\u05de\u05d0\u05d5\u05ea \u05d0\u05d9\u05e0\u05df \u05ea\u05d5\u05d0\u05de\u05d5\u05ea";
            IsSuccess = false;
            return;
        }
        if (NewPassword.Length < 6)
        {
            StatusMessage = "\u05d4\u05e1\u05d9\u05e1\u05de\u05d0 \u05d7\u05d9\u05d9\u05d1\u05ea \u05dc\u05d4\u05db\u05d9\u05dc \u05dc\u05e4\u05d7\u05d5\u05ea 6 \u05ea\u05d5\u05d5\u05d9\u05dd";
            IsSuccess = false;
            return;
        }

        IsBusy = true;
        StatusMessage = "";
        try
        {
            _forceLogout.StopListening();
            var result = await _auth.ChangePasswordAsync(NewPassword);
            if (result.IsSuccess)
            {
                NewPassword = "";
                ConfirmPassword = "";
                await ShowSuccessToastAsync("\u05d4\u05e1\u05d9\u05e1\u05de\u05d0 \u05e9\u05d5\u05e0\u05ea\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4 \u2713");
                var uid = _auth.CurrentUser?.Uid;
                if (uid != null) { await Task.Delay(2000); _forceLogout.StartListening(uid); }
            }
            else
            {
                StatusMessage = result.Error ?? "\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05e9\u05d9\u05e0\u05d5\u05d9 \u05d4\u05e1\u05d9\u05e1\u05de\u05d0";
                IsSuccess = false;
            }
        }
        catch
        {
            StatusMessage = "\u05e9\u05d2\u05d9\u05d0\u05d4 \u05d1\u05e9\u05d9\u05e0\u05d5\u05d9 \u05d4\u05e1\u05d9\u05e1\u05de\u05d0";
            IsSuccess = false;
        }
        finally
        {
            IsBusy = false;
        }
    }
}
"""
open(path, 'w', encoding='utf-8').write(new_content)
print('OK')
