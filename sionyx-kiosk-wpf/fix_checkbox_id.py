path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = "                if (CONFIG.saveCardEnabled) {\n                    var c = document.getElementById('saveCardContainer');\n                    if (c) c.style.display = 'block';\n                }"

new = "                if (CONFIG.saveCardEnabled) {\n                    var c = document.getElementById('saveCardCheckBox');\n                    if (c) c.style.display = 'block';\n                }"

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
