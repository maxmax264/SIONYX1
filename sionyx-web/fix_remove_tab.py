c = open(r'.\src\pages\SettingsPage.jsx', encoding='utf-8').read()
old = "import AuthDesignSettings from '../components/settings/AuthDesignSettings';\n"
c = c.replace(old, '', 1)
old2 = """    },
    {
      key: 'authdesign',
      label: (
        <span>
          <SettingOutlined />
          {' '}עיצוב דשבורד
        </span>
      ),
      children: <AuthDesignSettings />,"""
count = c.count(old2)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old2, '', 1)
    open(r'.\src\pages\SettingsPage.jsx', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
