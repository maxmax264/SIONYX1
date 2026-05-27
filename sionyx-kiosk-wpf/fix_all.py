# ── fix_all.py ──────────────────────────────────────────────────

# ══ תיקון 1: MainWindow — לא לעשות Dispose ל-HomeViewModel ══
path = r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs'
c = open(path, encoding='utf-8').read()

old = '''using SionyxKiosk.ViewModels;
using SionyxKiosk.Views.Pages;
namespace SionyxKiosk.Views.Windows;'''
new = '''using Serilog;
using SionyxKiosk.ViewModels;
using SionyxKiosk.Views.Pages;
namespace SionyxKiosk.Views.Windows;'''
c = c.replace(old, new)

old = '''            // Dispose previous page's ViewModel if it implements IDisposable.
            // This prevents event subscription leaks on singleton services.
            if (_currentPage?.DataContext is IDisposable disposableVm)
                disposableVm.Dispose();'''
new = '''            // Dispose previous page's ViewModel if it implements IDisposable,
            // BUT skip HomeViewModel — it is a singleton and must stay alive.
            if (_currentPage?.DataContext is IDisposable disposableVm
                && _currentPage.DataContext is not HomeViewModel)
            {
                Log.Debug("[NAV] Disposing ViewModel {Type}", disposableVm.GetType().Name);
                disposableVm.Dispose();
            }

            Log.Debug("[NAV] NavigateTo={Page} prev={Prev}", page,
                _currentPage?.GetType().Name ?? "none");'''
c = c.replace(old, new)

old = '''            if (pageInstance is Page p)
            {
                _currentPage = p;
                // Set Content directly instead of Navigate() to avoid
                // WPF Frame journal accumulation (keeps all old pages in memory).
                ContentFrame.Content = p;
            }'''
new = '''            if (pageInstance is Page p)
            {
                _currentPage = p;
                Log.Debug("[NAV] Navigated to {Page} VM={VM}", page,
                    p.DataContext?.GetType().Name ?? "null");
                // Set Content directly instead of Navigate() to avoid
                // WPF Frame journal accumulation (keeps all old pages in memory).
                ContentFrame.Content = p;
            }'''
c = c.replace(old, new)

open(path, 'w', encoding='utf-8').write(c)
print('Fix1 MainWindow: OK')

# ══ תיקון 2: HomePage — ניתוק events ב-Unloaded ══
path = r'.\src\SionyxKiosk\Views\Pages\HomePage.xaml.cs'
c = open(path, encoding='utf-8').read()

old = '''using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using SionyxKiosk.ViewModels;
using SionyxKiosk.Views.Dialogs;
using SionyxKiosk.Views.Windows;

namespace SionyxKiosk.Views.Pages;

public partial class HomePage : Page
{
    private readonly HomeViewModel _vm;
    private readonly IServiceProvider _services;

    public HomePage(HomeViewModel viewModel, IServiceProvider services)
    {
        _vm = viewModel;
        _services = services;
        DataContext = viewModel;
        Resources["StringToVis"] = new Views.Controls.StringToVisibilityConverter();
        Resources["InverseBool"] = new InverseBoolConverter();
        Resources["InverseBoolToVis"] = new InverseBoolToVisibilityConverter();
        InitializeComponent();

        viewModel.PropertyChanged += (_, e) =>
        {
            if (e.PropertyName == nameof(HomeViewModel.UnreadMessages))
                UpdateMessageCard(viewModel.UnreadMessages);
            if (e.PropertyName == nameof(HomeViewModel.HasAnnouncements))
                UpdateAnnouncementsSection();
        };

        viewModel.ViewMessagesRequested += OpenMessageDialog;
        viewModel.NavigateToPackagesRequested += NavigateToPackages;
        viewModel.SessionStartedSuccessfully += OnSessionStarted;
        viewModel.ResumeSessionRequested += OnResumeSession;

        UpdateMessageCard(viewModel.UnreadMessages);
        UpdateAnnouncementsSection();
    }'''
