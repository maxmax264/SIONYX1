content = open(r'.\src\SionyxKiosk\Services\FirebaseClient.cs', encoding='utf-8').read()
idx = content.find('DbDeleteAsync')
if idx == -1:
    print('NOT FOUND - need to add')
else:
    print(content[idx-50:idx+200])
