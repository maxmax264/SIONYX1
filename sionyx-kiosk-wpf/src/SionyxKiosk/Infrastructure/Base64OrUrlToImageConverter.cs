using System.Globalization;
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
