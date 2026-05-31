content = open(r'.\src\services\userService.js', encoding='utf-8').read()

old = "    await update(userRef, updates);\n\n    return {\n      success: true,\n      message: 'User balance adjusted successfully',"
new = """    await update(userRef, updates);

    // Log admin charge to purchases
    const timeDiff = adjustments.timeSeconds || 0;
    const printsDiff = adjustments.prints || 0;
    if (timeDiff !== 0 || printsDiff !== 0) {
      const purchasesRef = ref(database, `organizations/${orgId}/purchases`);
      const newRef = push(purchasesRef);
      await set(newRef, {
        userId,
        type: 'admin_charge',
        status: 'completed',
        createdAt: new Date().toISOString(),
        timeSeconds: timeDiff,
        prints: printsDiff,
        amount: 0,
        note: 'טעינת מפעיל',
      });
    }

    return {
      success: true,
      message: 'User balance adjusted successfully',"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\services\userService.js', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
