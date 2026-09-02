using System.Windows;

namespace SionyxKiosk.Views.Windows;

/// <summary>
/// Permanent branded background layer. Created once in App.OnStartup and
/// never closed for the lifetime of the process - see the XAML file for
/// why it exists.
/// </summary>
public partial class ShieldWindow : Window
{
    public ShieldWindow()
    {
        InitializeComponent();
    }
}
