content = open(r'src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
old = '''<DataTrigger Binding="{Binding FromSupervisor}" Value="False">
                                                                    <Setter Property="Visibility" Value="Visible"/>
                                                                </DataTrigger>'''
count = content.count(old)
print(f"Found {count} matches")
idx = content.find('FromSupervisor}" Value="False"')
print(repr(content[idx-20:idx+150]))
