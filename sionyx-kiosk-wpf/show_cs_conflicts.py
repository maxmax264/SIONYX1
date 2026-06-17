import re, sys

path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs'
content = open(path, encoding='utf-8').read()

# הצג את האזור סביב ה-conflict
lines = content.splitlines()
for i, line in enumerate(lines, 1):
    if '<<<<<<<' in line or '=======' in line or '>>>>>>>' in line:
        start = max(0, i-3)
        end = min(len(lines), i+3)
        for j in range(start, end):
            print(f"{j+1}: {lines[j]}")
        print("---")
