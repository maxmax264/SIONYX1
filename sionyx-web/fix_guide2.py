f=open(r'.\src\components\settings\KioskBackgroundSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='''            <Text>1. היכנס לאתר <a href="https://postimages.org" target="_blank" rel="noreferrer">postimages.org</a> והירשם — כדי שהתמונות ישמרו לצמיתות</Text>
            <Text>2. העלה את התמונה הרצויה</Text>
            <Text>3. לחץ על <strong>Direct link</strong> והעתק את הקישור</Text>
            <Text>4. הדבק את הקישור בשדה למטה ולחץ <strong>שמור</strong></Text>
            <Text type="secondary">הקישור צריך להסתיים ב־ .jpg / .png / .webp</Text>'''

new='''            <Text>1. היכנס לאתר <a href="https://postimages.org" target="_blank" rel="noreferrer">postimages.org</a> והירשם — כדי שהתמונות ישמרו לצמיתות</Text>
            <Text>2. העלה את התמונה הרצויה</Text>
            <Text>3. מהרשימה שמופיעה העתק את השורה <strong>קישור ישיר</strong></Text>
            <Text type="secondary">הקישור נראה כך: https://i.postimg.cc/xxxxx/image.jpg</Text>
            <Text>4. הדבק את הקישור בשדה למטה ולחץ <strong>שמור</strong></Text>'''

assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\components\settings\KioskBackgroundSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
