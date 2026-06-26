with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'rb') as f:
    raw = f.read()
try:
    raw.decode('utf-8')
    print("Valid UTF-8 again - revert succeeded")
except UnicodeDecodeError as e:
    print("Still has the original 12 bad lines:", e)
