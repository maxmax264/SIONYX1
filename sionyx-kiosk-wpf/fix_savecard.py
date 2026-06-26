content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', encoding='utf-8').read()

old = '''        function initNedarimIframe() {
            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&
                           document.getElementById('saveCardCheck').checked;
            var url = "https://matara.pro/nedarimplus/iframe?language=he";
            if (saveCard) {
                url += "&Tokef=Hide&CVV=Hide";
            }
            document.getElementById('NedarimFrame').src = url;
        }'''

new = '''        function initNedarimIframe() {
            var url = "https://matara.pro/nedarimplus/iframe?language=he";
            document.getElementById('NedarimFrame').src = url;
        }'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    # Fix onPurchaseCreated to use Ragil + SaveCard=1
    old2 = '''            var paymentType = saveCard ? 'CreateToken' : 'Ragil';
            var apiValidToUse = saveCard && CONFIG.saveCardApiValid ? CONFIG.saveCardApiValid : CONFIG.apiValid;
            postToNedarim({
                'Name': 'FinishTransaction2',
                'Value': {
                    'Mosad': CONFIG.mosadId,
                    'ApiValid': apiValidToUse,
                    'PaymentType': paymentType,'''
    new2 = '''            var apiValidToUse = saveCard && CONFIG.saveCardApiValid ? CONFIG.saveCardApiValid : CONFIG.apiValid;
            postToNedarim({
                'Name': 'FinishTransaction2',
                'Value': {
                    'Mosad': CONFIG.mosadId,
                    'ApiValid': apiValidToUse,
                    'PaymentType': 'Ragil',
                    'SaveCard': saveCard ? '1' : '0','''
    content = content.replace(old2, new2, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
