# 1. צור את ה-Converter
converter = """using System.Globalization;
using System.IO;
using System.Windows.Data;
using System.Windows.Media.Imaging;

namespace SionyxKiosk.Infrastructure;

[ValueConversion(typeof(string), typeof(BitmapImage))]
public class Base64OrUrlToImageConverter : IValueConverter
{
    public static readonly Base64OrUrlToImageConverter Instance = new();

    public object? Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        if (value is not string s || string.IsNullOrWhiteSpace(s)) return null;
        try
        {
            if (s.StartsWith("data:image", StringComparison.OrdinalIgnoreCase))
            {
                var base64 = s.Substring(s.IndexOf(',') + 1);
                var bytes = System.Convert.FromBase64String(base64);
                var bmp = new BitmapImage();
                bmp.BeginInit();
                bmp.StreamSource = new MemoryStream(bytes);
                bmp.CacheOption = BitmapCacheOption.OnLoad;
                bmp.EndInit();
                bmp.Freeze();
                return bmp;
            }
            else
            {
                var bmp = new BitmapImage();
                bmp.BeginInit();
                bmp.UriSource = new Uri(s, UriKind.Absolute);
                bmp.CacheOption = BitmapCacheOption.OnLoad;
                bmp.EndInit();
                bmp.Freeze();
                return bmp;
            }
        }
        catch { return null; }
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}
"""
open(r'.\src\SionyxKiosk\Infrastructure\Base64OrUrlToImageConverter.cs', 'w', encoding='utf-8').write(converter)
print("Converter OK")

# 2. עדכן App.xaml להוסיף את ה-Converter
f = open(r'.\src\SionyxKiosk\App.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '<Application x:Class="SionyxKiosk.App"\n             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n             ShutdownMode="OnExplicitShutdown">'
new = '<Application x:Class="SionyxKiosk.App"\n             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"\n             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"\n             xmlns:infra="clr-namespace:SionyxKiosk.Infrastructure"\n             ShutdownMode="OnExplicitShutdown">'
assert c.count(old) == 1
c = c.replace(old, new, 1)

old2 = '            <BooleanToVisibilityConverter x:Key="BoolToVis" />\n        </ResourceDictionary>'
new2 = '            <BooleanToVisibilityConverter x:Key="BoolToVis" />\n            <infra:Base64OrUrlToImageConverter x:Key="Base64ToImage" />\n        </ResourceDictionary>'
assert c.count(old2) == 1
c = c.replace(old2, new2, 1)

open(r'.\src\SionyxKiosk\App.xaml', 'w', encoding='utf-8').write(c)
print("App.xaml OK")

# 3. עדכן AuthWindow.xaml להשתמש ב-Converter
f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()

old3 = '               Source="{Binding BackgroundImageUrl}"\n               Stretch="UniformToFill"'
new3 = '               Source="{Binding BackgroundImageUrl, Converter={StaticResource Base64ToImage}}"\n               Stretch="UniformToFill"'
assert c.count(old3) == 1
c = c.replace(old3, new3, 1)

open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', 'w', encoding='utf-8').write(c)
print("AuthWindow.xaml OK")
