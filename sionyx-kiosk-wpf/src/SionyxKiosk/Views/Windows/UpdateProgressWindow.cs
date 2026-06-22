using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Shapes;

namespace SionyxKiosk.Views.Windows;

public class UpdateProgressWindow : Window
{
    private readonly TextBlock _statusText;
    private readonly TextBlock _percentText;
    private readonly Rectangle _progressBar;
    private readonly TextBlock _versionText;
    private Grid? _progressContainer;

    public UpdateProgressWindow()
    {
        WindowStyle = WindowStyle.None;
        ResizeMode = ResizeMode.NoResize;
        WindowState = WindowState.Maximized;
        Topmost = true;
        AllowsTransparency = false;
        Background = new SolidColorBrush(Color.FromRgb(15, 15, 25));
        FlowDirection = FlowDirection.RightToLeft;

        var root = new Grid();

        var center = new StackPanel
        {
            VerticalAlignment = VerticalAlignment.Center,
            HorizontalAlignment = HorizontalAlignment.Center,
            Width = 480
        };

        // Logo
        var logo = new TextBlock
        {
            Text = "SIONYX",
            FontSize = 52,
            FontWeight = FontWeights.ExtraBold,
            Foreground = Brushes.White,
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 0, 0, 8)
        };

        // Version
        _versionText = new TextBlock
        {
            Text = "",
            FontSize = 15,
            Foreground = new SolidColorBrush(Color.FromArgb(180, 255, 255, 255)),
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 0, 0, 48)
        };

        // Status text
        _statusText = new TextBlock
        {
            Text = "המערכת בעדכון, אנא המתן...",
            FontSize = 22,
            FontWeight = FontWeights.SemiBold,
            Foreground = Brushes.White,
            HorizontalAlignment = HorizontalAlignment.Center,
            TextAlignment = TextAlignment.Center,
            Margin = new Thickness(0, 0, 0, 32)
        };

        // Progress bar container
        _progressContainer = new Grid
        {
            Height = 10,
            Margin = new Thickness(0, 0, 0, 16)
        };

        var progressBg = new Rectangle
        {
            Fill = new SolidColorBrush(Color.FromArgb(60, 255, 255, 255)),
            RadiusX = 5,
            RadiusY = 5
        };

        _progressBar = new Rectangle
        {
            Fill = new LinearGradientBrush(
                Color.FromRgb(99, 102, 241),
                Color.FromRgb(139, 92, 246), 0),
            RadiusX = 5,
            RadiusY = 5,
            HorizontalAlignment = HorizontalAlignment.Left,
            Width = 0
        };

        _progressContainer.Children.Add(progressBg);
        _progressContainer.Children.Add(_progressBar);

        // Percent text
        _percentText = new TextBlock
        {
            Text = "0%",
            FontSize = 16,
            Foreground = new SolidColorBrush(Color.FromArgb(200, 255, 255, 255)),
            HorizontalAlignment = HorizontalAlignment.Center,
            Margin = new Thickness(0, 0, 0, 0)
        };

        center.Children.Add(logo);
        center.Children.Add(_versionText);
        center.Children.Add(_statusText);
        center.Children.Add(_progressContainer);
        center.Children.Add(_percentText);

        root.Children.Add(center);
        Content = root;

        Loaded += (_, _) => AnimateIn();
    }

    private void AnimateIn()
    {
        Opacity = 0;
        var anim = new DoubleAnimation(0, 1, TimeSpan.FromMilliseconds(400));
        BeginAnimation(OpacityProperty, anim);
    }

    public void SetVersion(string version)
    {
        Dispatcher.Invoke(() => _versionText.Text = $"גרסה {version}");
    }

    public void SetProgress(int percent, string status)
    {
        Dispatcher.Invoke(() =>
        {
            _percentText.Text = $"{percent}%";
            _statusText.Text = status;

            if (_progressContainer != null)
            {
                var targetWidth = (_progressContainer.ActualWidth > 0 ? _progressContainer.ActualWidth : 480) * percent / 100.0;
                var anim = new DoubleAnimation(_progressBar.Width, targetWidth, TimeSpan.FromMilliseconds(300));
                _progressBar.BeginAnimation(FrameworkElement.WidthProperty, anim);
            }
        });
    }

    public void SetComplete()
    {
        Dispatcher.Invoke(() =>
        {
            _statusText.Text = "המערכת עודכנה בהצלחה!";
            _statusText.Foreground = new SolidColorBrush(Color.FromRgb(52, 211, 153));
            _percentText.Text = "100%";
            if (_progressContainer != null)
            {
                var targetWidth = _progressContainer.ActualWidth > 0 ? _progressContainer.ActualWidth : 480;
                var anim = new DoubleAnimation(_progressBar.Width, targetWidth, TimeSpan.FromMilliseconds(300));
                _progressBar.BeginAnimation(FrameworkElement.WidthProperty, anim);
            }
        });
    }

    public void AllowClose() { }

    protected override void OnClosing(System.ComponentModel.CancelEventArgs e)
    {
        // Always allow close
        base.OnClosing(e);
    }
}
