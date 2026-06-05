path = r'.\src\SionyxKiosk\Services\SystemServicesManager.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    '            if (_forceLogout.IsPaused) return;\n            Logger.Warning("Force logout received: {Reason}", reason);\n            _ = Application.Current.Dispatcher.InvokeAsync(async () =>\n            {\n                if (ForceLogoutReceived != null)\n                    await ForceLogoutReceived.Invoke();\n            });',
    '            Logger.Warning("Force logout received: {Reason}", reason);\n            _ = Application.Current.Dispatcher.InvokeAsync(async () =>\n            {\n                if (_forceLogout.IsPaused) { Logger.Warning("ForceLogout suppressed - password change in progress"); return; }\n                if (ForceLogoutReceived != null)\n                    await ForceLogoutReceived.Invoke();\n            });'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
