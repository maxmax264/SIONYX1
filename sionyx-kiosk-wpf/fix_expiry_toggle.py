path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

# Step 1: onSaveCardToggle shows/hides the expiry row based on checkbox state
old1 = '''        function onSaveCardToggle() {
            initNedarimIframe();
        }'''

new1 = '''        function onSaveCardToggle() {
            var checked = document.getElementById('saveCardCheck').checked;
            var row = document.getElementById('saveCardExpiryRow');
            if (row) row.style.display = checked ? 'flex' : 'none';
            initNedarimIframe();
        }'''

count1 = content_n.count(old1)
print(f"Step 1 - Found {count1} matches")
if count1 == 1:
    content_n = content_n.replace(old1, new1, 1)
    print("Step 1 OK")
else:
    print("Step 1 NOT FOUND - aborting")
    exit()

# Step 2: since checkbox now starts checked by default, show the expiry row immediately too
old2 = '''                    if (CONFIG.saveCardEnabled) {
                        var c = document.getElementById('saveCardCheckBox');
                        if (c) c.style.display = 'block';
                        // Default to checked - saving the card is opt-out, not opt-in
                        var cb = document.getElementById('saveCardCheck');
                        if (cb) cb.checked = true;
                    }
                    initNedarimIframe();'''

new2 = '''                    if (CONFIG.saveCardEnabled) {
                        var c = document.getElementById('saveCardCheckBox');
                        if (c) c.style.display = 'block';
                        // Default to checked - saving the card is opt-out, not opt-in
                        var cb = document.getElementById('saveCardCheck');
                        if (cb) cb.checked = true;
                        var row = document.getElementById('saveCardExpiryRow');
                        if (row) row.style.display = 'flex';
                    }
                    initNedarimIframe();'''

count2 = content_n.count(old2)
print(f"Step 2 - Found {count2} matches")
if count2 == 1:
    content_n = content_n.replace(old2, new2, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("Step 2 OK - file saved")
else:
    print("Step 2 NOT FOUND - file NOT saved")
