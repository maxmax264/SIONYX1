lines = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').readlines()

# הוסף דגל _isPricingLoaded אחרי שורה 215
lines.insert(215, '    private bool _isPricingLoaded;\n')

# מצא את LoadPricingAsync ושנה אותה
start = next(i for i,l in enumerate(lines) if 'private async Task LoadPricingAsync' in l)
lines.insert(start, '    public Task PreloadPricingAsync() => LoadPricingAsync();\n')

# הוסף בדיקה בתחילת LoadPricingAsync
body_start = next(i for i,l in enumerate(lines) if 'private async Task LoadPricingAsync' in l) + 2
lines.insert(body_start, '        if (_isPricingLoaded) return;\n')

# מצא את השורה שמגדירה _colorPrice בתוך הפונקציה ושים _isPricingLoaded = true אחריה
price_set = next(i for i,l in enumerate(lines) if '_colorPrice' in l and 'cVal' in l)
lines.insert(price_set + 1, '                _isPricingLoaded = true;\n')

open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').writelines(lines)
print('OK')
