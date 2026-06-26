path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = "<input type=\"checkbox\" id=\"saveCardCheck\" style=\"width:18px; height:18px; cursor:pointer; accent-color:#6366F1;\">"

new = "<input type=\"checkbox\" id=\"saveCardCheck\" style=\"width:18px; height:18px; cursor:pointer; accent-color:#6366F1;\" onchange=\"onSaveCardToggle()\">"

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
