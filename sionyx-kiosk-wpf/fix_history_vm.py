content = open(r'.\src\SionyxKiosk\ViewModels\HistoryViewModel.cs', encoding='utf-8').read()

old1 = """using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Windows.Data;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Models;
using SionyxKiosk.Services;"""

new1 = """using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Text.Json;
using System.Windows.Data;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Models;
using SionyxKiosk.Services;"""

c1 = content.count(old1)
print(f"Step 1: {c1}")
if c1 == 1:
    content = content.replace(old1, new1, 1)
    print("Step 1: OK")
else:
    print("Step 1: NOT FOUND"); exit()

old2 = "public partial class HistoryViewModel : ObservableObject\n{"
new2 = "public partial class HistoryViewModel : ObservableObject, IDisposable\n{\n    private readonly FirebaseClient? _firebase;\n    private SseListener? _sessionListener;\n    private SseListener? _printListener;"

c2 = content.count(old2)
print(f"Step 2: {c2}")
if c2 == 1:
    content = content.replace(old2, new2, 1)
    print("Step 2: OK")
else:
    print("Step 2: NOT FOUND"); exit()

old3 = "    [ObservableProperty] private bool _sortNewestFirst = true;"
new3 = """    [ObservableProperty] private bool _sortNewestFirst = true;
    public ObservableCollection<SessionLogItem> SessionLogs { get; } = new();
    public ObservableCollection<PrintLogItem> PrintLogs { get; } = new();
    [ObservableProperty] private int _totalSessionMinutes;
    [ObservableProperty] private int _totalPrintPages;
    [ObservableProperty] private double _totalPrintCost;"""

c3 = content.count(old3)
print(f"Step 3: {c3}")
if c3 == 1:
    content = content.replace(old3, new3, 1)
    print("Step 3: OK")
else:
    print("Step 3: NOT FOUND"); exit()

old4 = "    public HistoryViewModel(PurchaseService purchaseService, string userId)"
new4 = "    public HistoryViewModel(PurchaseService purchaseService, string userId, FirebaseClient? firebase = null)"

c4 = content.count(old4)
print(f"Step 4: {c4}")
if c4 == 1:
    content = content.replace(old4, new4, 1)
    print("Step 4: OK")
else:
    print("Step 4: NOT FOUND"); exit()

old5 = """        FilteredPurchases = CollectionViewSource.GetDefaultView(_allPurchases);
        FilteredPurchases.Filter = ApplyFilter;
        FilteredPurchases.SortDescriptions.Add(
            new SortDescription(nameof(Purchase.CreatedAt), ListSortDirection.Descending));
    }"""

new5 = """        FilteredPurchases = CollectionViewSource.GetDefaultView(_allPurchases);
        FilteredPurchases.Filter = ApplyFilter;
        FilteredPurchases.SortDescriptions.Add(
            new SortDescription(nameof(Purchase.CreatedAt), ListSortDirection.Descending));
        _firebase = firebase;
        if (_firebase != null)
        {
            StartSessionListener();
            StartPrintListener();
        }
    }

    private void StartSessionListener()
    {
        _sessionListener = _firebase!.DbListen($"sessionLogs/{_userId}", (path, data) =>
        {
            if (data == null) return;
            var logs = new List<SessionLogItem>();
            try
            {
                foreach (var entry in data.Value.EnumerateObject())
                {
                    var log = entry.Value;
                    logs.Add(new SessionLogItem
                    {
                        EndTime = log.TryGetProperty("endTime", out var et) ? et.GetString() ?? "" : "",
                        ComputerName = log.TryGetProperty("computerName", out var cn) ? cn.GetString() ?? "" : "",
                        UsedSeconds = log.TryGetProperty("usedSeconds", out var us) ? (us.ValueKind == JsonValueKind.Number ? us.GetInt32() : 0) : 0,
                        Reason = log.TryGetProperty("reason", out var r) ? r.GetString() ?? "" : "",
                    });
                }
                logs.Sort((a, b) => string.Compare(b.EndTime, a.EndTime, StringComparison.Ordinal));
            }
            catch { }
            System.Windows.Application.Current?.Dispatcher.Invoke(() =>
            {
                SessionLogs.Clear();
                foreach (var l in logs) SessionLogs.Add(l);
                TotalSessionMinutes = logs.Sum(l => l.UsedSeconds) / 60;
            });
        });
    }

    private void StartPrintListener()
    {
        _printListener = _firebase!.DbListen($"printLogs/{_userId}", (path, data) =>
        {
            if (data == null) return;
            var logs = new List<PrintLogItem>();
            try
            {
                foreach (var entry in data.Value.EnumerateObject())
                {
                    var log = entry.Value;
                    logs.Add(new PrintLogItem
                    {
                        Timestamp = log.TryGetProperty("timestamp", out var ts) ? ts.GetString() ?? "" : "",
                        DocName = log.TryGetProperty("docName", out var dn) ? dn.GetString() ?? "" : "",
                        Pages = log.TryGetProperty("pages", out var p) ? (p.ValueKind == JsonValueKind.Number ? p.GetInt32() : 0) : 0,
                        Cost = log.TryGetProperty("cost", out var c) ? (c.ValueKind == JsonValueKind.Number ? c.GetDouble() : 0) : 0,
                        PrinterName = log.TryGetProperty("printerName", out var pn) ? pn.GetString() ?? "" : "",
                    });
                }
                logs.Sort((a, b) => string.Compare(b.Timestamp, a.Timestamp, StringComparison.Ordinal));
            }
            catch { }
            System.Windows.Application.Current?.Dispatcher.Invoke(() =>
            {
                PrintLogs.Clear();
                foreach (var l in logs) PrintLogs.Add(l);
                TotalPrintPages = logs.Sum(l => l.Pages);
                TotalPrintCost = logs.Sum(l => l.Cost);
            });
        });
    }

    public void Dispose()
    {
        _sessionListener?.Stop();
        _printListener?.Stop();
    }"""

c5 = content.count(old5)
print(f"Step 5: {c5}")
if c5 == 1:
    content = content.replace(old5, new5, 1)
    open(r'.\src\SionyxKiosk\ViewModels\HistoryViewModel.cs', 'w', encoding='utf-8').write(content)
    print("Step 5: OK - file written")
else:
    print("Step 5: NOT FOUND")
