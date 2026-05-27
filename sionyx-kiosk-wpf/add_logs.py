import re

#  HomeViewModel - לוגים על session start/end 
path = r'.\src\SionyxKiosk\ViewModels\HomeViewModel.cs'
c = open(path, encoding='utf-8').read()

old = '''            if (result.IsSuccess)
            {
                IsSessionActive = true;
                SessionStartedSuccessfully?.Invoke();
            }
            else
                ErrorMessage = result.Error ?? "שגיאה";'''
new = '''            if (result.IsSuccess)
            {
                IsSessionActive = true;
                Log.Information("[SESSION] Session STARTED successfully for user={User} remainingTime={Time}",
                    _user.Username, _user.RemainingTime);
                SessionStartedSuccessfully?.Invoke();
            }
            else
            {
                Log.Warning("[SESSION] Session START failed: {Error}", result.Error);
                ErrorMessage = result.Error ?? "שגיאה";
            }'''
c = c.replace(old, new)

old = '''            await _session.EndSessionAsync("user");
            IsSessionActive = false;

            // Use the session's authoritative remaining time (synced to Firebase)
            // instead of _user.RemainingTime which may be stale from login
            _user.RemainingTime = Math.Max(0, _session.RemainingTime);
            UpdateStats();'''
new = '''            Log.Information("[SESSION] Ending session for user={User}", _user.Username);
            await _session.EndSessionAsync("user");
            IsSessionActive = false;

            _user.RemainingTime = Math.Max(0, _session.RemainingTime);
            Log.Information("[SESSION] Session ENDED - remainingTime={Time} printBalance={Balance}",
                _user.RemainingTime, _user.PrintBalance);
            UpdateStats();'''
c = c.replace(old, new)

# לוג על עדכון יתרה ב-UpdateStats
old = '''    private void OnPrintJobAllowed(string doc, int pages, double cost, double remaining)
    {
        Log.Debug("[HVM] OnPrintJobAllowed doc={Doc} pages={Pages} cost={Cost} remaining={Remaining}",
            doc, pages, cost, remaining);
        _user.PrintBalance = remaining;
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = remaining > 0 ? $"{remaining:F2} " : "-");
    }
    private void OnPrintBudgetUpdated(double balance)
    {
        Log.Debug("[HVM] OnPrintBudgetUpdated balance={Balance}", balance);
        _user.PrintBalance = balance;
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = balance > 0 ? $"{balance:F2} " : "-");
    }'''
new = '''    private void OnPrintJobAllowed(string doc, int pages, double cost, double remaining)
    {
        Log.Information("[PRINT] Job ALLOWED: doc='{Doc}' pages={Pages} cost={Cost} remaining={Remaining}",
            doc, pages, cost, remaining);
        _user.PrintBalance = remaining;
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = remaining > 0 ? $"{remaining:F2} " : "-");
    }
    private void OnPrintBudgetUpdated(double balance)
    {
        Log.Information("[PRINT] Budget updated: balance={Balance}", balance);
        _user.PrintBalance = balance;
        Application.Current?.Dispatcher.InvokeAsync(() => PrintBalance = balance > 0 ? $"{balance:F2} " : "-");
    }'''
c = c.replace(old, new)

open(path, 'w', encoding='utf-8').write(c)
print('HomeViewModel: OK')

#  MainWindow - לוג מפורט על כל ניווט 
path = r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs'
c = open(path, encoding='utf-8').read()

old = '''            Log.Debug("[NAV] NavigateTo={Page} prev={Prev}", page,
                _currentPage?.GetType().Name ?? "none");'''
new = '''            Log.Information("[NAV] NavigateTo={Page} prev={Prev} user={User} sessionActive={Session}",
                page,
                _currentPage?.GetType().Name ?? "none",
                (_currentPage?.DataContext as SionyxKiosk.ViewModels.HomeViewModel)?.ToString() ?? "-",
                SionyxKiosk.Services.SessionService.IsActiveStatic);'''
if '[NAV] NavigateTo={Page} prev={Prev}" page,' in c:
    c = c.replace(old, new)
    print('MainWindow NAV log: OK')
else:
    # simpler replacement
    old2 = 'Log.Debug("[NAV] NavigateTo={Page} prev={Prev}", page,'
    new2 = 'Log.Information("[NAV] NavigateTo={Page} prev={Prev}", page,'
    c = c.replace(old2, new2)
    print('MainWindow NAV log: upgraded to Information')

open(path, 'w', encoding='utf-8').write(c)
print('MainWindow: OK')

print('ALL DONE')
