path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
html = open(path, encoding='utf-8').read()
html_n = html.replace('\r\n', '\n')

# 1. הוסף פאנל כרטיס שמור לפני iframe-card
old1 = '            <div class="iframe-card">'
new1 = '''            <!-- כרטיס שמור -->
            <div id="savedCardPanel" style="display:none; flex-direction:column; gap:14px; padding:20px; border:2px solid #E2E8F0; border-radius:14px; background:#FAFBFC; margin-bottom:18px; flex-shrink:0;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <div style="width:48px; height:48px; border-radius:12px; background:#EEF2FF; display:flex; align-items:center; justify-content:center; font-size:22px; flex-shrink:0;">&#x1F4B3;</div>
                    <div style="flex:1;">
                        <div style="font-size:15px; font-weight:700; color:#0F172A; margin-bottom:3px;">\u05db\u05e8\u05d8\u05d9\u05e1 \u05e9\u05de\u05d5\u05e8</div>
                        <div style="font-size:13px; color:#94A3B8; font-weight:500;" id="savedCardSub">\u05de\u05e1\u05ea\u05d9\u05d9\u05dd \u05d1-****</div>
                    </div>
                    <button onclick="deleteCard()" style="background:none; border:none; font-size:13px; font-weight:600; color:#EF4444; cursor:pointer; padding:4px 8px; border-radius:8px; font-family:inherit;">&#x1F5D1; \u05de\u05d7\u05e7 \u05db\u05e8\u05d8\u05d9\u05e1</button>
                </div>
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:14px; font-weight:700; color:#0F172A; flex-shrink:0;">CVV:</span>
                    <input type="password" id="savedCvvInput" maxlength="4" placeholder="&#x2022;&#x2022;&#x2022;" autocomplete="off" inputmode="numeric"
                        style="width:110px; padding:10px 14px; border:2px solid #E2E8F0; border-radius:10px; font-size:20px; font-weight:700; color:#0F172A; background:white; outline:none; letter-spacing:6px; text-align:center; direction:ltr; font-family:'Courier New',monospace;">
                    <span style="font-size:12px; color:#94A3B8; font-weight:500;">3-4 \u05e1\u05e4\u05e8\u05d5\u05ea \u05d1\u05d2\u05d1 \u05d4\u05db\u05e8\u05d8\u05d9\u05e1</span>
                </div>
                <button onclick="useOtherCard()" style="background:none; border:none; font-size:13px; font-weight:600; color:#6366F1; cursor:pointer; padding:0; font-family:inherit; text-decoration:underline; text-align:right;">\u05e9\u05dc\u05dd \u05e2\u05dd \u05db\u05e8\u05d8\u05d9\u05e1 \u05d0\u05d7\u05e8</button>
            </div>

            <div class="iframe-card" id="iframeSection">'''

count1 = html_n.count(old1)
print(f"iframe-card: {count1} matches")
if count1 == 1:
    html_n = html_n.replace(old1, new1, 1)

# 2. תקן את סגירת iframe-card (הוסף id)
old2 = '            <div class="iframe-card">'
count2 = html_n.count(old2)
print(f"remaining iframe-card: {count2} (should be 0)")

open(path, 'w', encoding='utf-8', newline='\r\n').write(html_n)
print("OK")
