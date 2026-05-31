content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

old = "  CrownOutlined,\n} from '@ant-design/icons';"
new = "  CrownOutlined,\n  HistoryOutlined,\n  PrinterOutlined,\n  ReloadOutlined,\n} from '@ant-design/icons';"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
