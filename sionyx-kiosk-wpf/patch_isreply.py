content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', encoding='utf-8').read()

old = '''    public bool FromSupervisor { get; set; }
}'''

new = '''    public bool FromSupervisor { get; set; }
    public bool IsUserReply { get; set; }
}'''

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml.cs', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
