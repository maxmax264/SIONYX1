content = open(r'.\src\SionyxKiosk\Infrastructure\RegistryConfig.cs', encoding='utf-8').read()

old = '            // Required values\n            ["OrgId"] = ReadValue("OrgId"),\n            ["ApiKey"] = ReadValue("FirebaseApiKey"),'
new = '            // Required values\n            ["OrgId"] = ReadValue("OrgId"),\n            ["ComputerName"] = ReadValue("ComputerName"),\n            ["ApiKey"] = ReadValue("FirebaseApiKey"),'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Infrastructure\RegistryConfig.cs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
