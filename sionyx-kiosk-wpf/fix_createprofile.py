content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()

old = '''                if (!File.Exists(Path.Combine(profilePath, "ntuser.dat")))
                {
                    string sid = GetUserSid(KioskUsername);
                    if (sid != null)
                    {
                        session.Log($"SID for {KioskUsername}: {sid}");

                        var pathBuf = new StringBuilder(260);
                        int hr = CreateProfile(sid, KioskUsername, pathBuf, 260);

                        if (hr == 0)
                            session.Log($"[OK] Profile created at: {pathBuf}");
                        else
                            session.Log($"[WARN] CreateProfile HRESULT: 0x{hr:X8} (profile may already exist)");
                    }
                    else
                    {
                        session.Log("[WARN] Could not resolve SID — profile will be created on first logon");
                    }
                }
                else
                {
                    session.Log("[INFO] Profile already exists");
                }'''

new = '''                session.Log("[INFO] Skipping CreateProfile — Windows will create profile on first logon via AutoLogon");'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
