content = open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8').read()

old = "  Statistic,\n} from 'antd';"
new = "  Statistic,\n  Tabs,\n  Input,\n} from 'antd';"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
