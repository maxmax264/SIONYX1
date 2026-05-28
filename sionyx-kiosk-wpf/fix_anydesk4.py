content = open(r'.\src\SionyxKiosk\Services\ProcessRestrictionService.cs', encoding='utf-8').read()

old = '        catch (Exception ex)\n        {\n            Logger.Error("Error terminating {Name}: {Error}", name, ex.Message);\n            ErrorOccurred?.Invoke($"Error blocking {name}");\n        }'
new = '        catch (Exception ex)\n        {\n            _permanentlyFailed.Add(proc.Id);\n            Logger.Error("Error terminating {Name} (PID:{Pid}) — will not retry: {Error}", name, proc.Id, ex.Message);\n            ErrorOccurred?.Invoke($"Error blocking {name}");\n        }'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ProcessRestrictionService.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
