using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Text.Json;
using System.Windows.Data;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Models;
using SionyxKiosk.Services;

namespace SionyxKiosk.ViewModels;

/// <summary>History page ViewModel: purchase history with search, filter, sort.</summary>
public partial class HistoryViewModel : ObservableObject, IDisposable
{
    private readonly FirebaseClient? _firebase;
    private SseListener? _sessionListener;
    private SseListener? _printListener;
    private readonly PurchaseService _purchaseService;
    private readonly string _userId;

    private ObservableCollection<Purchase> _allPurchases = new();

    [ObservableProperty] private bool _isLoading;
    [ObservableProperty] private string _errorMessage = "";
    [ObservableProperty] private double _totalSpent;
    [ObservableProperty] private int _totalPurchases;
    [ObservableProperty] private double _totalPrintBudget;
    [ObservableProperty] private string _searchText = "";
    [ObservableProperty] private string _selectedStatus = "הכל";
    [ObservableProperty] private bool _sortNewestFirst = true;
    public ObservableCollection<SessionLogItem> SessionLogs { get; } = new();
    public ObservableCollection<PrintLogItem> PrintLogs { get; } = new();
    [ObservableProperty] private int _totalSessionMinutes;
    [ObservableProperty] private int _totalPrintPages;
    [ObservableProperty] private double _totalPrintCost;
    [ObservableProperty] private bool _isPurchasesTab = true;
    [ObservableProperty] private bool _isSessionsTab = false;
    [ObservableProperty] private bool _isPrintsTab = false;
    public bool IsPurchasesTabVisible => IsPurchasesTab;
    public bool IsSessionsTabVisible => IsSessionsTab;
    public bool IsPrintsTabVisible => IsPrintsTab;

    /// <summary>Filtered and sorted view of purchases, bound to the UI.</summary>
    public ICollectionView FilteredPurchases { get; }

    /// <summary>Status options for the filter dropdown.</summary>
    public List<string> StatusOptions { get; } = new() { "הכל", "הושלם", "ממתין", "נכשל", "בוטל" };

    public HistoryViewModel(PurchaseService purchaseService, string userId, FirebaseClient? firebase = null)
    {
        _purchaseService = purchaseService;
        _userId = userId;

        FilteredPurchases = CollectionViewSource.GetDefaultView(_allPurchases);
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
    }

    partial void OnSearchTextChanged(string value) => FilteredPurchases.Refresh();
    partial void OnIsPurchasesTabChanged(bool value) { OnPropertyChanged(nameof(IsPurchasesTabVisible)); OnPropertyChanged(nameof(IsSessionsTabVisible)); OnPropertyChanged(nameof(IsPrintsTabVisible)); }
    partial void OnIsSessionsTabChanged(bool value) { OnPropertyChanged(nameof(IsPurchasesTabVisible)); OnPropertyChanged(nameof(IsSessionsTabVisible)); OnPropertyChanged(nameof(IsPrintsTabVisible)); }
    partial void OnIsPrintsTabChanged(bool value) { OnPropertyChanged(nameof(IsPurchasesTabVisible)); OnPropertyChanged(nameof(IsSessionsTabVisible)); OnPropertyChanged(nameof(IsPrintsTabVisible)); }
    partial void OnSelectedStatusChanged(string value) => FilteredPurchases.Refresh();

    [RelayCommand]
    private void ToggleSort()
    {
        SortNewestFirst = !SortNewestFirst;
        FilteredPurchases.SortDescriptions.Clear();
        FilteredPurchases.SortDescriptions.Add(new SortDescription(
            nameof(Purchase.CreatedAt),
            SortNewestFirst ? ListSortDirection.Descending : ListSortDirection.Ascending));
    }

    [RelayCommand]
    private async Task LoadHistoryAsync()
    {
        IsLoading = true;
        ErrorMessage = "";

        var result = await _purchaseService.GetUserPurchaseHistoryAsync(_userId);
        IsLoading = false;

        if (result.IsSuccess && result.Data is List<Purchase> purchases)
        {
            _allPurchases.Clear();
            foreach (var p in purchases)
                _allPurchases.Add(p);

            TotalPurchases = purchases.Count;
            TotalSpent = purchases.Where(p => p.Status == "completed").Sum(p => p.Amount);
            TotalPrintBudget = purchases.Where(p => p.Status == "completed").Sum(p => p.PrintBudget);
            FilteredPurchases.Refresh();
        }
        else
        {
            ErrorMessage = result.Error ?? "שגיאה בטעינת היסטוריה";
        }
    }

    private bool ApplyFilter(object obj)
    {
        if (obj is not Purchase purchase) return false;

        // Status filter
        if (SelectedStatus != "הכל")
        {
            var statusLabel = PurchaseStatusExtensions.Parse(purchase.Status).ToHebrewLabel();
            if (statusLabel != SelectedStatus) return false;
        }

        // Search filter
        if (!string.IsNullOrWhiteSpace(SearchText))
        {
            var term = SearchText.Trim();
            if (!purchase.PackageName.Contains(term, StringComparison.OrdinalIgnoreCase) &&
                !purchase.Amount.ToString("F2").Contains(term) &&
                !purchase.CreatedAt.Contains(term))
                return false;
        }

        return true;
    }
}
