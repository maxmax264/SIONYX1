path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

# החזר FlowDirection לPage
old1 = 'Title="הודעות">'
new1 = 'Title="הודעות" FlowDirection="RightToLeft">'

# הפוך בועות: הודעות נכנסות Left->Right, יוצאות Right->Left
old2 = 'MaxWidth="280" HorizontalAlignment="Left"\r\n                                                        Background="#F1F5F9" Margin="0,0,80,0"'
new2 = 'MaxWidth="280" HorizontalAlignment="Right"\r\n                                                        Background="#F1F5F9" Margin="80,0,0,0"'

old3 = 'MaxWidth="280" HorizontalAlignment="Right"\r\n                                                        Margin="80,0,0,0"'
new3 = 'MaxWidth="280" HorizontalAlignment="Left"\r\n                                                        Margin="0,0,80,0"'

print(f"Page title: {content.count(old1)}")
print(f"Incoming bubble: {content.count(old2)}")
print(f"Outgoing bubble: {content.count(old3)}")

content = content.replace(old1, new1, 1)
open(path, 'w', encoding='utf-8').write(content)
print("OK - restored FlowDirection")
