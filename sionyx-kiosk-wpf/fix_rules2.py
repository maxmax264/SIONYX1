import json
with open(r'C:\Users\user\Desktop\SIONYX-clean\database.rules.json', encoding='utf-8') as f:
    rules = json.load(f)

rules['rules']['system'] = {
    'update': {
        '.read': True,
        '.write': False
    }
}

with open(r'C:\Users\user\Desktop\SIONYX-clean\database.rules.json', 'w', encoding='utf-8') as f:
    json.dump(rules, f, indent=2, ensure_ascii=False)
print('OK')
