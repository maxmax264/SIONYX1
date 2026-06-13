content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

old = "                if (fromSupervisor) _supervisorMessages.Add(item);\n                else _adminMessages.Add(item);"
new = "                if (_deletedIds.Contains(id)) continue;\n                if (fromSupervisor) _supervisorMessages.Add(item);\n                else _adminMessages.Add(item);"

count = content.count(old)
print(f"Found messages filter: {count}")
if count == 1:
    content = content.replace(old, new, 1)

# Filter replies too
old2 = "                    if (isSupervisorReply) _supervisorMessages.Add(replyItem);\n                    else _adminMessages.Add(replyItem);"
new2 = "                    if (_deletedIds.Contains(prop.Name)) continue;\n                    if (isSupervisorReply) _supervisorMessages.Add(replyItem);\n                    else _adminMessages.Add(replyItem);"

count2 = content.count(old2)
print(f"Found replies filter: {count2}")
if count2 == 1:
    content = content.replace(old2, new2, 1)

open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
print('Done')
