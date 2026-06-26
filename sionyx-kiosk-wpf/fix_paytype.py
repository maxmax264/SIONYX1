content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = "            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&\n                           document.getElementById('saveCardCheck').checked;\n            var apiValidToUse = saveCard && CONFIG.saveCardApiValid ? CONFIG.saveCardApiValid : CONFIG.apiValid;\n            postToNedarim({\n                'Name': 'FinishTransaction2',\n                'Value': {\n                    'Mosad': CONFIG.mosadId,\n                    'ApiValid': apiValidToUse,\n                    'PaymentType': 'Ragil',\n                    'SaveCard': saveCard ? '1' : '0',"

new = "            var saveCard = CONFIG.saveCardEnabled && document.getElementById('saveCardCheck') &&\n                           document.getElementById('saveCardCheck').checked;\n            var apiValidToUse = saveCard && CONFIG.saveCardApiValid ? CONFIG.saveCardApiValid : CONFIG.apiValid;\n            var paymentType = saveCard ? 'CreateToken' : 'Ragil';\n            postToNedarim({\n                'Name': 'FinishTransaction2',\n                'Value': {\n                    'Mosad': CONFIG.mosadId,\n                    'ApiValid': apiValidToUse,\n                    'PaymentType': paymentType,"

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html', 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
    idx = content_n.find("'PaymentType': 'Ragil'")
    print(repr(content_n[idx-200:idx+50]))
