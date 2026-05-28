content = open(r'.\src\pages\LandingPage.jsx', encoding='utf-8').read()

old = 'התחל עכשיו - חינם'
new = 'התחל עכשיו'

count = content.count(old)
print(f"Found {count} matches")
content = content.replace(old, new)
open(r'.\src\pages\LandingPage.jsx', 'w', encoding='utf-8').write(content)
print('OK')
