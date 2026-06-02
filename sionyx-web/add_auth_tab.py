f=open(r'.\src\pages\SettingsPage.jsx', encoding='utf-8')
c=f.read()
f.close()

old='import { SettingOutlined, DollarOutlined, DownloadOutlined, PictureOutlined } from "@ant-design/icons";'
new='import { SettingOutlined, DollarOutlined, DownloadOutlined, PictureOutlined, FormatPainterOutlined } from "@ant-design/icons";'
c=c.replace(old,new,1)

old="import KioskBackgroundSettings from '../components/settings/KioskBackgroundSettings';"
new="""import KioskBackgroundSettings from '../components/settings/KioskBackgroundSettings';
import AuthDesignSettings from '../components/settings/AuthDesignSettings';"""
assert c.count(old)==1
c=c.replace(old,new,1)

old="    {\n      key: 'downloads',"
new="""    {
      key: 'authdesign',
      label: (
        <span>
          <FormatPainterOutlined />
          {' '}עיצוב מסך כניסה
        </span>
      ),
      children: <AuthDesignSettings />,
    },
    {
      key: 'downloads',"""
assert c.count(old)==1
c=c.replace(old,new,1)

open(r'.\src\pages\SettingsPage.jsx','w',encoding='utf-8').write(c)
print("OK")
