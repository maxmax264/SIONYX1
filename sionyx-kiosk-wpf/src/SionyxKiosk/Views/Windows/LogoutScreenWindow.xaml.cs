using System.Windows;

namespace SionyxKiosk.Views.Windows;

/// <summary>
/// Full-screen goodbye screen shown while logout cleanup runs in the
/// background. Purely presentational - the caller (App.xaml.cs) owns
/// how long it stays open and closes it explicitly once cleanup
/// finishes (or a minimum display time elapses, whichever is longer),
/// so people have real time to notice this before the screen changes.
/// </summary>
public partial class LogoutScreenWindow : Window
{
    public LogoutScreenWindow()
    {
        InitializeComponent();
    }
}
