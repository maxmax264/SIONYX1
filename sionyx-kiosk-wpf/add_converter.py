f = open(r'.\src\SionyxKiosk\App.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n             ShutdownMode="OnExplicitShutdown">'
new = '             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n             ShutdownMode="OnExplicitShutdown">'

# הוסף converter ל-MergedDictionaries
old2 = '            </ResourceDictionary.MergedDictionaries>\n        </ResourceDictionary>'
new2 = '            </ResourceDictionary.MergedDictionaries>\n            <BooleanToVisibilityConverter x:Key="BoolToVis" />\n        </ResourceDictionary>'

assert c.count(old2) == 1
c = c.replace(old2, new2, 1)
open(r'.\src\SionyxKiosk\App.xaml', 'w', encoding='utf-8').write(c)
print("OK")
