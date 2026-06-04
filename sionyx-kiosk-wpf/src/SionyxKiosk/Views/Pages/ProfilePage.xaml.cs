using System.Windows;
using System.Windows.Controls;
using SionyxKiosk.ViewModels;

namespace SionyxKiosk.Views.Pages;

public partial class ProfilePage : Page
{
    private ProfileViewModel _vm => (ProfileViewModel)DataContext;

    public ProfilePage(ProfileViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }

    private void NewPasswordBox_Changed(object sender, RoutedEventArgs e)
    {
        if (DataContext is ProfileViewModel vm)
            vm.NewPassword = ((PasswordBox)sender).Password;
    }

    private void ConfirmPasswordBox_Changed(object sender, RoutedEventArgs e)
    {
        if (DataContext is ProfileViewModel vm)
            vm.ConfirmPassword = ((PasswordBox)sender).Password;
    }
}
