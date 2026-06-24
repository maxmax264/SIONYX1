using System.Collections.Generic;
using System.Diagnostics;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Win32;

namespace SionyxKiosk.Views.Dialogs;

public partial class StartupSettingsDialog : Window
{
    private const string RunKey = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Run";
    private const string RunValueName = "SIONYX";
    private const string SionyxStartupKey = @"SOFTWARE\SIONYX\Startup";

    public StartupSettingsDialog()
    {
        Title = "\u05d4\u05d2\u05d3\u05e8\u05d5\u05ea \u05d4\u05e4\u05e2\u05dc\u05d4 \u05d0\u05d5\u05d8\u05d5\u05de\u05d8\u05d9\u05ea";
        Width = 400;
        Height = 420;
        WindowStartupLocation = WindowStartupLocation.CenterScreen;
        ResizeMode = ResizeMode.NoResize;
        FlowDirection = FlowDirection.RightToLeft;
        Topmost = true;

        var grid = new Grid { Margin = new Thickness(20) };
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
        grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
        grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

        var title = new TextBlock
        {
            Text = "\u05d1\u05d7\u05e8 \u05d0\u05d9\u05d6\u05d4 \u05d9\u05d5\u05d6\u05e8\u05d9\u05dd \u05d4\u05e7\u05d9\u05d5\u05e1\u05e7 \u05d9\u05e2\u05dc\u05d4 \u05d0\u05d9\u05ea\u05dd \u05d1\u05d4\u05e4\u05e2\u05dc\u05d4:",
            FontSize = 13,
            FontWeight = FontWeights.Bold,
            Margin = new Thickness(0, 0, 0, 8),
            TextWrapping = TextWrapping.Wrap
        };
        Grid.SetRow(title, 0);

        var subtitle = new TextBlock
        {
            Text = "\u05d1\u05e8\u05d9\u05e8\u05ea \u05de\u05d7\u05d3\u05dc: \u05db\u05dc \u05d4\u05d9\u05d5\u05d6\u05e8\u05d9\u05dd \u05de\u05e1\u05d5\u05de\u05e0\u05d9\u05dd",
            FontSize = 11,
            Foreground = System.Windows.Media.Brushes.Gray,
            Margin = new Thickness(0, 0, 0, 12)
        };
        Grid.SetRow(subtitle, 1);

        var listBox = new ListBox { Margin = new Thickness(0, 0, 0, 12) };
        Grid.SetRow(listBox, 2);

        var users = GetLocalUsers();
        var checkBoxes = new List<(string username, CheckBox cb)>();

        foreach (var user in users)
        {
            bool isEnabled = IsStartupEnabledForUser(user);
            var cb = new CheckBox
            {
                Content = user + (user == Environment.UserName ? " (\u05e0\u05d5\u05db\u05d7\u05d9)" : ""),
                IsChecked = isEnabled,
                Margin = new Thickness(4, 4, 4, 4),
                FontSize = 13
            };
            checkBoxes.Add((user, cb));
            listBox.Items.Add(cb);
        }

        var btnPanel = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Left };
        var btnSave = new Button { Content = "\u05e9\u05de\u05d5\u05e8", Width = 80, Margin = new Thickness(0, 0, 8, 0), Padding = new Thickness(8, 4, 8, 4) };
        var btnCancel = new Button { Content = "\u05d1\u05d8\u05dc", Width = 80, Padding = new Thickness(8, 4, 8, 4) };
        btnPanel.Children.Add(btnSave);
        btnPanel.Children.Add(btnCancel);
        Grid.SetRow(btnPanel, 3);

        grid.Children.Add(title);
        grid.Children.Add(subtitle);
        grid.Children.Add(listBox);
        grid.Children.Add(btnPanel);
        Content = grid;

