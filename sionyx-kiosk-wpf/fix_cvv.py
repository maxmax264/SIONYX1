content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', encoding='utf-8').read()

old = '''        function initNedarimIframe() {
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&
                           document.getElementById('saveCardCheck').checked;
            var url = "https://matara.pro/nedarimplus/iframe?language=he";
            if (saveCard) {
                url += "&Tokef=Hide";
            }
            document.getElementById('NedarimFrame').src = url;
        }'''

new = '''        function initNedarimIframe() {
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&
                           document.getElementById('saveCardCheck').checked;
            var url = "https://matara.pro/nedarimplus/iframe?language=he";
            if (saveCard) {
                url += "&Tokef=Hide&CVV=Hide";
            }
            document.getElementById('NedarimFrame').src = url;
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
