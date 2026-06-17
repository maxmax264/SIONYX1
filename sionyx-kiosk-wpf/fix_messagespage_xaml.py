import re, sys

path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

original = content

# פונקציה שמקבלת קובץ עם conflict markers ומחזירה את הגרסה של הרימוט (======= עד >>>>>>>)
def resolve_take_remote(text):
    pattern = re.compile(
        r'<<<<<<< HEAD.*?=======\n(.*?)>>>>>>> [0-9a-f]+\n',
        re.DOTALL
    )
    result = pattern.sub(lambda m: m.group(1), text)
    return result

resolved = resolve_take_remote(content)

count_before = content.count('<<<<<<<')
count_after = resolved.count('<<<<<<<')
print(f"Conflict markers before: {count_before}")
print(f"Conflict markers after: {count_after}")

if count_after == 0:
    open(path, 'w', encoding='utf-8').write(resolved)
    print("OK - all conflicts resolved (took remote for all)")
else:
    print("ERROR - some conflicts remain, not writing")
    sys.exit(1)
