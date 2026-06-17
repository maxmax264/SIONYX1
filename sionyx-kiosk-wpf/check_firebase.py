content = open(r'.\src\SionyxKiosk\Infrastructure\FirebaseClient.cs', encoding='utf-8').read()
idx = content.find('DbGetAsync')
print(content[idx:idx+300])
