lines = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').readlines()

# הוסף public log directory אחרי שורה 44 (var logDir = ...)
idx = next(i for i,l in enumerate(lines) if 'Directory.CreateDirectory(logDir)' in l)
lines.insert(idx + 1, '        var publicLogDir = Path.Combine(@"C:\\Users\\Public\\Documents\\SIONYX", "logs");\n')
lines.insert(idx + 2, '        Directory.CreateDirectory(publicLogDir);\n')

# מצא את retainedFileCountLimit והוסף WriteTo.File נוסף אחרי .CreateLogger
create_idx = next(i for i,l in enumerate(lines) if 'retainedFileCountLimit' in l)
lines.insert(create_idx + 1, '            .WriteTo.File(\n')
lines.insert(create_idx + 2, '                Path.Combine(publicLogDir, "sionyx-.log"),\n')
lines.insert(create_idx + 3, '                rollingInterval: RollingInterval.Day,\n')
lines.insert(create_idx + 4, '                retainedFileCountLimit: 7,\n')
lines.insert(create_idx + 5, '                fileSizeLimitBytes: 10_000_000)\n')

open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').writelines(lines)
print('OK')
