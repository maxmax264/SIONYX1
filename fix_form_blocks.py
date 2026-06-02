content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

# הסר formX/formY/formWidth מה-LoadAuthDesignAsync
old = """                if (d.TryGetProperty("formX", out var fx)) {
                    FormX = fx.GetDouble();
                    Serilog.Log.Information("[Design] FormX updated to {V}", FormX);
                }
                if (d.TryGetProperty("formY", out var fy)) {
                    FormY = fy.GetDouble();
                    Serilog.Log.Information("[Design] FormY updated to {V}", FormY);
                }
                if (d.TryGetProperty("formWidth", out var fw)) {
                    FormWidth = fw.GetDouble();
                    Serilog.Log.Information("[Design] FormWidth updated to {V}", FormWidth);
                }"""

if old in content:
    content = content.replace(old, "")
    print("Removed formX/Y/Width blocks: OK")
else:
    print("NOT FOUND - trying CRLF")
    old2 = old.replace('\n', '\r\n')
    if old2 in content:
        content = content.replace(old2, "")
        print("Removed CRLF: OK")
    else:
        # מציא את המיקום
        idx = content.find('formX')
        print(f"formX found at index: {idx}")
        print(repr(content[idx-50:idx+200]))

open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
