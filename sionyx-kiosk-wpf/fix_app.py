content = open(r'.\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = """                services.AddTransient(sp => new MessagesPage(
                    sp.GetRequiredService<ChatService>(),
                    sp.GetRequiredService<FirebaseClient>()));"""

new = """                services.AddTransient(sp => new MessagesPage(
                    sp.GetRequiredService<ChatService>(),
                    sp.GetRequiredService<FirebaseClient>(),
                    sp.GetRequiredService<LocalDatabase>()));"""

count = content.count(old)
print(f"Found: {count}")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('Done')
else:
    print('NOT FOUND')
