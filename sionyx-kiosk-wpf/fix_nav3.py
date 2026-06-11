content = open(r'.\src\SionyxKiosk\Views\Windows\MainWindow.xaml.cs', encoding='utf-8').read()
old = 'using SionyxKiosk.Views.Pages;'
new = 'using SionyxKiosk.Views.Pages;'
# Check it exists
count = content.count(old)
print(f"Using exists: {count}")
