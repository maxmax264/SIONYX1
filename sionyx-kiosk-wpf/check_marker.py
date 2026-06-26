path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

old = """                <div id="saveCardCheckBox" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer; font-size:15px; font-weight:600; color:#0F172A;">
                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;" onchange="onSaveCardToggle()">
"""

count = content_n.count(old)
print(f"Found start marker: {count} matches")
