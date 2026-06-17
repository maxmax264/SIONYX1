content = open(r'src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
old = 'Binding="{Binding FromSupervisor}" Value="True"><Setter Property="Visibility" Value="Visible"/>'
new = 'Binding="{Binding IsUserReply}" Value="False"><Setter Property="Visibility" Value="Visible"/>'
# מחפש את הגרסה הארוכה עם newlines
old2 = '<DataTrigger Binding="{Binding FromSupervisor}" Value="True">\n                                                                    <Setter Property="Visibility" Value="Visible"/>\n                                                                </DataTrigger>'
new2 = '<DataTrigger Binding="{Binding IsUserReply}" Value="False"><Setter Property="Visibility" Value="Visible"/></DataTrigger>'
count = content.count(old2)
print(f"Found long: {count}")
count2 = content.count(old)
print(f"Found short: {count2}")
