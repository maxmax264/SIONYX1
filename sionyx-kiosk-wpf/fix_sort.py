content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', encoding='utf-8').read()

old1 = """      const merged = [...msgs, ...replies].sort(
        (a, b) => dayjs(a.timestamp).unix() - dayjs(b.timestamp).unix()
      );
      setUserMessages(merged);"""

new1 = """      const merged = [...msgs, ...replies].sort(
        (a, b) => (a.timestamp || 0) - (b.timestamp || 0)
      );
      setUserMessages(merged);"""

count1 = content.count(old1)
print(f"Found sort1: {count1}")
if count1 >= 1:
    content = content.replace(old1, new1)
    print('Fixed')

open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\MessagesPage.jsx', 'w', encoding='utf-8').write(content)
print('Done')
