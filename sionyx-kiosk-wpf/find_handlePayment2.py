path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

import re
m = re.search(r'(        function handlePayment\(\) \{.*?        \})', content_n, re.DOTALL)
if m:
    print(repr(m.group(1)))
else:
    print("NOT FOUND")
