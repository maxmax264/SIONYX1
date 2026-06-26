path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''                if (CONFIG.savedKevaId) {
                    document.getElementById('savedCardPanel').style.display = 'flex';
                    document.getElementById('iframeSection').style.display = 'none';
                    document.getElementById('saveCardCheckBox').style.display = 'none';
                } else {
                    if (CONFIG.saveCardEnabled) {
                        var c = document.getElementById('saveCardCheckBox');
                        if (c) c.style.display = 'block';
                    }
                    initNedarimIframe();
                }'''

new = '''                if (CONFIG.savedKevaId) {
                    document.getElementById('savedCardPanel').style.display = 'flex';
                    document.getElementById('iframeSection').style.display = 'none';
                    document.getElementById('saveCardCheckBox').style.display = 'none';
                } else {
                    if (CONFIG.saveCardEnabled) {
                        var c = document.getElementById('saveCardCheckBox');
                        if (c) c.style.display = 'block';
                        // Default to checked - saving the card is opt-out, not opt-in
                        var cb = document.getElementById('saveCardCheck');
                        if (cb) cb.checked = true;
                    }
                    initNedarimIframe();
                }'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
