content = open(r'.\installer\Package.wxs', encoding='utf-8').read()

old = '    <SetProperty Id="CA_LaunchKiosk"        Before="CA_LaunchKiosk"        Sequence="execute" Value="INSTALLDIR=[INSTALLFOLDER]" />\n\n'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, '', 1)
    open(r'.\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    # try without trailing newline
    old2 = '    <SetProperty Id="CA_LaunchKiosk"        Before="CA_LaunchKiosk"        Sequence="execute" Value="INSTALLDIR=[INSTALLFOLDER]" />\n'
    count2 = content.count(old2)
    print(f"Found {count2} matches (variant 2)")
    if count2 == 1:
        content = content.replace(old2, '', 1)
        open(r'.\installer\Package.wxs', 'w', encoding='utf-8').write(content)
        print("DONE")
    else:
        print("NOT FOUND")
