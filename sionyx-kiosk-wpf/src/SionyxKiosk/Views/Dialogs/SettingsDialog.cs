using System.Windows;
using System.Windows.Controls;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Views.Dialogs;

public partial class SettingsDialog : Window
{
    public SettingsDialog()
    {
        Title = "הגדרות";
        Width = 380;
        Height = 380;
        WindowStartupLocation = WindowStartupLocation.CenterScreen;
        ResizeMode = ResizeMode.NoResize;
        FlowDirection = FlowDirection.RightToLeft;

        var grid = new Grid { Margin = new Thickness(20) };
        for (int i = 0; i < 9; i++)
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

        // ── Password section ──────────────────────────────────────
        var title = new TextBlock
        {
            Text = "שינוי סיסמת יציאה (למנהל בלבד)",
            FontSize = 14,
            FontWeight = FontWeights.Bold,
            Margin = new Thickness(0, 0, 0, 16)
        };
        Grid.SetRow(title, 0);

        var lblCurrent = new TextBlock { Text = "סיסמה נוכחית:", Margin = new Thickness(0, 0, 0, 4) };
        Grid.SetRow(lblCurrent, 1);

        var txtCurrent = new PasswordBox { Margin = new Thickness(0, 0, 0, 12) };
        Grid.SetRow(txtCurrent, 2);

        var lblNew = new TextBlock { Text = "סיסמה חדשה:", Margin = new Thickness(0, 0, 0, 4) };
        Grid.SetRow(lblNew, 3);

        var txtNew = new PasswordBox { Margin = new Thickness(0, 0, 0, 16) };
        Grid.SetRow(txtNew, 4);

        // ── Update frequency section ──────────────────────────────
        var lblUpdate = new TextBlock
        {
            Text = "תדירות בדיקת עדכונים:",
            Margin = new Thickness(0, 0, 0, 4)
        };
        Grid.SetRow(lblUpdate, 5);

        var cmbUpdate = new ComboBox { Margin = new Thickness(0, 0, 0, 16) };
        cmbUpdate.Items.Add(new ComboBoxItem { Content = "ללא", Tag = "0" });
        cmbUpdate.Items.Add(new ComboBoxItem { Content = "כל דקה", Tag = "1" });
        cmbUpdate.Items.Add(new ComboBoxItem { Content = "כל 10 דקות", Tag = "10" });
        cmbUpdate.Items.Add(new ComboBoxItem { Content = "כל שעה", Tag = "60" });
        cmbUpdate.Items.Add(new ComboBoxItem { Content = "כל יום", Tag = "1440" });

        // Load saved value
        var savedInterval = RegistryConfig.ReadValueCurrentUser("UpdateCheckIntervalMinutes") ?? "0";
        foreach (ComboBoxItem item in cmbUpdate.Items)
        {
            if (item.Tag?.ToString() == savedInterval)
            {
                cmbUpdate.SelectedItem = item;
                break;
            }
        }
        if (cmbUpdate.SelectedItem == null) cmbUpdate.SelectedIndex = 0;
        Grid.SetRow(cmbUpdate, 6);

        // ── Buttons ───────────────────────────────────────────────
        var btnPanel = new StackPanel
        {
            Orientation = Orientation.Horizontal,
            HorizontalAlignment = HorizontalAlignment.Left
        };
        var btnSave = new Button { Content = "שמור", Width = 80, Margin = new Thickness(0, 0, 8, 0), Padding = new Thickness(8, 4, 8, 4) };
        var btnCancel = new Button { Content = "בטל", Width = 80, Padding = new Thickness(8, 4, 8, 4) };
        btnPanel.Children.Add(btnSave);
        btnPanel.Children.Add(btnCancel);
        Grid.SetRow(btnPanel, 8);

        grid.Children.Add(title);
        grid.Children.Add(lblCurrent);
        grid.Children.Add(txtCurrent);
        grid.Children.Add(lblNew);
        grid.Children.Add(txtNew);
        grid.Children.Add(lblUpdate);
        grid.Children.Add(cmbUpdate);
        grid.Children.Add(btnPanel);

        Content = grid;

        btnCancel.Click += (s, e) => Close();
        btnSave.Click += (s, e) =>
        {
            var current = txtCurrent.Password;
            var newPass = txtNew.Password;

            // Save update interval (even if password fields are empty)
            if (cmbUpdate.SelectedItem is ComboBoxItem selected)
            {
                var interval = selected.Tag?.ToString() ?? "0";
                RegistryConfig.WriteValue("UpdateCheckIntervalMinutes", interval);
                Services.AutoUpdateService.ApplyIntervalFromRegistry();
            }

            // Password change is optional — only validate if user typed something
            if (!string.IsNullOrEmpty(current) || !string.IsNullOrEmpty(newPass))
            {
                var expected = AppConstants.GetAdminExitPassword();
                if (current != expected)
                {
                    MessageBox.Show("סיסמה נוכחית שגויה", "שגיאה", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                if (newPass.Length < 4)
                {
                    MessageBox.Show("סיסמה חייבת להכיל לפחות 4 תווים", "שגיאה", MessageBoxButton.OK, MessageBoxImage.Warning);
                    return;
                }

                var ok = RegistryConfig.WriteValue("AdminExitPassword", newPass);
                if (!ok)
                {
                    MessageBox.Show("שגיאה בשמירה — נסה כאדמין", "שגיאה", MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }
            }

            MessageBox.Show("הגדרות נשמרו בהצלחה!", "הגדרות", MessageBoxButton.OK, MessageBoxImage.Information);
            Close();
        };
    }
}
