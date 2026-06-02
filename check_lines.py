lines = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').readlines()
# הדפס שורות 288-305 כדי לראות בדיוק מה יש
for i, l in enumerate(lines[288:308], start=289):
    print(f"{i}: {repr(l)}")
