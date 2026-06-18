import re, sys

path = r'.\installer\Package.wxs'
content = open(path, encoding='utf-8').read()

def resolve_take_remote(text):
    pattern = re.compile(
        r'<<<<<<< HEAD.*?=======\n(.*?)>>>>>>> [0-9a-f]+\n',
        re.DOTALL
    )
    return pattern.sub(lambda m: m.group(1), text)

resolved = resolve_take_remote(content)

count_before = content.count('<<<<<<<')
count_after = resolved.count('<<<<<<<')
print(f"Conflicts before: {count_before}, after: {count_after}")

if count_after == 0:
    open(path, 'w', encoding='utf-8').write(resolved)
    print("OK")
else:
    print("ERROR")
    sys.exit(1)
