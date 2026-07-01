path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''        function handleTransactionResponse(response) {
            document.getElementById('loadingPayment').classList.remove('active');
            if (response.Status === 'Error') {
                document.getElementById('formSection').style.display = 'flex';
                showError(response.Message || 'התשלום נכשל. נסה שוב.');
            } else {
                document.getElementById('processingMessage').classList.add('active');
                window.chrome.webview.postMessage({
                    action: 'paymentSuccess',
                    response: response
                });
            }
        }'''

new = '''        function handleTransactionResponse(response) {
            document.getElementById('loadingPayment').classList.remove('active');
            if (response.Status === 'Error') {
                document.getElementById('formSection').style.display = 'flex';
                showError(response.Message || 'התשלום נכשל. נסה שוב.');
            } else {
                document.getElementById('processingMessage').classList.add('active');
                // Nedarim hides the expiry field when creating a token, so it never comes back
                // in the response - we capture what the user typed in our own field instead.
                var expiryInput = document.getElementById('saveCardExpiryInput');
                var enteredExpiry = expiryInput ? expiryInput.value.trim() : '';
                window.chrome.webview.postMessage({
                    action: 'paymentSuccess',
                    response: response,
                    enteredExpiry: enteredExpiry
                });
            }
        }'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
