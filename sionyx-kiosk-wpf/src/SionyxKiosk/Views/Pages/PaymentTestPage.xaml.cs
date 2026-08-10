using System.Windows.Controls;
using SionyxKiosk.ViewModels;
using SionyxKiosk.Views.Windows;

namespace SionyxKiosk.Views.Pages;

public partial class PaymentTestPage : Page
{
    public PaymentTestPage(PaymentTestViewModel viewModel)
    {
        DataContext = viewModel;
        Resources["InverseBool"] = new InverseBoolConverter();
        InitializeComponent();
    }
}
