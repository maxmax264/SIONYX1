import urllib.request, json

# קרא את הקובץ הנוכחי כגיבוי
backup = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html.backup', encoding='utf-8').read()
print("Backup OK:", len(backup), "chars")

# בדוק שיש גישה לאינטרנט
try:
    urllib.request.urlopen("https://www.google.com", timeout=5)
    print("Internet: OK")
except:
    print("Internet: NO ACCESS")
