path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''            else if (msg.action === 'savedCardCharging') {
                // C# is charging via saved card - stay on loading screen
                document.getElementById('formSection').style.display = 'none';
                document.getElementById('loadingPayment').classList.add('active');
            }
        });'''

new = '''            else if (msg.action === 'savedCardCharging') {
                // C# is charging via saved card - stay on loading screen
                document.getElementById('formSection').style.display = 'none';
                document.getElementById('loadingPayment').classList.add('active');
            }
            else if (msg.action === 'cardDeleted') {
                useOtherCard();
            }
        });'''

count = content_n.count(old)
print(f"Step 1 - Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    print("Step 1 OK")
else:
    print("Step 1 NOT FOUND - aborting")
    exit()

old2 = '''        function deleteCard() {
            window.chrome.webview.postMessage({ action: 'deleteCard' });
            useOtherCard();
        }'''

new2 = '''        function deleteCard() {
            // Wait for C# to confirm deletion (via 'cardDeleted' message) before switching UI,
            // to avoid a race where the user pays again before Firebase is actually updated.
            window.chrome.webview.postMessage({ action: 'deleteCard' });
        }'''

count2 = content_n.count(old2)
print(f"Step 2 - Found {count2} matches")
if count2 == 1:
    content_n = content_n.replace(old2, new2, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("Step 2 OK - file saved")
else:
    print("Step 2 NOT FOUND - aborting, file NOT saved")
