path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

count = content_n.count("if (row) row.style.display = checked ? 'flex' : 'none';")
print(f"Step 1 (toggle) - Found {count} matches (should already be flex)")

count2 = content_n.count("if (row) row.style.display = 'flex';")
print(f"Step 2 (initial show) - Found {count2} matches (should already be flex)")
