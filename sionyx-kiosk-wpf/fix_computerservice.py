content = open(r'.\src\SionyxKiosk\Services\ComputerService.cs', encoding='utf-8').read()

old = "    public async Task<ServiceResult> RegisterComputerAsync(string? computerName = null, string? location = null)\n    {\n        try\n        {\n            LogOperation(\"RegisterComputer\");\n            var info = DeviceInfo.GetComputerInfo();\n            var computerId = info[\"deviceId\"].ToString()!;\n\n            var name = info[\"computerName\"].ToString()!;\n            if (!string.IsNullOrEmpty(computerName))\n                name = computerName;\n            else if (name == \"Unknown-PC\")\n                name = $\"PC-{computerId[..8].ToUpper()}\";"

new = "    public async Task<ServiceResult> RegisterComputerAsync(string? computerName = null, string? location = null)\n    {\n        try\n        {\n            LogOperation(\"RegisterComputer\");\n            var info = DeviceInfo.GetComputerInfo();\n            var computerId = info[\"deviceId\"].ToString()!;\n\n            // Priority: 1) passed param, 2) registry custom name, 3) Windows hostname, 4) fallback\n            var name = info[\"computerName\"].ToString()!;\n            if (!string.IsNullOrEmpty(computerName))\n                name = computerName;\n            else\n            {\n                var registryName = Infrastructure.RegistryConfig.ReadValue(\"ComputerName\");\n                if (!string.IsNullOrEmpty(registryName))\n                    name = registryName;\n                else if (name == \"Unknown-PC\")\n                    name = $\"PC-{computerId[..8].ToUpper()}\";\n            }"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Services\ComputerService.cs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
