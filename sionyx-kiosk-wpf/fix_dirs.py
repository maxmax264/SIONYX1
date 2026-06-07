content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''                Directory.CreateDirectory(startupPath);
                Directory.CreateDirectory(sionyxDir);
                Directory.CreateDirectory(logsDir);
                session.Log("[OK] Profile directories created");'''

new = '''                // Create all standard Windows profile directories
                var standardDirs = new[]
                {
                    @"Desktop",
                    @"Documents",
                    @"Downloads",
                    @"Pictures",
                    @"Music",
                    @"Videos",
                    @"AppData\Local",
                    @"AppData\Local\Microsoft\Windows",
                    @"AppData\Local\Temp",
                    @"AppData\LocalLow",
                    @"AppData\Roaming",
                    @"AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
                    @"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup",
                };
                foreach (var dir in standardDirs)
                    Directory.CreateDirectory(Path.Combine(profilePath, dir));
                Directory.CreateDirectory(sionyxDir);
                Directory.CreateDirectory(logsDir);
                session.Log("[OK] Profile directories created");'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
