content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '                        if (winlogon != null)\n                        {\n                            winlogon.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);\n                            winlogon.DeleteValue("DefaultPassword", false);\n                            session.Log("[OK] Auto-login configured");\n                        }'

new = '''                        if (winlogon != null)
                        {
                            // Get the actual logged-in user via query user
                            string loggedInUser = "";
                            try
                            {
                                var psi = new System.Diagnostics.ProcessStartInfo("query", "user")
                                {
                                    UseShellExecute = false,
                                    RedirectStandardOutput = true,
                                    CreateNoWindow = true
                                };
                                using var proc = System.Diagnostics.Process.Start(psi);
                                var output = proc?.StandardOutput.ReadToEnd() ?? "";
                                proc?.WaitForExit(5000);
                                foreach (var line in output.Split('\\n'))
                                {
                                    var trimmed = line.TrimStart('>').Trim();
                                    if (trimmed.StartsWith("USERNAME") || string.IsNullOrWhiteSpace(trimmed)) continue;
                                    loggedInUser = trimmed.Split(' ', System.StringSplitOptions.RemoveEmptyEntries)[0].TrimStart('>');
                                    break;
                                }
                            }
                            catch { }
                            session.Log($"[INFO] Logged-in user: {loggedInUser}");

                            winlogon.SetValue("AutoAdminLogon", "1", RegistryValueKind.String);
                            if (!string.IsNullOrEmpty(loggedInUser))
                                winlogon.SetValue("DefaultUserName", loggedInUser, RegistryValueKind.String);
                            winlogon.DeleteValue("DefaultPassword", false);
                            session.Log("[OK] Auto-login configured");
                        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    idx = content.find('AutoAdminLogon')
    print(repr(content[idx:idx+200]))
