path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()
lines = content.splitlines()
for i, line in enumerate(lines, 1):
    if '\u05f3' in line or '\xd7\xb3' in line.encode('latin-1', errors='replace').decode('latin-1'):
        # בדוק אם יש תווים לא-עברים תקינים מעורבים עם \u05f3
        if any(ord(c) in range(0x05B0, 0x05FF) and c != '\u05f3' for c in line):
            pass
        if '\u05f3' in line:
            print(f"{i}: {line.strip()}")
