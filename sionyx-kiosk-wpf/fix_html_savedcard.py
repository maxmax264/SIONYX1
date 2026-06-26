path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '                if (CONFIG.saveCardEnabled) {\n                    var c = document.getElementById(\'saveCardCheckBox\');\n                    if (c) c.style.display = \'block\';\n                }\n                initNedarimIframe();'

new = '                if (CONFIG.savedKevaId) {\n                    document.getElementById(\'savedCardPanel\').style.display = \'flex\';\n                    document.getElementById(\'iframeSection\').style.display = \'none\';\n                    document.getElementById(\'saveCardCheckBox\').style.display = \'none\';\n                } else {\n                    if (CONFIG.saveCardEnabled) {\n                        var c = document.getElementById(\'saveCardCheckBox\');\n                        if (c) c.style.display = \'block\';\n                    }\n                    initNedarimIframe();\n                }'

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
