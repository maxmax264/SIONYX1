using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Services;

namespace SionyxKiosk.ViewModels;

public partial class ProfileViewModel : ObservableObject
{
    private readonly AuthService _auth;

    [ObservableProperty] private string _firstName = "";
    [ObservableProperty] private string _lastName = "";
    [ObservableProperty] private string _phoneNumber = "";
    [ObservableProperty] private string _newPassword = "";
    [ObservableProperty] private string _confirmPassword = "";
    [ObservableProperty] private string _statusMessage = "";
    [ObservableProperty] private bool _isSuccess;
    [ObservableProperty] private bool _isBusy;

    public ProfileViewModel(AuthService auth)
    {
        _auth = auth;
        LoadUser();
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
                StatusMessage = "הפרטים עודכנו בהצלחה";
                IsSuccess = true;
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
            StatusMessage = "יש למלא סיסמה חדשה ואישור";
            IsSuccess = false;
            return;
        }
        if (NewPassword != ConfirmPassword)
        {
            StatusMessage = "הסיסמאות אינן תואמות";
            IsSuccess = false;
            return;
        }
        if (NewPassword.Length < 6)
        {
            StatusMessage = "הסיסמה חייבת להכיל לפחות 6 תווים";
            IsSuccess = false;
            return;
        }

        IsBusy = true;
        StatusMessage = "";
        try
        {
            var result = await _auth.ChangePasswordAsync(NewPassword);
            if (result.IsSuccess)
            {
                StatusMessage = "הסיסמה שונתה בהצלחה";
                IsSuccess = true;
                NewPassword = "";
                ConfirmPassword = "";
            }
            else
            {
                StatusMessage = result.Error ?? "שגיאה בשינוי הסיסמה";
                IsSuccess = false;
            }
        }
        catch
        {
            StatusMessage = "שגיאה בשינוי הסיסמה";
            IsSuccess = false;
        }
        finally
        {
            IsBusy = false;
        }
    }
}
