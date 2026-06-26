with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Services\KioskPolicyService.cs', 'rb') as f:
    raw = f.read()
try:
    raw.decode('utf-8')
    print("File is valid UTF-8, length:", len(raw))
except UnicodeDecodeError as e:
    print("File has encoding issues:", e)
