import json
with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\new_rules.json', encoding='utf-8') as f:
    rules = json.load(f)

settings = rules['rules']['organizations']['$orgId']['metadata']['settings']
settings['adminExitPassword'] = {'.read': True}

with open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\new_rules.json', 'w', encoding='utf-8') as f:
    json.dump(rules, f, indent=2, ensure_ascii=False)
print('OK')
