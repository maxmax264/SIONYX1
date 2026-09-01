using CommunityToolkit.Mvvm.ComponentModel;
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
            StatusMessage = "יש למלא שם פרטי ושם משפחה";
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
                await ShowSuccessToastAsync("הפרטים עודכנו בהצלחה");
            }
            else
            {
                StatusMessage = result.Error ?? "שגיאה בעדכון הפרטים";
                IsSuccess = false;
            }
        }
        catch
        {
            StatusMessage = "שגיאה בעדכון הפרטים";
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
            StatusMessage = "יש למלא סיסמא חדשה ואישור";
            IsSuccess = false;
            return;
        }
        if (NewPassword != ConfirmPassword)
        {
            StatusMessage = "הסיסמאות אינן תואמות";
            IsSuccess = false;
            return;
        }
        if (NewPassword.Length < 4)
        {
            StatusMessage = "הסיסמא חייבת להכיל לפחות 4 תווים";
            IsSuccess = false;
            return;
        }

        IsBusy = true;
        StatusMessage = "";
        try
        {
            _forceLogout.Pause();
            var result = await _auth.ChangePasswordAsync(NewPassword);
            if (result.IsSuccess)
            {
                NewPassword = "";
                ConfirmPassword = "";
                await ShowSuccessToastAsync("הסיסמא שונתה בהצלחה ✓");
                await Task.Delay(3000);
                _forceLogout.Resume();
            }
            else
            {
                StatusMessage = result.Error ?? "שגיאה בשינוי הסיסמא";
                IsSuccess = false;
            }
        }
        catch
        {
            StatusMessage = "שגיאה בשינוי הסיסמא";
            IsSuccess = false;
        }
        finally
        {
            IsBusy = false;
        }
    }
}
