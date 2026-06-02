content = open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml', encoding='utf-8').read()

old = '''             <infra:InverseBoolToVisibilityConverter x:Key="InverseBoolToVis" />'''

new = '''             <views:InverseBoolToVisibilityConverter x:Key="InverseBoolToVis" />'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)

old2 = '''             xmlns:infra="clr-namespace:SionyxKiosk.Infrastructure"'''
# check if views namespace already exists
if 'xmlns:views=' not in content:
    content = content.replace(
        '<Application x:Class="SionyxKiosk.App"',
        '<Application x:Class="SionyxKiosk.App"\n             xmlns:views="clr-namespace:SionyxKiosk.Views.Windows"'
    )
    print("Added views namespace")

open(r'.\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml', 'w', encoding='utf-8').write(content)
print('OK')
