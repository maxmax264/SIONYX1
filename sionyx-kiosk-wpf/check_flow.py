path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
raw = open(path, 'rb').read()

old = b'Title="\xe2\x80\x9d\xe2\x80\xa2\xe2\x80\x9c\xc2\xa2\xe2\x80\xa2\xc3\x97" FlowDirection="RightToLeft">'
new = b'Title="\xd7\x94\xd7\x95\xd7\x93\xd7\xa2\xd7\x95\xd7\xaa">'

# נסתכל מה יש בפועל
idx = raw.find(b'FlowDirection="RightToLeft"')
print(repr(raw[idx-20:idx+40]))
