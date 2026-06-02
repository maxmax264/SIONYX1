f = open(r'.\src\components\settings\KioskDesignSettings.jsx', encoding='utf-8')
c = f.read()
f.close()
# מצא את פונקציית השמירה
idx = c.find('handleSave')
if idx == -1:
    idx = c.find('onSave')
if idx == -1:
    idx = c.find('set(')
print('=== פונקציית שמירה ===')
print(c[idx:idx+600])
