content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', encoding='utf-8').read()

old = '''        function initNedarimIframe() {
            var url = "https://matara.pro/nedarimplus/iframe?language=he";
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&
                           document.getElementById('saveCardCheck').checked;
            if (CONFIG.saveCardEnabled) {
                url += "&Tokef=Hide";
            }
            document.getElementById('NedarimFrame').src = url;
        }'''

new = '''        function initNedarimIframe() {
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&
                           document.getElementById('saveCardCheck').checked;
            var url = "https://matara.pro/nedarimplus/iframe?language=he";
            if (saveCard) {
                url += "&Tokef=Hide";
            }
            document.getElementById('NedarimFrame').src = url;
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    # Add onchange to checkbox to reload iframe
    old2 = '''                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;">'''
    new2 = '''                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;" onchange="initNedarimIframe()">'''
    content = content.replace(old2, new2, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
