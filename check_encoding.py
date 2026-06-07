import re
with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8-sig') as f:
    content = f.read()

# מצא את הפונקציה לפי שורה ראשונה ואחרונה
idx = content.find('private static void RemoveUserAndProfile(string username, Session session)')
print(f"Found at index: {idx}")
if idx > 0:
    print(repr(content[idx:idx+200]))
