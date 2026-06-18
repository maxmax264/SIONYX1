path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

# לשונית פיקוח - הודעות נכנסות (פיקוח): Left->Right
old_sup_in = 'Background="#F0FDF4" Margin="0,0,80,0"'
new_sup_in = 'Background="#F0FDF4" Margin="80,0,0,0"'

# לשונית פיקוח - תגובות יוצאות (אתה): Left->Left עם Margin שונה
old_sup_out = '<!-- תגובת המשתמש - ימין, ירוק כהה -->\n                                                <Border CornerRadius="14" Padding="12,10"\n                                                        MaxWidth="280" HorizontalAlignment="Left"\n                                                        Margin="0,0,80,0">'
new_sup_out = '<!-- תגובת המשתמש - ימין, ירוק כהה -->\n                                                <Border CornerRadius="14" Padding="12,10"\n                                                        MaxWidth="280" HorizontalAlignment="Right"\n                                                        Margin="0,0,80,0">'

print(f"Supervisor incoming: {content.count(old_sup_in)}")
print(f"Supervisor outgoing: {content.count(old_sup_out)}")

content = content.replace(old_sup_in, new_sup_in)
content = content.replace(old_sup_out, new_sup_out)
open(path, 'w', encoding='utf-8').write(content)
print("OK")
