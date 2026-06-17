content = open(r'src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
old = '''<DataTrigger Binding="{Binding FromSupervisor}" Value="False">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>'''
new = '''<DataTrigger Binding="{Binding IsUserReply}" Value="True">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>'''
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'src\SionyxKiosk\Views\Pages\MessagesPage.xaml', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
