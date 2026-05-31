content = open(r'.\src\components\settings\KioskBackgroundSettings.jsx', encoding='utf-8').read()

replacements = [
    ("\\u05ea\\u05de\\u05d5\\u05e0\\u05ea \\u05e8\\u05e7\\u05e2 \\u05d4\\u05d5\\u05e4\\u05e2\\u05dc\\u05d4", "\u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2 \u05d4\u05d5\u05e4\u05e2\u05dc\u05d4"),
    ("\\u05ea\\u05de\\u05d5\\u05e0\\u05ea \\u05e8\\u05e7\\u05e2 \\u05d1\\u05d5\\u05d8\\u05dc\\u05d4", "\u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2 \u05d1\u05d5\u05d8\u05dc\u05d4"),
    ("\\u05d4\\u05db\\u05e0\\u05e1 \\u05e7\\u05d9\\u05e9\\u05d5\\u05e8", "\u05d4\u05db\u05e0\u05e1 \u05e7\u05d9\u05e9\u05d5\u05e8"),
    ("\\u05d2\\u05d5\\u05d3\\u05dc \\u05de\\u05e7\\u05e1\\u05d9\\u05de\\u05dc\\u05d9", "\u05d2\u05d5\u05d3\u05dc \u05de\u05e7\u05e1\u05d9\u05de\u05dc\u05d9"),
    ("\\u05ea\\u05de\\u05d5\\u05e0\\u05d4 \\u05e0\\u05e9\\u05de\\u05e8\\u05d4 \\u05d1\\u05d4\\u05e6\\u05dc\\u05d7\\u05d4", "\u05ea\u05de\u05d5\u05e0\u05d4 \u05e0\u05e9\u05de\u05e8\u05d4 \u05d1\u05d4\u05e6\u05dc\u05d7\u05d4"),
    ("\\u05e7\\u05d9\\u05e9\\u05d5\\u05e8 \\u05e0\\u05e9\\u05de\\u05e8", "\u05e7\u05d9\u05e9\u05d5\u05e8 \u05e0\u05e9\u05de\u05e8"),
    ("\\u05ea\\u05de\\u05d5\\u05e0\\u05d4 \\u05e0\\u05de\\u05d7\\u05e7\\u05d4", "\u05ea\u05de\u05d5\u05e0\u05d4 \u05e0\u05de\u05d7\u05e7\u05d4"),
    ("\\u05d4\u05e4\u05e2\u05dc \\u05ea\\u05de\\u05d5\\u05e0\\u05ea \\u05e8\\u05e7\\u05e2 \\u05dc\\u05e7\\u05d9\\u05d5\\u05e1\\u05e7", "\u05d4\u05e4\u05e2\u05dc \u05ea\u05de\u05d5\u05e0\u05ea \u05e8\u05e7\u05e2 \u05dc\u05e7\u05d9\u05d5\u05e1\u05e7"),
]

found = False
for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        found = True

if found:
    open(r'.\src\components\settings\KioskBackgroundSettings.jsx', 'w', encoding='utf-8').write(content)
    print("Fixed")
else:
    print("No unicode escapes found - checking...")
    import re
    matches = re.findall(r'\\u[0-9a-fA-F]{4}', content)
    print(f"Found {len(matches)} unicode escapes: {matches[:5]}")
