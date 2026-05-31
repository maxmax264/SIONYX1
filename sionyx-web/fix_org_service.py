content = open(r'.\src\services\organizationService.js', encoding='utf-8').read()

old = """        purchasesRaw.push({
          amount: purchase.amount,
          createdAt: purchase.createdAt,
          status: purchase.status,
          packageName: pkgName,
          minutes: purchase.minutes,
        });"""

new = """        purchasesRaw.push({
          id: purchase.id,
          amount: purchase.amount,
          createdAt: purchase.createdAt,
          status: purchase.status,
          packageName: purchase.packageName || null,
          minutes: purchase.minutes,
          type: purchase.type,
          note: purchase.note,
          userId: purchase.userId,
          timeSeconds: purchase.timeSeconds,
          prints: purchase.prints,
        });"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\services\organizationService.js', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