        btnCancel.Click += (s, e) => Close();
        btnSave.Click += (s, e) =>
        {
            string? autoLoginUser = null;
            foreach (var (username, cb) in checkBoxes)
            {
                if (cb.IsChecked == true) { autoLoginUser = username; break; }
            }
            SetAutoLogin(autoLoginUser ?? string.Empty);
            MessageBox.Show("\u05d4\u05d4\u05d2\u05d3\u05e8\u05d5\u05ea \u05e0\u05e9\u05de\u05e8\u05d5!", "\u05d4\u05d2\u05d3\u05e8\u05d5\u05ea", MessageBoxButton.OK, MessageBoxImage.Information);
            Close();
        };
    }

    private static List<string> GetLocalUsers()
    {
        var users = new List<string>();
        try
        {
            var psi = new ProcessStartInfo("net", "user")
            {
                UseShellExecute = false,
                RedirectStandardOutput = true,
                CreateNoWindow = true
            };
            using var proc = Process.Start(psi);
            var output = proc?.StandardOutput.ReadToEnd() ?? "";
            proc?.WaitForExit(5000);

            bool inUsers = false;
            foreach (var line in output.Split('\n'))
            {
                if (line.Contains("---")) { inUsers = true; continue; }
                if (!inUsers) continue;
                if (line.Contains("command completed")) break;
                foreach (var part in line.Split(' ', System.StringSplitOptions.RemoveEmptyEntries))
                {
                    if (!string.IsNullOrWhiteSpace(part))
                        users.Add(part.Trim());
                }
            }
        }
        catch { }

        // Filter out system accounts
        users.RemoveAll(u => u.Equals("Administrator", System.StringComparison.OrdinalIgnoreCase)
            || u.Equals("Guest", System.StringComparison.OrdinalIgnoreCase)
            || u.Equals("DefaultAccount", System.StringComparison.OrdinalIgnoreCase)
            || u.Equals("WDAGUtilityAccount", System.StringComparison.OrdinalIgnoreCase));

        if (users.Count == 0)
            users.Add(Environment.UserName);

        return users;
    }

    private static void SetAutoLogin(string username)
    {
        try
        {
            using var baseKey = Microsoft.Win32.RegistryKey.OpenBaseKey(Microsoft.Win32.RegistryHive.LocalMachine, Microsoft.Win32.RegistryView.Registry64);
            using var winlogon = baseKey.OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true);
            using var runKey = baseKey.OpenSubKey(RunKey, true);
            if (winlogon == null) return;

            string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location.Replace(".dll", ".exe");

            if (!string.IsNullOrEmpty(username))
            {
                winlogon.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                winlogon.SetValue("DefaultUserName", username, RegistryValueKind.String);
                winlogon.DeleteValue("DefaultPassword", false);
                runKey?.SetValue(RunValueName, $"\"{exePath}\" --kiosk", RegistryValueKind.String);
            }
            else
            {
                winlogon.SetValue("AutoAdminLogon", "0", RegistryValueKind.String);
                runKey?.DeleteValue(RunValueName, false);
            }
        }
        catch { }
    }

    private static bool IsStartupEnabledForUser(string username)
    {
        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(SionyxStartupKey);
            if (key == null) return true; // default: enabled
            var val = key.GetValue(username);
            if (val == null) return true; // default: enabled
            return (int)val == 1;
        }
        catch { return true; }
    }

    private static void SetStartupForUser(string username, bool enabled)
    {
        try
        {
            // Save preference
            using var prefKey = Registry.LocalMachine.CreateSubKey(SionyxStartupKey, writable: true);
            prefKey?.SetValue(username, enabled ? 1 : 0, RegistryValueKind.DWord);

            // Configure AutoAdminLogon in Winlogon
            using (var baseKey = Microsoft.Win32.RegistryKey.OpenBaseKey(Microsoft.Win32.RegistryHive.LocalMachine, Microsoft.Win32.RegistryView.Registry64))
            using (var winlogon = baseKey.OpenSubKey(@"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon", true))
            {
                if (winlogon != null)
                {
                    if (enabled)
                    {
                        winlogon.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                        winlogon.SetValue("DefaultUserName", username, RegistryValueKind.String);
                        winlogon.DeleteValue("DefaultPassword", false);
                    }
                    else
                    {
                        winlogon.SetValue("AutoAdminLogon", "0", RegistryValueKind.String);
                    }
                }
            }

            // Apply Run key to HKLM so it works for any user
            string exePath = System.Reflection.Assembly.GetExecutingAssembly().Location
                .Replace(".dll", ".exe");
            using var runKey = Registry.LocalMachine.OpenSubKey(RunKey, true);
            if (enabled)
                runKey?.SetValue(RunValueName, $"\"{exePath}\" --kiosk", RegistryValueKind.String);
            else
                runKey?.DeleteValue(RunValueName, false);
        }
        catch { }
    }
}
