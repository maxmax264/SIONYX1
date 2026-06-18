import re

with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8') as f:
    content = f.read()

fixes = {
    '׳׳×׳"': 'אתה',
    '׳׳ ׳"׳': 'מנהל',
    '׳₪׳™׳§׳•׳—': 'פיקוח',
    '׳"׳•׳"׳¢׳•׳×': 'הודעות',
    '׳׳׳ ׳"׳': 'מנהל',
    '׳׳"׳₪׳™׳§׳•׳—': 'הפיקוח',
    '׳×׳'׳•׳'׳"': 'תגובה',
    '׳ ׳©׳׳—׳"': 'נשלחה',
    '׳׳×׳•׳': 'אתמול',
}

for bad, good in fixes.items():
    content = content.replace(bad, good)

with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
