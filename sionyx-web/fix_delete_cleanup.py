content = open(r'.\src\services\userService.js', encoding='utf-8').read()

old = '''};
  } catch (error) {
    logger.error('Error deleting user:', error);
    const errorMessage = error.message || 'שגיאה במחיקת המשתמש';
    return { success: false, error: errorMessage };
  }
};'''

new = '};'

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\services\userService.js', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
