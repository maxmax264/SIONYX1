f=open(r'.\src\pages\ReportsPage.jsx', encoding='utf-8')
c=f.read()
f.close()

old = """    },
    {
      title: '\u05e1\u05db\u05d5\u05dd',
      dataIndex: 'amount',
      key"""

new = """    },
    {
      title: '\u05d3\u05e7\u05d5\u05ea',
      dataIndex: 'timeSeconds',
      key: 'timeSeconds',
      render: v => {
        if (!v && v !== 0) return '\u2014';
        const mins = Math.round(Math.abs(v) / 60);
        return v >= 0 ? `+${mins} \u05d3\u05e7` : `-${mins} \u05d3\u05e7`;
      },
    },
    {
      title: '\u05e1\u05db\u05d5\u05dd',
      dataIndex: 'amount',
      key"""

count = c.count(old)
print(f"Found {count} matches")
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\pages\ReportsPage.jsx', 'w', encoding='utf-8').write(c)
    print("OK")
else:
    print("NOT FOUND")
