content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\PrintHistoryViewModel.cs', encoding='utf-8').read()
old = '    public PrintHistoryViewModel(PrintHistoryService history, string userId, FirebaseClient? firebase = null)'
new = '    public PrintHistoryViewModel(PrintHistoryService history, string userId = "", FirebaseClient? firebase = null)'
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\PrintHistoryViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
