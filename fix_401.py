content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8').read()

old = '''            var url = $"{cfg.DatabaseUrl}/organizations/{cfg.OrgId}/metadata/authDesign.json";
            var json = await http.GetStringAsync(url);'''

new = '''            var url = $"{cfg.DatabaseUrl}/organizations/{cfg.OrgId}/metadata/authDesign.json";
            var response = await http.GetAsync(url);
            if (!response.IsSuccessStatusCode) { Serilog.Log.Warning("[Design] authDesign HTTP {S}", response.StatusCode); return; }
            var json = await response.Content.ReadAsStringAsync();'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
