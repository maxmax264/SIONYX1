content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

lines_to_remove = [
    '                if (d.TryGetProperty("formX", out var fx)) {\r\n                    FormX = fx.GetDouble();\r\n                    Serilog.Log.Information("[Design] FormX updated to {V}", FormX);\r\n                }',
    '                if (d.TryGetProperty("formY", out var fy)) {\r\n                    FormY = fy.GetDouble();\r\n                    Serilog.Log.Information("[Design] FormY updated to {V}", FormY);\r\n                }',
    '                if (d.TryGetProperty("formWidth", out var fw)) {\r\n                    FormWidth = fw.GetDouble();\r\n                    Serilog.Log.Information("[Design] FormWidth updated to {V}", FormWidth);\r\n                }',
    '                if (d.TryGetProperty("formX", out var fx)) {\n                    FormX = fx.GetDouble();\n                    Serilog.Log.Information("[Design] FormX updated to {V}", FormX);\n                }',
    '                if (d.TryGetProperty("formY", out var fy)) {\n                    FormY = fy.GetDouble();\n                    Serilog.Log.Information("[Design] FormY updated to {V}", FormY);\n                }',
    '                if (d.TryGetProperty("formWidth", out var fw)) {\n                    FormWidth = fw.GetDouble();\n                    Serilog.Log.Information("[Design] FormWidth updated to {V}", FormWidth);\n                }',
]

removed = 0
for line in lines_to_remove:
    if line in content:
        content = content.replace(line, '')
        removed += 1
        print(f"Removed: formX/formY/formWidth block")

if removed == 0:
    # try single-line format
    for old in [
        '                if (d.TryGetProperty("formX", out var fx)) FormX = fx.GetDouble();',
        '                if (d.TryGetProperty("formY", out var fy)) FormY = fy.GetDouble();',
        '                if (d.TryGetProperty("formWidth", out var fw)) FormWidth = fw.GetDouble();',
    ]:
        if old in content:
            content = content.replace(old, '')
            removed += 1
            print(f"Removed single-line: {old.strip()[:50]}")

print(f"Total removed: {removed}")
open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
