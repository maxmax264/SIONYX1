f = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8')
lines = f.readlines()
f.close()

# תקן שורה 1009+1010 (index 1008+1009)
lines[1008] = '                            File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] PendingRename registered for {mainProfile}\\n");\n'
lines[1009] = ''

# תקן שורה 1016+1017 (index 1015+1016)
lines[1015] = '                        File.AppendAllText(@"C:\\Users\\user\\Desktop\\sionyx_debug.log", $"[{DateTime.Now}] PendingRename FAILED: {rex.Message}\\n");\n'
lines[1016] = ''

f = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8')
f.writelines(lines)
f.close()
print("SAVED")
