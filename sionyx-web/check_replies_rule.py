content = open(r'C:\Users\user\Desktop\SIONYX-clean\database.rules.json', encoding='utf-8').read()
idx = content.find('"userReplies"')
if idx == -1:
    print("NOT FOUND - need to add")
else:
    print(content[idx:idx+300])
