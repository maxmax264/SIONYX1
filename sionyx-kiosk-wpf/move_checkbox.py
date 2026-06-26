path = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\Assets\templates\payment.html'
content = open(path, encoding='utf-8').read()
content_n = content.replace('\r\n', '\n')

checkbox_block_start = """                <div id="saveCardCheckBox" style="display:none; margin-bottom:14px; padding:12px 16px; background:#F8FAFC; border:1.5px solid #E2E8F0; border-radius:10px; direction:rtl;">"""

start_idx = content_n.find(checkbox_block_start)
end_marker = "</div>"
end_idx = content_n.find(end_marker, start_idx) + len(end_marker)
full_block = content_n[start_idx:end_idx]

print("Block found:", start_idx != -1)
print("Block length:", len(full_block))

# מסירים את הבלוק ממקומו הנוכחי (כולל שורה ריקה אחת לפניו אם קיימת)
removal_target = "\n" + full_block + "\n\n"
count_removal = content_n.count(removal_target)
print(f"Removal target matches: {count_removal}")

if count_removal == 1:
    content_n = content_n.replace(removal_target, "\n", 1)

    # מוסיפים את הבלוק לפני iframe-card
    iframe_marker = '            <div class="iframe-card" id="iframeSection">'
    count_iframe = content_n.count(iframe_marker)
    print(f"iframe marker matches: {count_iframe}")
    if count_iframe == 1:
        new_block = full_block + "\n\n" + iframe_marker
        content_n = content_n.replace(iframe_marker, new_block, 1)
        open(path, 'w', encoding='utf-8', newline='\r\n').write(content_n)
        print('OK - moved successfully')
    else:
        print('IFRAME MARKER NOT UNIQUE - aborting, no changes written')
else:
    print('REMOVAL TARGET NOT FOUND CLEANLY - aborting, no changes written')
