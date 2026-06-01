f=open(r'.\src\components\settings\KioskBackgroundSettings.jsx', encoding='utf-8')
c=f.read()
f.close()

old='''      <Alert
        type="info"
        showIcon
        message="איך להגדיר תמונת רקע לקיוסק?"
        description={
          <Space direction="vertical" size={4}>
            <Text><strong>דרך 1 - העלאת קובץ:</strong> לחץ "בחר תמונה" ובחר קובץ מהמחשב. לא מומלץ עם נטפרי.</Text>
            <Text><strong>דרך 2 - קישור חיצוני (מומלץ עם נטפרי):</strong></Text>
            <Text>1. העלה תמונה ל-<a href="https://postimages.org" target="_blank" rel="noreferrer">postimages.org</a> או <a href="https://imgur.com" target="_blank" rel="noreferrer">imgur.com</a></Text>
            <Text>2. העתק את ה-<strong>Direct link</strong> - חייב להסתיים ב-.jpg או .png</Text>
            <Text>3. הדבק בשדה "הדבק קישור" ולחץ שמור</Text>
            <Text type="secondary">לדוגמה: https://i.postimg.cc/xxxxx/image.jpg</Text>
          </Space>
        }
        style={{ marginBottom: 8 }}
      />'''

new='''      <Alert
        type="info"
        showIcon
        message="איך להגדיר תמונת רקע לקיוסק?"
        description={
          <Space direction="vertical" size={4}>
            <Text>1. היכנס לאתר <a href="https://postimages.org" target="_blank" rel="noreferrer">postimages.org</a> והירשם — כדי שהתמונות ישמרו לצמיתות</Text>
            <Text>2. העלה את התמונה הרצויה</Text>
            <Text>3. לחץ על <strong>Direct link</strong> והעתק את הקישור</Text>
            <Text>4. הדבק את הקישור בשדה למטה ולחץ <strong>שמור</strong></Text>
            <Text type="secondary">הקישור צריך להסתיים ב־ .jpg / .png / .webp</Text>
          </Space>
        }
        style={{ marginBottom: 8 }}
      />'''

assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\components\settings\KioskBackgroundSettings.jsx','w',encoding='utf-8').write(c)
print("OK")
