path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = "function initNedarimIframe() {"
new = """function initNedarimIframe() {
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') && document.getElementById('saveCardCheck').checked;
            var iframeUrl = "https://matara.pro/nedarimplus/iframe?language=he";
            if (saveCard) iframeUrl += "&CVV=Hide";"""

count = content_n.count(old)
print(f"Found {count} matches")
