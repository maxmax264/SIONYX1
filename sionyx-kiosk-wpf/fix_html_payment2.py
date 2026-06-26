path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = "        function handlePayment() {\n            var name = document.getElementById('clientName').value.trim();\n            if (!name) { showError('\u05e0\u05d0 \u05dc\u05d4\u05d6\u05d9\u05df \u05e9\u05dd \u05de\u05dc\u05d0'); return; }\n\n            hideError();\n            document.getElementById('formSection').style.display = 'none';\n            document.getElementById('loadingPayment').classList.add('active');\n\n            window.chrome.webview.postMessage({ action: 'createPendingPurchase' });\n        }"

new = "        function handlePayment() {\n            var name = document.getElementById('clientName').value.trim();\n            if (!name) { showError('\u05e0\u05d0 \u05dc\u05d4\u05d6\u05d9\u05df \u05e9\u05dd \u05de\u05dc\u05d0'); return; }\n\n            if (CONFIG.savedKevaId) {\n                var cvv = document.getElementById('savedCvvInput').value.trim();\n                if (!cvv) { showError('\u05e0\u05d0 \u05dc\u05d4\u05d6\u05d9\u05df CVV'); return; }\n                hideError();\n                document.getElementById('formSection').style.display = 'none';\n                document.getElementById('loadingPayment').classList.add('active');\n                window.chrome.webview.postMessage({ action: 'createPendingPurchase', useSavedCard: true, cvv: cvv });\n                return;\n            }\n\n            hideError();\n            document.getElementById('formSection').style.display = 'none';\n            document.getElementById('loadingPayment').classList.add('active');\n\n            window.chrome.webview.postMessage({ action: 'createPendingPurchase' });\n        }\n\n        function useOtherCard() {\n            document.getElementById('savedCardPanel').style.display = 'none';\n            document.getElementById('iframeSection').style.display = 'flex';\n            if (CONFIG.saveCardEnabled)\n                document.getElementById('saveCardCheckBox').style.display = 'block';\n            CONFIG.savedKevaId = null;\n            initNedarimIframe();\n        }\n\n        function deleteCard() {\n            window.chrome.webview.postMessage({ action: 'deleteCard' });\n            useOtherCard();\n        }"

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
