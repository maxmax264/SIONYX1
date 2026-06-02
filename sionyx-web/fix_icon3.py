f=open(r'.\src\pages\SettingsPage.jsx', encoding='utf-8')
c=f.read()
f.close()

old="import { SettingOutlined, DollarOutlined, DownloadOutlined, PictureOutlined } from '@ant-design/icons';"
new="import { SettingOutlined, DollarOutlined, DownloadOutlined, PictureOutlined, BgColorsOutlined } from '@ant-design/icons';"
assert c.count(old)==1
c=c.replace(old,new,1)

old="          <FormatPainterOutlined />"
new="          <BgColorsOutlined />"
c=c.replace(old,new,1)

open(r'.\src\pages\SettingsPage.jsx','w',encoding='utf-8').write(c)
print("OK")
