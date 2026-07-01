path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

# Step 1: Remove the name input field + label from the form
old1 = '''            <div>
                <label class="input-label" for="clientName">שם מלא</label>
                <input type="text" id="clientName" class="input-field"
                       placeholder="שם מלא כפי שמופיע בכרטיס האשראי"
                       required autocomplete="off">
            </div>

            <!-- כרטיס שמור -->'''

new1 = '''            <!-- כרטיס שמור -->'''

count1 = content_n.count(old1)
print(f"Step 1 - Found {count1} matches")
if count1 == 1:
    content_n = content_n.replace(old1, new1, 1)
    print("Step 1 OK")
else:
    print("Step 1 NOT FOUND - aborting")
    exit()

# Step 2: setConfig no longer needs to populate the (now removed) input
old2 = '''                CONFIG = msg.config;
                if (CONFIG.userName) {
                    document.getElementById('clientName').value = CONFIG.userName;
                }
                if (CONFIG.savedKevaId) {'''

new2 = '''                CONFIG = msg.config;
                if (CONFIG.savedKevaId) {'''

count2 = content_n.count(old2)
print(f"Step 2 - Found {count2} matches")
if count2 == 1:
    content_n = content_n.replace(old2, new2, 1)
    print("Step 2 OK")
else:
    print("Step 2 NOT FOUND - aborting")
    exit()

# Step 3: handlePayment() - read name from CONFIG instead of the removed input
old3 = '''        function handlePayment() {
            var name = document.getElementById('clientName').value.trim();
            if (!name) { showError('נא להזין שם מלא'); return; }

            if (CONFIG.savedKevaId) {'''

new3 = '''        function handlePayment() {
            if (CONFIG.savedKevaId) {'''

count3 = content_n.count(old3)
print(f"Step 3 - Found {count3} matches")
if count3 == 1:
    content_n = content_n.replace(old3, new3, 1)
    print("Step 3 OK")
else:
    print("Step 3 NOT FOUND - aborting")
    exit()

# Step 4: onPurchaseCreated() - read name from CONFIG instead of the removed input
old4 = '''        function onPurchaseCreated(purchaseId) {
            var name = document.getElementById('clientName').value.trim();
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&'''

new4 = '''        function onPurchaseCreated(purchaseId) {
            var name = CONFIG.userName || '';
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&'''

count4 = content_n.count(old4)
print(f"Step 4 - Found {count4} matches")
if count4 == 1:
    content_n = content_n.replace(old4, new4, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("Step 4 OK - file saved")
else:
    print("Step 4 NOT FOUND - file NOT saved")
