content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', encoding='utf-8').read()

old = '''        window.onload = function() {
            window.addEventListener("message", handlePostMessage, false);
            document.getElementById('NedarimFrame').onload = function() {
                postToNedarim({'Name': 'GetHeight'});
            };
            document.getElementById('NedarimFrame').src =
                "https://matara.pro/nedarimplus/iframe?language=he";
        };'''

new = '''        window.onload = function() {
            window.addEventListener("message", handlePostMessage, false);
            document.getElementById('NedarimFrame').onload = function() {
                postToNedarim({'Name': 'GetHeight'});
            };
            // iframe src will be set after CONFIG is received
        };

        function initNedarimIframe() {
            var url = "https://matara.pro/nedarimplus/iframe?language=he";
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&
                           document.getElementById('saveCardCheck').checked;
            if (CONFIG.saveCardEnabled) {
                url += "&Tokef=Hide";
            }
            document.getElementById('NedarimFrame').src = url;
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    # Call initNedarimIframe after config is set
    old2 = '''                if (CONFIG.saveCardEnabled) {
                    var c = document.getElementById('saveCardContainer');
                    if (c) c.style.display = 'block';
                }
            }'''
    new2 = '''                if (CONFIG.saveCardEnabled) {
                    var c = document.getElementById('saveCardContainer');
                    if (c) c.style.display = 'block';
                }
                initNedarimIframe();
            }'''
    content = content.replace(old2, new2, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
