import re, sys
path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\Package.wxs'
content = open(path, encoding='utf-8').read()

# Remove DesktopShortcutComp
content = re.sub(r'\s*<Component Id="DesktopShortcutComp".*?</Component>', '', content, flags=re.DOTALL)

# Remove StartMenuShortcutComp
content = re.sub(r'\s*<Component Id="StartMenuShortcutComp".*?</Component>', '', content, flags=re.DOTALL)

# Remove ComponentGroupRef to Shortcuts
content = content.replace('<ComponentGroupRef Id="Shortcuts" />', '')

# Remove DesktopFolder declaration
content = content.replace('<StandardDirectory Id="DesktopFolder" />', '')

open(path, 'w', encoding='utf-8').write(content)
print("OK")
