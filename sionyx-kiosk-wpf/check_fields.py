content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()
# מצא את כל המקומות שבהם נקבע FromSupervisor או IsUserReply
import re
for m in re.finditer(r'(FromSupervisor|IsUserReply)\s*=', content):
    start = max(0, m.start()-100)
    print(content[start:m.end()+100])
    print("---")
