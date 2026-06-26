path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:14px; font-weight:700; color:#0F172A; flex-shrink:0;">CVV:</span>
                    <input type="password" id="savedCvvInput" maxlength="4" placeholder="&#x2022;&#x2022;&#x2022;" autocomplete="off" inputmode="numeric"
                        style="width:110px; padding:10px 14px; border:2px solid #E2E8F0; border-radius:10px; font-size:20px; font-weight:700; color:#0F172A; background:white; outline:none; letter-spacing:6px; text-align:center; direction:ltr; font-family:'Courier New',monospace;">
                    <span style="font-size:12px; color:#94A3B8; font-weight:500;">3-4 ספרות בגב הכרטיס</span>
                </div>
                <button onclick="useOtherCard()"'''

new = '''                <button onclick="useOtherCard()"'''

count = content_n.count(old)
print(f"Step 1 - Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    print("Step 1 OK")
else:
    print("Step 1 NOT FOUND - aborting")
    exit()

old2 = '''        function handlePayment() {
            var name = document.getElementById('clientName').value.trim();
            if (!name) { showError('נא להזין שם מלא'); return; }

            if (CONFIG.savedKevaId) {
                var cvv = document.getElementById('savedCvvInput').value.trim();
                if (!cvv) { showError('נא להזין CVV'); return; }
                hideError();
                document.getElementById('formSection').style.display = 'none';
                document.getElementById('loadingPayment').classList.add('active');
                window.chrome.webview.postMessage({ action: 'chargeWithSavedCard', cvv: cvv });
                return;
            }'''

new2 = '''        function handlePayment() {
            var name = document.getElementById('clientName').value.trim();
            if (!name) { showError('נא להזין שם מלא'); return; }

            if (CONFIG.savedKevaId) {
                hideError();
                document.getElementById('formSection').style.display = 'none';
                document.getElementById('loadingPayment').classList.add('active');
                window.chrome.webview.postMessage({ action: 'chargeWithSavedCard' });
                return;
            }'''

count2 = content_n.count(old2)
print(f"Step 2 - Found {count2} matches")
if count2 == 1:
    content_n = content_n.replace(old2, new2, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("Step 2 OK - file saved")
else:
    print("Step 2 NOT FOUND - file NOT saved")
