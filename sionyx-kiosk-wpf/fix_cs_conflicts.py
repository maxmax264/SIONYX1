import re, sys

path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs'
content = open(path, encoding='utf-8').read()

# בלוק 1: מחיקת _supervisorDisplayName (לוקחים remote = כלום)
old1 = '<<<<<<< HEAD\n    private string _supervisorDisplayName = "\u05e4\u05d9\u05e7\u05d5\u05d7";\n=======\n>>>>>>> d82e28093333a1ccd75a5882946789702310029a\n'
# נשתמש בregex כי הטקסט העברי עלול להיות מקולקל

def resolve_take_remote(text):
    pattern = re.compile(
        r'<<<<<<< HEAD.*?=======\n(.*?)>>>>>>> [0-9a-f]+\n',
        re.DOTALL
    )
    return pattern.sub(lambda m: m.group(1), text)

resolved = resolve_take_remote(content)

count_before = content.count('<<<<<<<')
count_after = resolved.count('<<<<<<<')
print(f"Conflict markers before: {count_before}")
print(f"Conflict markers after:  {count_after}")

if count_after == 0:
    open(path, 'w', encoding='utf-8').write(resolved)
    print("OK")
else:
    print("ERROR - conflicts remain")
    sys.exit(1)
