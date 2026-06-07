content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
old = '            session.Log("[DBG] ntuser.dat path: C:\\\\Users\\\\" + KioskUsername + "\\\\ntuser.dat");\n            session.Log("[DBG] ntuser.dat exists: " + File.Exists(@"C:\\\\Users\\\\" + KioskUsername + @"\\\\ntuser.dat"));\n            session.Log("[DBG] Profile dir exists: " + Directory.Exists(@"C:\\\\Users\\\\" + KioskUsername));'
idx = content.find('[DBG] ntuser.dat path')
print(repr(content[idx-20:idx+300]))
