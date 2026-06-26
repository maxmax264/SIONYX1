import re
path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\installer\Package.wxs'
content = open(path, encoding='utf-8').read()

# Remove empty Shortcuts ComponentGroup
content = re.sub(r'\s*<ComponentGroup Id="Shortcuts".*?</ComponentGroup>', '', content, flags=re.DOTALL)

open(path, 'w', encoding='utf-8').write(content)
print("OK")
