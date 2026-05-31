f = open(r'.\src\owner\pages\OwnerDashboardPage.jsx', encoding='utf-8')
c = f.read()
f.close()

import re
matches = [(m.start(), c[m.start()-30:m.start()+50]) for m in re.finditer(r'sysSnap', c)]
for pos, ctx in matches:
    print(pos, repr(ctx))
    print("---")
