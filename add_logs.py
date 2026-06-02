import re

file_path = r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# לוגיקה להחלפת הקוד הקיים בקוד עם לוגים
old_block = """                if (d.TryGetProperty("cleanMode", out var cm)) CleanMode = cm.GetBoolean();
                if (d.TryGetProperty("formX", out var fx)) FormX = fx.GetDouble();
                if (d.TryGetProperty("formY", out var fy)) FormY = fy.GetDouble();
                if (d.TryGetProperty("formWidth", out var fw)) FormWidth = fw.GetDouble();"""

new_block = """                if (d.TryGetProperty("cleanMode", out var cm)) { 
                    CleanMode = cm.GetBoolean(); 
                    Serilog.Log.Information("[Design] CleanMode updated to {V}", CleanMode); 
                }
                if (d.TryGetProperty("formX", out var fx)) { 
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

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Logs added successfully.")
else:
    print("Could not find the block to replace. Please check the file content.")
