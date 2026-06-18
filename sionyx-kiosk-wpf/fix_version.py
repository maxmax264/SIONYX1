import json

path = r'.\version.json'
data = {
    "version": "3.4.156",
    "major": 3,
    "minor": 4,
    "patch": 156,
    "buildNumber": 260,
    "lastBuildDate": "2026-06-17T22:05:16.6149816+03:00"
}
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
print("OK")
