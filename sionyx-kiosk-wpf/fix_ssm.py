path = r'.\src\SionyxKiosk\Services\SystemServicesManager.cs'
content = open(path, encoding='utf-8').read()
content = content.replace(
    '        _forceLogoutHandler = reason =>\n        {\n            Logger.Warning("Force logout received: {Reason}", reason);\n            _ = Application.Current.Dispatcher.InvokeAsync(async () =>\n            {\n                if (ForceLogoutReceived != null)\n                    await ForceLogoutReceived.Invoke();\n            });\n        };',
    '        _forceLogoutHandler = reason =>\n        {\n            if (_forceLogout.IsPaused) return;\n            Logger.Warning("Force logout received: {Reason}", reason);\n            _ = Application.Current.Dispatcher.InvokeAsync(async () =>\n            {\n                if (ForceLogoutReceived != null)\n                    await ForceLogoutReceived.Invoke();\n            });\n        };'
)
open(path, 'w', encoding='utf-8').write(content)
print('OK')
