path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = "            else if (msg.action === 'showTimeout') {\n                showTimeout();\n            }\n        });"

new = "            else if (msg.action === 'showTimeout') {\n                showTimeout();\n            }\n            else if (msg.action === 'savedCardCharging') {\n                // C# is charging via saved card - stay on loading screen\n                document.getElementById('formSection').style.display = 'none';\n                document.getElementById('loadingPayment').classList.add('active');\n            }\n        });"

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    result = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(result)
    print('OK')
else:
    print('NOT FOUND')
