path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
raw = open(path, 'rb').read()

broken_title = b'Title="\xd7\xb3\xe2\x80\x9d\xd7\xb3\xe2\x80\xa2\xd7\xb3\xe2\x80\x9c\xd7\xb3\xc2\xa2\xd7\xb3\xe2\x80\xa2\xd7\xb3\xc3\x97"'
broken_text  = b'Text="\xd7\xb3\xe2\x80\x9d\xd7\xb3\xe2\x80\xa2\xd7\xb3\xe2\x80\x9c\xd7\xb3\xc2\xa2\xd7\xb3\xe2\x80\xa2\xd7\xb3\xc3\x97"'

correct_title = 'Title="\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea"'.encode('utf-8')
correct_text  = 'Text="\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea"'.encode('utf-8')

print(f"Title matches: {raw.count(broken_title)}")
print(f"Text matches:  {raw.count(broken_text)}")

raw2 = raw.replace(broken_title, correct_title)
raw2 = raw2.replace(broken_text, correct_text)

open(path, 'wb').write(raw2)
print("OK")
