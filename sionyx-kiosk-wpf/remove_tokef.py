path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = "function initNedarimIframe() {\n            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&\n                           document.getElementById('saveCardCheck').checked;\n            var url = \"https://matara.pro/nedarimplus/iframe?language=he\";\n            if (saveCard) {\n                url += \"&Tokef=Hide&CVV=Hide\";\n            }\n            document.getElementById('loadingIframe').style.display = 'flex';\n            document.getElementById('NedarimFrame').src = url;\n        }"

new = "function initNedarimIframe() {\n            var url = \"https://matara.pro/nedarimplus/iframe?language=he\";\n            document.getElementById('loadingIframe').style.display = 'flex';\n            document.getElementById('NedarimFrame').src = url;\n        }"

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
