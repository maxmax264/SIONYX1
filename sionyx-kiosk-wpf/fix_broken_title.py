path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

old1 = 'Title="\u05f3\u201d\u05f3\u2022\u05f3\u201d\u05f3\xa2\u05f3\u2022\u05f3\u00d7" FlowDirection="RightToLeft">'
new1 = 'Title="\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea" FlowDirection="RightToLeft">'

# נחפש ונחליף לפי הטקסט המדויק שראינו
broken_title = content[content.find('Title='):content.find('Title=')+50]
print(repr(broken_title))

# החלפה לפי מה שבפועל בקובץ
content2 = content.replace(
    'Title="\u05f3\u201d\u05f3\u2022\u05f3\u201d\u05f3\xa2\u05f3\u2022\u05f3\xd7"',
    'Title="\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea"'
)

# גם TextBlock הראשי
content2 = content2.replace(
    'Text="\u05f3\u201d\u05f3\u2022\u05f3\u201d\u05f3\xa2\u05f3\u2022\u05f3\xd7"',
    'Text="\u05d4\u05d5\u05d3\u05e2\u05d5\u05ea"'
)

if content2 != content:
    open(path, 'w', encoding='utf-8').write(content2)
    print("OK - fixed")
else:
    # נסה גישה אחרת - החלף לפי bytes
    raw = open(path, 'rb').read()
    print("First 500 bytes around Title:")
    idx = raw.find(b'Title=')
    print(repr(raw[idx:idx+60]))
