content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\components\settings\PaymentSettings.jsx', encoding='utf-8').read()
content = content.replace('placeholder="לדוגמה: QWtE4M6uVn"', 'placeholder="הזן את קוד ה-ApiValid מנדרים פלוס"')
open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\components\settings\PaymentSettings.jsx', 'w', encoding='utf-8').write(content)
print('OK')
