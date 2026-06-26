content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', encoding='utf-8').read()

old = '''        function onPurchaseCreated(purchaseId) {
            var name = document.getElementById('clientName').value.trim();
            postToNedarim({
                'Name': 'FinishTransaction2',
                'Value': {
                    'Mosad': CONFIG.mosadId,
                    'ApiValid': CONFIG.apiValid,
                    'PaymentType': 'Ragil',
                    'Currency': '1',
                    'Zeout': '',
                    'FirstName': name,
                    'LastName': '',
                    'Street': '',
                    'City': '',
                    'Phone': '',
                    'Mail': '',
                    'Amount': CONFIG.amount,
                    'Tashlumim': '1',
                    'Groupe': '',
                    'Comment': '\u05e8\u05db\u05d9\u05e9\u05ea \u05d7\u05d1\u05d9\u05dc\u05d4: ' + CONFIG.packageName,
                    'Param1': purchaseId,
                    'Param2': CONFIG.orgId || '',
                    'ForceUpdateMatching': '0',
                    'CallBack': CONFIG.callbackUrl || '',
                    'CallBackMailError': ''
                }
            });
        }'''

new = '''        function onPurchaseCreated(purchaseId) {
            var name = document.getElementById('clientName').value.trim();
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&
                           document.getElementById('saveCardCheck').checked;
            var paymentType = saveCard ? 'CreateToken' : 'Ragil';
            var apiValidToUse = saveCard && CONFIG.saveCardApiValid ? CONFIG.saveCardApiValid : CONFIG.apiValid;
            postToNedarim({
                'Name': 'FinishTransaction2',
                'Value': {
                    'Mosad': CONFIG.mosadId,
                    'ApiValid': apiValidToUse,
                    'PaymentType': paymentType,
                    'Currency': '1',
                    'Zeout': '',
                    'FirstName': name,
                    'LastName': '',
                    'Street': '',
                    'City': '',
                    'Phone': '',
                    'Mail': '',
                    'Amount': CONFIG.amount,
                    'Tashlumim': '1',
                    'Groupe': '',
                    'Comment': '\u05e8\u05db\u05d9\u05e9\u05ea \u05d7\u05d1\u05d9\u05dc\u05d4: ' + CONFIG.packageName,
                    'Param1': purchaseId,
                    'Param2': CONFIG.orgId || '',
                    'ForceUpdateMatching': '0',
                    'CallBack': CONFIG.callbackUrl || '',
                    'CallBackMailError': ''
                }
            });
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    # Add save card checkbox after clientName input
    old2 = '                <button id="payButton" class="btn-pay" onclick="handlePayment()">'
    new2 = '''                <div id="saveCardContainer" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer; font-size:15px; font-weight:600; color:#0F172A;">
                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;">
                        \u05e9\u05de\u05d5\u05e8 \u05db\u05e8\u05d8\u05d9\u05e1 \u05dc\u05e8\u05db\u05d9\u05e9\u05d5\u05ea \u05d4\u05d1\u05d0\u05d5\u05ea
                    </label>
                    <p style="margin:6px 0 0 28px; font-size:12px; color:#94A3B8;">\u05d4\u05db\u05e8\u05d8\u05d9\u05e1 \u05e0\u05e9\u05de\u05e8 \u05d1\u05e6\u05d5\u05e8\u05d4 \u05de\u05d0\u05d5\u05d1\u05d8\u05d7\u05ea \u05d0\u05e6\u05dc \u05e0\u05d3\u05e8\u05d9\u05dd \u05e4\u05dc\u05d5\u05e1. \u05d1\u05e4\u05e2\u05dd \u05d4\u05d1\u05d0\u05d4 \u05ea\u05d6\u05d3\u05e7\u05e7 \u05dc\u05d4\u05d6\u05d9\u05df \u05e8\u05e7 CVV.</p>
                </div>
                <button id="payButton" class="btn-pay" onclick="handlePayment()">'''
    content = content.replace(old2, new2, 1)
    # Show checkbox when config loaded
    old3 = "        window.chrome.webview.addEventListener('message', function(event) {\n            const msg = event.data;\n            if (msg.action === 'setConfig') {\n                CONFIG = msg.config;\n                if (CONFIG.userName) {\n                    document.getElementById('clientName').value = CONFIG.userName;\n                }\n            }"
    new3 = "        window.chrome.webview.addEventListener('message', function(event) {\n            const msg = event.data;\n            if (msg.action === 'setConfig') {\n                CONFIG = msg.config;\n                if (CONFIG.userName) {\n                    document.getElementById('clientName').value = CONFIG.userName;\n                }\n                if (CONFIG.saveCardEnabled) {\n                    var c = document.getElementById('saveCardContainer');\n                    if (c) c.style.display = 'block';\n                }\n            }"
    content = content.replace(old3, new3, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
