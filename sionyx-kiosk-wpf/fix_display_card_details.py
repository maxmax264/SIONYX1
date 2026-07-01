path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''                CONFIG = msg.config;
                if (CONFIG.savedKevaId) {
                    document.getElementById('savedCardPanel').style.display = 'flex';
                    document.getElementById('iframeSection').style.display = 'none';
                    document.getElementById('saveCardCheckBox').style.display = 'none';
                } else {'''

new = '''                CONFIG = msg.config;
                if (CONFIG.savedKevaId) {
                    document.getElementById('savedCardPanel').style.display = 'flex';
                    document.getElementById('iframeSection').style.display = 'none';
                    document.getElementById('saveCardCheckBox').style.display = 'none';
                    var sub = document.getElementById('savedCardSub');
                    if (sub) {
                        var parts = [];
                        if (CONFIG.savedCardLastNum) parts.push('מסתיים ב-' + CONFIG.savedCardLastNum);
                        if (CONFIG.savedCardExpiry) parts.push('בתוקף עד ' + CONFIG.savedCardExpiry);
                        sub.textContent = parts.length ? parts.join(' · ') : 'כרטיס שמור';
                    }
                } else {'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
