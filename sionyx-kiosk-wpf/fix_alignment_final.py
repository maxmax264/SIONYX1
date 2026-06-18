path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

# הסר FlowDirection מה-Grid
old = '<Grid Margin="0,0,0,10" FlowDirection="LeftToRight">'
new = '<Grid Margin="0,0,0,10">'

count = content.count(old)
print(f"Grid matches: {count}")
content = content.replace(old, new)

# החזר הודעות נכנסות ל-Left (RTL = ימין)
old2 = 'MaxWidth="280" HorizontalAlignment="Right"\n                                                        Background="#F1F5F9" Margin="80,0,0,0"'
new2 = 'MaxWidth="280" HorizontalAlignment="Left"\n                                                        Background="#F1F5F9" Margin="0,0,80,0"'

old3 = 'MaxWidth="280" HorizontalAlignment="Right"\n                                                        Background="#F0FDF4" Margin="80,0,0,0"'
new3 = 'MaxWidth="280" HorizontalAlignment="Left"\n                                                        Background="#F0FDF4" Margin="0,0,80,0"'

# הודעות יוצאות (אתה) נשארות Left (RTL = ימין פיזית? לא...)
# בעצם ב-RTL: Left=ימין, Right=שמאל
# אז הודעות נכנסות צריכות Right (=שמאל פיזי), יוצאות Left (=ימין פיזי)

print(f"Admin incoming: {content.count(old2)}")
print(f"Supervisor incoming: {content.count(old3)}")

content = content.replace(old2, new2)
content = content.replace(old3, new3)

open(path, 'w', encoding='utf-8').write(content)
print("OK")
