content = open(r'.\src\pages\UsersPage.jsx', encoding='utf-8').read()

old = "        {selectedUser && (\n          <Tabs activeKey={userHistoryTab}"
new = "        <div style={{ marginTop: 8 }}>\n        {selectedUser && (\n          <Tabs activeKey={userHistoryTab}"

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)

old2 = "          />\n        )}\n      </Drawer>"
new2 = "          />\n        )}\n        </div>\n      </Drawer>"
count2 = content.count(old2)
print(f"Found2 {count2} matches")
if count2 == 1:
    content = content.replace(old2, new2, 1)
    open(r'.\src\pages\UsersPage.jsx', 'w', encoding='utf-8').write(content)
    print("OK")
