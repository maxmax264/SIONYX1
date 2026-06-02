content = open(r'.\src\pages\SettingsPage.jsx', encoding='utf-8').read()
old = "import DownloadsSettings from '../components/settings/DownloadsSettings';"
new = "import DownloadsSettings from '../components/settings/DownloadsSettings';\nimport AuthDesignSettings from '../components/settings/AuthDesignSettings';"
count = content.count(old)
print(f'Found {count} matches')
if count == 1:
    content = content.replace(old, new, 1)
    old2 = "      children: <DownloadsSettings />,"
    new2 = "      children: <DownloadsSettings />,\n    },\n    {\n      key: 'authdesign',\n      label: (\n        <span>\n          <SettingOutlined />\n          {' '}עיצוב דשבורד\n        </span>\n      ),\n      children: <AuthDesignSettings />,"
    content = content.replace(old2, new2, 1)
    open(r'.\src\pages\SettingsPage.jsx', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
