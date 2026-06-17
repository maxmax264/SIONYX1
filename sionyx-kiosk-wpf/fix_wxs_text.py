content = open(r'.\installer\Package.wxs', encoding='utf-8').read()

old = '''    <Property Id="WIXUI_EXITDIALOGOPTIONALTEXT"
              Value="SIONYX מותקן ומוכן לשימוש!" />'''

new = '''    <Property Id="WIXUI_EXITDIALOGOPTIONALTEXT"
              Value="SIONYX is installed and ready!" />'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\Package.wxs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
