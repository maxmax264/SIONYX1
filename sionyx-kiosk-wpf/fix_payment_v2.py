path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'

html = open(path+'.backup', encoding='utf-8').read()

# החלף את כל הקטע של saveCardContainer הישן
old = """                <div id="saveCardContainer" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer; font-size:15px; font-weight:600; color:#0F172A;">
                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;" onchange="initNedarimIframe()">
                        \u05e9\u05de\u05d5\u05e8 \u05db\u05e8\u05d8\u05d9\u05e1 \u05dc\u05e8\u05db\u05d9\u05e9\u05d5\u05ea \u05d4\u05d1\u05d0\u05d5\u05ea
                    </label>
                    <p style="margin:6px 0 0 28px; font-size:12px; color:#94A3B8;">\u05d4\u05db\u05e8\u05d8\u05d9\u05e1 \u05e0\u05e9\u05de\u05e8 \u05d1\u05e6\u05d5\u05e8\u05d4 \u05de\u05d0\u05d5\u05d1\u05d8\u05d7\u05ea \u05d0\u05e6\u05dc \u05e0\u05d3\u05e8\u05d9\u05dd \u05e4\u05dc\u05d5\u05e1. \u05d1\u05e4\u05e2\u05dd \u05d4\u05d1\u05d0\u05d4 \u05ea\u05d6\u05d3\u05e7\u05e7 \u05dc\u05d4\u05d6\u05d9\u05df \u05e8\u05e7 CVV.</p>
                </div>"""

new = """                <div id="saveCardCheckBox" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer; font-size:15px; font-weight:600; color:#0F172A;">
                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;">
                        \u05e9\u05de\u05d5\u05e8 \u05db\u05e8\u05d8\u05d9\u05e1 \u05dc\u05e8\u05db\u05d9\u05e9\u05d5\u05ea \u05d4\u05d1\u05d0\u05d5\u05ea
                    </label>
                    <p style="margin:6px 0 0 28px; font-size:12px; color:#94A3B8;">\u05d4\u05db\u05e8\u05d8\u05d9\u05e1 \u05e0\u05e9\u05de\u05e8 \u05d1\u05e6\u05d5\u05e8\u05d4 \u05de\u05d0\u05d5\u05d1\u05d8\u05d7\u05ea \u05d0\u05e6\u05dc \u05e0\u05d3\u05e8\u05d9\u05dd \u05e4\u05dc\u05d5\u05e1. \u05d1\u05e4\u05e2\u05dd \u05d4\u05d1\u05d0\u05d4 \u05ea\u05d6\u05d3\u05e7\u05e7 \u05dc\u05d4\u05d6\u05d9\u05df \u05e8\u05e7 CVV.</p>
                </div>"""

count = html.count(old)
print(f"saveCardContainer: {count} matches")
if count == 1:
    html = html.replace(old, new, 1)
    print("replaced OK")

open(path, 'w', encoding='utf-8').write(html)
print("File written OK")
