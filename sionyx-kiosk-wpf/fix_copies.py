content = open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', encoding='utf-8').read()
old = '''                        if (devMode.dmCopies > 1)
                        {
                            copies = devMode.dmCopies;
                        }
                        else
                        {
                            copies = ReadCopiesFromSpl(jobId);
                        }'''
new = '''                        // Windows 11 XPS driver bug: dmCopies sometimes contains
                        // page count instead of copy count (e.g. Notepad sends dmCopies=51
                        // for a 1-copy job). If dmCopies seems unreasonably large relative
                        // to TotalPages, fall back to SPL file which is always accurate.
                        var splCopies = ReadCopiesFromSpl(jobId);
                        if (devMode.dmCopies > 1 && (info.TotalPages == 0 || devMode.dmCopies <= info.TotalPages * 100))
                        {
                            copies = splCopies > 1 ? splCopies : devMode.dmCopies;
                        }
                        else if (splCopies > 1)
                        {
                            copies = splCopies;
                        }
                        else
                        {
                            copies = 1;
                        }'''
if old in content:
    open(r'.\src\SionyxKiosk\Services\PrintMonitorService.cs', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK')
else:
    print('NOT FOUND')
