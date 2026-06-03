f = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8')
c = f.read()
f.close()

old = '                services.AddTransient<AuthViewModel>(sp => new AuthViewModel(\n                    sp.GetRequiredService<AuthService>(),\n                    sp.GetRequiredService<OrganizationMetadataService>()));'
new = '                services.AddSingleton<AuthViewModel>(sp => new AuthViewModel(\n                    sp.GetRequiredService<AuthService>(),\n                    sp.GetRequiredService<OrganizationMetadataService>()));'

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
