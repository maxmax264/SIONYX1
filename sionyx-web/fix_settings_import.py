content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\SettingsPage.jsx', encoding='utf-8').read()
old = "import PricingSettings from '../components/settings/PricingSettings';"
new = """import PricingSettings from '../components/settings/PricingSettings';
import PhoneVerificationSettings from '../components/settings/PhoneVerificationSettings';"""
count = content.count(old)
print(f"import match: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\src\pages\SettingsPage.jsx', 'w', encoding='utf-8').write(content)
    print('import OK')
else:
    print('NOT FOUND')
