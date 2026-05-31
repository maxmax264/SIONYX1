content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()

old = 'remaining);\n                DispatchEvent(() => JobAllowed?.Invoke(docName, billablePages, cost, remaining));\n            }\n            else\n            {\n                CancelJob'

new = 'remaining);\n                DispatchEvent(() => JobAllowed?.Invoke(docName, billablePages, cost, remaining));\n                // Save print log\n                try\n                {\n                    var logKey = $"{DateTimeOffset.UtcNow.ToUnixTimeMilliseconds()}";\n                    var orgId = Firebase.OrgId;\n                    await Firebase.DbUpdateAsync($"organizations/{orgId}/printLogs/{_userId}/{logKey}", new Dictionary<string, object?>\n                    {\n                        ["userId"] = _userId,\n                        ["docName"] = docName,\n                        ["pages"] = billablePages,\n                        ["cost"] = cost,\n                        ["remaining"] = remaining,\n                        ["printerName"] = printerName,\n                        ["isColor"] = details.IsColor,\n                        ["timestamp"] = DateTime.Now.ToString("o"),\n                        ["computerName"] = Infrastructure.RegistryConfig.ReadValue("ComputerName") ?? Infrastructure.DeviceInfo.GetComputerName(),\n                    });\n                    Logger.Information("[LOG] Print log saved for user {UserId}", _userId);\n                }\n                catch (Exception ex)\n                {\n                    Logger.Warning(ex, "[LOG] Failed to save print log (non-fatal)");\n                }\n            }\n            else\n            {\n                CancelJob'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
