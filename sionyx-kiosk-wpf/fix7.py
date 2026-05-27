content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '''            .WriteTo.File(
                Path.Combine(logDir, "sionyx-.log"),
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 7,
            .WriteTo.File(
                Path.Combine(publicLogDir, "sionyx-.log"),
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 7,
                fileSizeLimitBytes: 10_000_000)
                fileSizeLimitBytes: 10_000_000)'''

new = '''            .WriteTo.File(
                Path.Combine(logDir, "sionyx-.log"),
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 7,
                fileSizeLimitBytes: 10_000_000)
            .WriteTo.File(
                Path.Combine(publicLogDir, "sionyx-.log"),
                rollingInterval: RollingInterval.Day,
                retainedFileCountLimit: 7,
                fileSizeLimitBytes: 10_000_000)'''

open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content.replace(old, new))
print('OK')
