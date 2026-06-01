f = open(r'database.rules.json', encoding='utf-8')
c = f.read()
f.close()
import re
for m in re.finditer(r'"metadata"', c):
    print(m.start(), repr(c[m.start()-50:m.start()+100]))
    print("---")
