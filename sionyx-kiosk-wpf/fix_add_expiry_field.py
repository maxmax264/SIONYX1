path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = '''                <div id="saveCardCheckBox" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer; font-size:15px; font-weight:600; color:#0F172A;">
                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;" onchange="onSaveCardToggle()">
                        שמור כרטיס לרכישות הבאות
                    </label>
                    <p style="margin:6px 0 0 28px; font-size:12px; color:#94A3B8;">הכרטיס נשמר בצורה מאובטחת אצל נדרים פלוס. בפעם הבאה תזדקק להזין רק CVV.</p>
                </div>'''

new = '''                <div id="saveCardCheckBox" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer; font-size:15px; font-weight:600; color:#0F172A;">
                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;" onchange="onSaveCardToggle()">
                        שמור כרטיס לרכישות הבאות
                    </label>
                    <p style="margin:6px 0 0 28px; font-size:12px; color:#94A3B8;">הכרטיס נשמר בצורה מאובטחת אצל נדרים פלוס.</p>
                    <div id="saveCardExpiryRow" style="display:none; margin:10px 0 0 28px; align-items:center; gap:10px;">
                        <span style="font-size:13px; font-weight:600; color:#0F172A;">תוקף הכרטיס:</span>
                        <input type="text" id="saveCardExpiryInput" maxlength="5" placeholder="MM/YY" inputmode="numeric" autocomplete="off"
                            style="width:90px; padding:8px 12px; border:2px solid #E2E8F0; border-radius:8px; font-size:15px; font-weight:600; color:#0F172A; background:white; outline:none; text-align:center; direction:ltr; font-family:'Courier New',monospace;">
                    </div>
                </div>'''

count = content_n.count(old)
print(f"Found {count} matches")
if count == 1:
    content_n = content_n.replace(old, new, 1)
    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print("OK - file saved")
else:
    print("NOT FOUND - file NOT saved")
