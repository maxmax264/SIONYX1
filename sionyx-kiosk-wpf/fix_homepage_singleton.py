content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '''                services.AddTransient<HomePage>(sp =>
                {
                    var vm = sp.GetRequiredService<HomeViewModel>();
                    return new HomePage(vm, sp);
                });'''
new = '''                services.AddSingleton<HomePage>(sp =>
                {
                    var vm = sp.GetRequiredService<HomeViewModel>();
                    return new HomePage(vm, sp);
                });'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