new = '''using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using Serilog;
using SionyxKiosk.ViewModels;
using SionyxKiosk.Views.Dialogs;
using SionyxKiosk.Views.Windows;

namespace SionyxKiosk.Views.Pages;

public partial class HomePage : Page
{
    private readonly HomeViewModel _vm;
    private readonly IServiceProvider _services;
    private System.ComponentModel.PropertyChangedEventHandler? _propChangedHandler;

    public HomePage(HomeViewModel viewModel, IServiceProvider services)
    {
        _vm = viewModel;
        _services = services;
        DataContext = viewModel;
        Resources["StringToVis"] = new Views.Controls.StringToVisibilityConverter();
        Resources["InverseBool"] = new InverseBoolConverter();
        Resources["InverseBoolToVis"] = new InverseBoolToVisibilityConverter();
        InitializeComponent();

        _propChangedHandler = (_, e) =>
        {
            if (e.PropertyName == nameof(HomeViewModel.UnreadMessages))
                UpdateMessageCard(viewModel.UnreadMessages);
            if (e.PropertyName == nameof(HomeViewModel.HasAnnouncements))
                UpdateAnnouncementsSection();
        };
        viewModel.PropertyChanged += _propChangedHandler;

        viewModel.ViewMessagesRequested += OpenMessageDialog;
        viewModel.NavigateToPackagesRequested += NavigateToPackages;
        viewModel.SessionStartedSuccessfully += OnSessionStarted;
        viewModel.ResumeSessionRequested += OnResumeSession;

        Unloaded += OnPageUnloaded;

        UpdateMessageCard(viewModel.UnreadMessages);
        UpdateAnnouncementsSection();
    }

    private void OnPageUnloaded(object sender, RoutedEventArgs e)
    {
        Log.Debug("[HOME] HomePage.Unloaded — unsubscribing events from HomeViewModel");
        _vm.PropertyChanged -= _propChangedHandler;
        _vm.ViewMessagesRequested -= OpenMessageDialog;
        _vm.NavigateToPackagesRequested -= NavigateToPackages;
        _vm.SessionStartedSuccessfully -= OnSessionStarted;
        _vm.ResumeSessionRequested -= OnResumeSession;
    }'''
c = c.replace(old, new)
open(path, 'w', encoding='utf-8').write(c)
print('Fix2 HomePage: OK')

# ══ תיקון 3: HomeViewModel — עדכון _user.PrintBalance + לוגים ══
path = r'.\src\SionyxKiosk\ViewModels\HomeViewModel.cs'
c = open(path, encoding='utf-8').read()

old = '''using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Models;
using System.Windows;
using SionyxKiosk.Services;'''
new = '''using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Models;
using System.Windows;
using Serilog;
using SionyxKiosk.Services;'''
c = c.replace(old, new)

old = '''    private void OnPrintJobAllowed(string doc, int pages, double cost, double remaining)
    {
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = remaining > 0 ? $"{remaining:F2} ₪" : "—");
    }
    private void OnPrintBudgetUpdated(double balance)
    {
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = balance > 0 ? $"{balance:F2} ₪" : "—");
    }'''
new = '''    private void OnPrintJobAllowed(string doc, int pages, double cost, double remaining)
    {
        Log.Debug("[HVM] OnPrintJobAllowed doc={Doc} pages={Pages} cost={Cost} remaining={Remaining}",
            doc, pages, cost, remaining);
        _user.PrintBalance = remaining;
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = remaining > 0 ? $"{remaining:F2} ₪" : "—");
    }
    private void OnPrintBudgetUpdated(double balance)
    {
        Log.Debug("[HVM] OnPrintBudgetUpdated balance={Balance}", balance);
        _user.PrintBalance = balance;
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = balance > 0 ? $"{balance:F2} ₪" : "—");
    }'''
c = c.replace(old, new)

old = '''    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;'''
new = '''    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        Log.Warning("[HVM] HomeViewModel.Dispose() called — caller: {Caller}",
            new System.Diagnostics.StackTrace(1, false).ToString().Split('\\n')[0].Trim());'''
c = c.replace(old, new)

open(path, 'w', encoding='utf-8').write(c)
print('Fix3 HomeViewModel: OK')
