content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = '''    private async Task StartMonitoringAsync()
    {
        await LoadPricingAsync();
        InitializeKnownJobs();
        _processedJobs.Clear();
        _stopRequested = false;
        _isMonitoring = true;'''

new = '''    private async Task StartMonitoringAsync()
    {
        // Stop idle listener - session listener takes over
        _idleBudgetListener?.Stop();
        _idleBudgetListener = null;
        await LoadPricingAsync();
        InitializeKnownJobs();
        _processedJobs.Clear();
        _stopRequested = false;
        _isMonitoring = true;'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print("OK - file written")
else:
    print("NOT FOUND - stop")
