path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''        function initNedarimIframe() {
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') && document.getElementById('saveCardCheck').checked;
            var url = "https://matara.pro/nedarimplus/iframe?language=he";
            if (saveCard) url += "&Tokef=Hide&CVV=Hide";
            document.getElementById('loadingIframe').style.display = 'flex';
            document.getElementById('NedarimFrame').src = url;
        }'''

new = '''        function initNedarimIframe() {
            // CVV is never required: Nedarim does not store it and it cannot be verified
            // for saved-card charges anyway, so we never ask for it - regardless of whether
            // the card is being saved or not. Card number + expiry only.
            var url = "https://matara.pro/nedarimplus/iframe?language=he&CVV=Hide";
            document.getElementById('loadingIframe').style.display = 'flex';
            document.getElementById('NedarimFrame').src = url;
        }'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
