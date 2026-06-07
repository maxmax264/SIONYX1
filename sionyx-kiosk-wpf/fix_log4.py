content = open(r'.\installer\CustomActions\KioskSetupActions.cs', encoding='utf-8').read()
idx = content.find('[DBG] ntuser.dat path')
if idx == -1:
    print('NOT FOUND')
else:
    start = content.rfind('\n', 0, idx) + 1
    end = content.find('\n', content.find('[DBG] Profile dir exists', idx)) + 1
    bad = content[start:end]
    print(f"Removing {len(bad)} chars")
    good = '            session.Log("[DBG] Profile check running");\n'
    content = content[:start] + good + content[end:]
    open(r'.\installer\CustomActions\KioskSetupActions.cs', 'w', encoding='utf-8').write(content)
    print('OK')
