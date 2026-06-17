content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''        [CustomAction]
        public static ActionResult LaunchKiosk(Session session)
        {
            session.Log("=== LaunchKiosk: START ===");
            try
            {
                string installDir = session.CustomActionData["INSTALLDIR"];'''

new = '''        [CustomAction]
        public static ActionResult LaunchKiosk(Session session)
        {
            session.Log("=== LaunchKiosk: START ===");
            try
            {
                // In immediate mode, read directly from session properties
                string installDir = session["INSTALLFOLDER"] ?? session.CustomActionData["INSTALLDIR"] ?? @"C:\Program Files\SIONYX\";'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print("DONE")
else:
    print("NOT FOUND")
