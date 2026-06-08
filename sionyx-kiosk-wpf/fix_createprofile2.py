import re

path = r'.\installer\CustomActions\KioskSetupActions.cs'
content = open(path, encoding='utf-8').read()

old = '''                session.Log("[INFO] Skipping CreateProfile — Windows will create profile on first logon via AutoLogon");'''

new = '''                // Create the profile via Win32 API so Windows does not show "Getting Windows ready"
                var profilePathBuilder = new StringBuilder(260);
                string userSid = GetUserSid(KioskUsername);
                if (userSid != null)
                {
                    int cpResult = CreateProfile(userSid, KioskUsername, profilePathBuilder, (uint)profilePathBuilder.Capacity);
                    session.Log($"[INFO] CreateProfile API result: {cpResult} path: {profilePathBuilder}");
                }
                else
                {
                    session.Log("[WARN] Could not get SID for CreateProfile — skipping API call");
                }'''

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
