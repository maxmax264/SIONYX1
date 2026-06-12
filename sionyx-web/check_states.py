content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()
# Find all useState declarations
import re
for m in re.finditer(r'const \[(\w+), set\w+\] = useState', content):
    print(m.group(0))
