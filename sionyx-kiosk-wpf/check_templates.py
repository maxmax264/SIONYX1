content = open(r'.\src\SionyxKiosk\Views\Pages\MessagesPage.xaml', encoding='utf-8').read()
# Count how many DataTemplates we have
import re
templates = [m.start() for m in re.finditer('<DataTemplate>', content)]
print(f"Total DataTemplates: {len(templates)}")
for i, pos in enumerate(templates):
    print(f"\n=== Template {i+1} (pos {pos}) ===")
    print(content[pos:pos+200])
