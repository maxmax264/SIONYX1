f = open(r'.\src\SionyxKiosk\Infrastructure\Logging\LoggingSetup.cs', encoding='utf-8')
c = f.read()
f.close()

old = '''        if (RegistryConfig.IsProduction())
        {
            return Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "SIONYX", "logs");
        }'''
new = '''        if (RegistryConfig.IsProduction())
        {
            return Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.CommonDocuments),
                "SIONYX", "logs");
        }'''

assert c.count(old) == 1
c = c.replace(old, new, 1)
open(r'.\src\SionyxKiosk\Infrastructure\Logging\LoggingSetup.cs', 'w', encoding='utf-8').write(c)
print("OK")
