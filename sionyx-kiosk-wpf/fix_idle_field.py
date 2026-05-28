content = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').read()

old = '''    // Live sync from Firebase
    private SseListener? _remainingTimeListener;
    private bool _isFirstRemainingTimeEvent = true;'''
new = '''    // Live sync from Firebase
    private SseListener? _remainingTimeListener;
    private SseListener? _idleRemainingTimeListener;
    private bool _isFirstRemainingTimeEvent = true;'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\SessionService.cs', 'w', encoding='utf-8').write(content)
    print('OK - field added')
else:
    print('NOT FOUND - field')
