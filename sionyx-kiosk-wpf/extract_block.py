path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

# הבלוק המלא של ה-checkbox במקומו הנוכחי
checkbox_block = """                <div id="saveCardCheckBox" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">
                    <label style="display:flex; align-items:center; gap:10px; cursor:pointer; font-size:15px; font-weight:600; color:#0F172A;">
                        <input type="checkbox" id="saveCardCheck" style="width:18px; height:18px; cursor:pointer; accent-color:#6366F1;" onchange="onSaveCardToggle()">
"""

# מוצאים את כל הבלוק עד לסגירת ה-div (3 שורות נוספות בערך)
start_idx = content_n.find(checkbox_block)
if start_idx == -1:
    print("START NOT FOUND")
else:
    # מחפשים את הסגירה </div> הבאה אחרי תחילת הבלוק
    end_marker = "</div>"
    search_from = start_idx + len(checkbox_block)
    end_idx = content_n.find(end_marker, search_from) + len(end_marker)
    full_block = content_n[start_idx:end_idx]
    print("=== EXTRACTED BLOCK ===")
    print(full_block)
    print("=== END BLOCK ===")
