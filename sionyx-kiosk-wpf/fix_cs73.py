content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '                                using var proc = System.Diagnostics.Process.Start(psi);\n                                var output = proc?.StandardOutput.ReadToEnd() ?? "";\n                                proc?.WaitForExit(5000);\n                                foreach (var line in output.Split(\'\\n\'))\n                                {\n                                    var trimmed = line.TrimStart(\'>\').Trim();\n                                    if (trimmed.StartsWith("USERNAME") || string.IsNullOrWhiteSpace(trimmed)) continue;\n                                    loggedInUser = trimmed.Split(\' \', System.StringSplitOptions.RemoveEmptyEntries)[0].TrimStart(\'>\');\n                                    break;\n                                }'

new = '                                var proc = System.Diagnostics.Process.Start(psi);\n                                var output = proc != null ? proc.StandardOutput.ReadToEnd() : "";\n                                if (proc != null) proc.WaitForExit(5000);\n                                foreach (var line in output.Split(\'\\n\'))\n                                {\n                                    var trimmed = line.TrimStart(\'>\').Trim();\n                                    if (trimmed.StartsWith("USERNAME") || string.IsNullOrWhiteSpace(trimmed)) continue;\n                                    var parts = trimmed.Split(new char[]{\' \'}, System.StringSplitOptions.RemoveEmptyEntries);\n                                    if (parts.Length > 0) loggedInUser = parts[0].TrimStart(\'>\');\n                                    break;\n                                }'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
