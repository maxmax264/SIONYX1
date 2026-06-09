using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Reflection;

namespace SionyxKiosk.Views.Dialogs;

public class AboutDialog : Window
{
    public AboutDialog(string orgName, string version)
    {
        Title = "אודות SIONYX";
        Width = 360;
        Height = 260;
        ResizeMode = ResizeMode.NoResize;
        WindowStartupLocation = WindowStartupLocation.CenterScreen;
        Topmost = true;
        FlowDirection = FlowDirection.RightToLeft;
        Background = new SolidColorBrush(Color.FromRgb(18, 18, 18));

        var stack = new StackPanel { Margin = new Thickness(30), HorizontalAlignment = HorizontalAlignment.Center };

        var title = new TextBlock
        {
            Text = "SIONYX",
            FontSize = 28,
            FontWeight = FontWeights.Bold,
            Foreground = Brushes.White,
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 0, 0, 8)
        };

        var org = new TextBlock
        {
            Text = orgName,
            FontSize = 14,
            Foreground = new SolidColorBrush(Color.FromRgb(180, 180, 180)),
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 0, 0, 4)
        };

        var ver = new TextBlock
        {
            Text = $"גרסה {version}",
            FontSize = 13,
            Foreground = new SolidColorBrush(Color.FromRgb(140, 140, 140)),
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 0, 0, 24)
        };

        var closeBtn = new Button
        {
            Content = "סגור",
            Width = 100,
            Height = 34,
            HorizontalAlignment = HorizontalAlignment.Center,
            Background = new SolidColorBrush(Color.FromRgb(40, 40, 40)),
            Foreground = Brushes.White,
            BorderBrush = new SolidColorBrush(Color.FromRgb(80, 80, 80)),
            Cursor = System.Windows.Input.Cursors.Hand
        };
        closeBtn.Click += (s, e) => Close();

        stack.Children.Add(title);
        stack.Children.Add(org);
        stack.Children.Add(ver);
        stack.Children.Add(closeBtn);
        Content = stack;
    }
}
