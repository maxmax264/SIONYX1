using System.Collections.ObjectModel;
using System.Collections.Specialized;
using System.Text.Json;
using CommunityToolkit.Mvvm.ComponentModel;
using SionyxKiosk.Infrastructure;
using SionyxKiosk.Models;
using SionyxKiosk.Services;

namespace SionyxKiosk.ViewModels;

public partial class PrintHistoryViewModel : ObservableObject, IDisposable
{
    private readonly PrintHistoryService _history;
    private readonly FirebaseClient? _firebase;
    private readonly string _userId;
    private SseListener? _printListener;

    [ObservableProperty] private int _totalPages;
    [ObservableProperty] private double _totalCost;
    [ObservableProperty] private int _approvedCount;
    [ObservableProperty] private int _deniedCount;

    public ObservableCollection<PrintJobRecord> Jobs => _history.Jobs;
    public bool HasJobs => Jobs.Count > 0;

    public PrintHistoryViewModel(PrintHistoryService history, string userId = "", FirebaseClient? firebase = null)
    {
        _history = history;
        _userId = userId;
        _firebase = firebase;

        RefreshStats();
        _history.Jobs.CollectionChanged += OnJobsChanged;

        if (_firebase != null)
            StartPrintListener();
    }

    private void StartPrintListener()
    {
        _printListener = _firebase!.DbListen($"printLogs/{_userId}", (path, data) =>
        {
            if (data == null) return;
            var records = new List<PrintJobRecord>();
            try
            {
                var root = data.Value;
                var logsEl = root.TryGetProperty("data", out var d) ? d : root;
                if (logsEl.ValueKind != JsonValueKind.Object) return;

                foreach (var entry in logsEl.EnumerateObject())
                {
                    var log = entry.Value;
                    var timestamp = log.TryGetProperty("timestamp", out var ts) ? ts.GetString() ?? "" : "";
                    var cost = log.TryGetProperty("cost", out var c) && c.ValueKind == JsonValueKind.Number ? c.GetDouble() : 0;
                    var pages = log.TryGetProperty("pages", out var p) && p.ValueKind == JsonValueKind.Number ? p.GetInt32() : 0;

                    records.Add(new PrintJobRecord
                    {
                        DocumentName = log.TryGetProperty("docName", out var dn) ? dn.GetString() ?? "Unknown" : "Unknown",
                        Pages = pages,
                        Copies = 1,
                        IsColor = false,
                        Cost = cost,
                        Status = "approved",
                        Timestamp = DateTime.TryParse(timestamp, out var dt) ? dt : DateTime.Now
                    });
                }

                records.Sort((a, b) => b.Timestamp.CompareTo(a.Timestamp));
            }
            catch { }

            System.Windows.Application.Current?.Dispatcher.Invoke(() =>
            {
                _history.Jobs.Clear();
                foreach (var r in records)
                    _history.Jobs.Add(r);
            });
        });
    }

    private void OnJobsChanged(object? sender, NotifyCollectionChangedEventArgs e)
    {
        RefreshStats();
        OnPropertyChanged(nameof(HasJobs));
    }

    private void RefreshStats()
    {
        TotalPages = _history.TotalPages;
        TotalCost = _history.TotalCost;
        ApprovedCount = _history.ApprovedCount;
        DeniedCount = _history.DeniedCount;
    }

    public void Dispose()
    {
        _history.Jobs.CollectionChanged -= OnJobsChanged;
        _printListener?.Stop();
    }
}
