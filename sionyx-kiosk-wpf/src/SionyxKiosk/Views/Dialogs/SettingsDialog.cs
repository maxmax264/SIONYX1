using System.Windows;
using System.Windows.Controls;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Views.Dialogs;

public partial class SettingsDialog : Window
{
    public SettingsDialog()
    {
        Title = "הגדרות";
        Width = 360;
        Height = 260;
        WindowStartupLocation = WindowStartupLocation.CenterScreen;
        ResizeMode = ResizeMode.NoResize;
        FlowDirection = FlowDirection.RightToLeft;

        var grid = new Grid { Margin = new Thickness(20) };
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

        var title = new TextBlock { Text = "שינוי סיסמא יציאה (ללא אינטרנט)", FontSize = 14, FontWeight = FontWeights.Bold, Margin = new Thickness(0,0,0,16) };
        Grid.SetRow(title, 0);

        var lblCurrent = new TextBlock { Text = "סיסמא נוכחית:", Margin = new Thickness(0,0,0,4) };
        Grid.SetRow(lblCurrent, 1);

        var txtCurrent = new PasswordBox { Margin = new Thickness(0,0,0,12) };
        Grid.SetRow(txtCurrent, 2);

        var lblNew = new TextBlock { Text = "סיסמא חדשה:", Margin = new Thickness(0,0,0,4) };
        Grid.SetRow(lblNew, 3);

        var txtNew = new PasswordBox { Margin = new Thickness(0,0,0,12) };
        Grid.SetRow(txtNew, 4);

        var btnPanel = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Left };
        var btnSave = new Button { Content = "שמור", Width = 80, Margin = new Thickness(0,0,8,0), Padding = new Thickness(8,4,8,4) };
        var btnCancel = new Button { Content = "בטל", Width = 80, Padding = new Thickness(8,4,8,4) };
        btnPanel.Children.Add(btnSave);
        btnPanel.Children.Add(btnCancel);

        var rowBtn = new RowDefinition { Height = GridLength.Auto };
        grid.RowDefinitions.Add(rowBtn);
        Grid.SetRow(btnPanel, 5);

        grid.Children.Add(title);
        grid.Children.Add(lblCurrent);
        grid.Children.Add(txtCurrent);
        grid.Children.Add(lblNew);
        grid.Children.Add(txtNew);
        grid.Children.Add(btnPanel);

        Content = grid;

        btnCancel.Click += (s, e) => Close();
        btnSave.Click += (s, e) =>
        {
            var current = txtCurrent.Password;
            var newPass = txtNew.Password;

            var expected = AppConstants.GetAdminExitPassword();
            if (current != expected)
            {
                MessageBox.Show("סיסמא נוכחית שגויה", "שגיאה", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (newPass.Length < 4)
            {
                MessageBox.Show("סיסמא חייבת להכיל לפחות 4 תווים", "שגיאה", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            var ok = RegistryConfig.WriteValue("AdminExitPassword", newPass);
            if (ok)
            {
                MessageBox.Show("סיסמא עודכנה בהצלחה!", "הגדרות", MessageBoxButton.OK, MessageBoxImage.Information);
                Close();
            }
            else
                MessageBox.Show("שגיאה בשמירה ? הרץ כמנהל", "שגיאה", MessageBoxButton.OK, MessageBoxImage.Error);
        };
    }
}
