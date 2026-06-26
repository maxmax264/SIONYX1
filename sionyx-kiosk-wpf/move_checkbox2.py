path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

checkbox_block_start = """                <div id="saveCardCheckBox" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">"""

start_idx = content_n.find(checkbox_block_start)
end_marker = "</div>"
end_idx = content_n.find(end_marker, start_idx) + len(end_marker)
full_block = content_n[start_idx:end_idx]

count_block = content_n.count(full_block)
print(f"Block occurrences: {count_block}")
print(f"Block length: {len(full_block)}")

iframe_marker = '            <div class="iframe-card" id="iframeSection">'
count_iframe = content_n.count(iframe_marker)
print(f"iframe marker matches: {count_iframe}")

if count_block == 1 and count_iframe == 1:
    # מסירים את הבלוק ממקומו (בלי לגעת בשורות ריקות שמסביב)
    content_n = content_n.replace(full_block, "", 1)

    # מוסיפים אותו לפני iframe-card
    new_block = full_block + "\n\n"
    content_n = content_n.replace(iframe_marker, new_block + iframe_marker, 1)

    open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
    print('OK - moved successfully')
else:
    print('ABORTING - counts not exactly 1, no changes written')
