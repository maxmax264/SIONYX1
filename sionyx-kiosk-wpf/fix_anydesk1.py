content = open(r'.\src\SionyxKiosk\Services\ProcessRestrictionService.cs', encoding='utf-8').read()

old = '        catch (System.ComponentModel.Win32Exception)\n        {\n            _recentlyBlocked.Add(proc.Id);\n            Logger.Warning("Access denied terminating {Name}. User may be admin.", name);\n            ErrorOccurred?.Invoke($"Cannot terminate {name} - access denied");\n        }'
new = '        catch (System.ComponentModel.Win32Exception)\n        {\n            _recentlyBlocked.Add(proc.Id);\n            _permanentlyFailed.Add(proc.Id);\n            Logger.Warning("Access denied terminating {Name} (PID:{Pid}) — will not retry.", name, proc.Id);\n            ErrorOccurred?.Invoke($"Cannot terminate {name} - access denied");\n        }'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ProcessRestrictionService.cs', 'w', encoding='utf-8').write(content)
    print('OK - Win32Exception')
else:
    print('NOT FOUND')
