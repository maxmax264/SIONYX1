path = r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml'
content = open(path, encoding='utf-8').read()

# הודעות נכנסות: שמאל -> ימין (בגלל RTL זה יופיע משמאל)
old1 = 'MaxWidth="280" HorizontalAlignment="Left"\n                                        Background="#F1F5F9" Margin="0,0,80,0"'
new1 = 'MaxWidth="280" HorizontalAlignment="Right"\n                                        Background="#F1F5F9" Margin="80,0,0,0"'

# הודעות יוצאות: ימין -> שמאל
old2 = 'MaxWidth="280" HorizontalAlignment="Right"\n                                        Margin="80,0,0,0"'
new2 = 'MaxWidth="280" HorizontalAlignment="Left"\n                                        Margin="0,0,80,0"'

print(f"Incoming: {content.count(old1)} matches")
print(f"Outgoing: {content.count(old2)} matches")
