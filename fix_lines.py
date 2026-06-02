lines = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').readlines()
# הסר שורות 292-303 (אינדקס 291-302)
del lines[291:303]
open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').writelines(lines)
print("Removed lines 292-303: OK")
