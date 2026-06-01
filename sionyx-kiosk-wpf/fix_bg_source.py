import re

# תקן XAML
f=open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c=f.read()
f.close()
old='Source="{Binding BackgroundImageUrl, Converter={StaticResource Base64ToImage}}"'
new='Source="{Binding BackgroundImageSource}"'
assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml','w',encoding='utf-8').write(c)
print('XAML OK')

# הוסף property ל-ViewModel
f=open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c=f.read()
f.close()
old='    [ObservableProperty] private bool _hasBackgroundImage;'
new='    [ObservableProperty] private bool _hasBackgroundImage;\n    [ObservableProperty] private System.Windows.Media.ImageSource? _backgroundImageSource;'
assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs','w',encoding='utf-8').write(c)
print('Property OK')

# תקן את LoadBackground לטעון BitmapImage
f=open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c=f.read()
f.close()
old='                    BackgroundImageUrl = url;\n                    HasBackgroundImage = true;\n                    Serilog.Log.Information("[BG] Background set OK, HasBg={H}", HasBackgroundImage);\n                    return;'
new='''                    BackgroundImageUrl = url;
                    HasBackgroundImage = true;
                    try {
                        var bmp = new System.Windows.Media.Imaging.BitmapImage();
                        bmp.BeginInit();
                        if (url.StartsWith("data:image")) {
                            var b64 = url.Substring(url.IndexOf(',')+1);
                            var bytes = System.Convert.FromBase64String(b64);
                            bmp.StreamSource = new System.IO.MemoryStream(bytes);
                        } else {
                            bmp.UriSource = new Uri(url, UriKind.Absolute);
                        }
                        bmp.CacheOption = System.Windows.Media.Imaging.BitmapCacheOption.OnLoad;
                        bmp.EndInit();
                        bmp.Freeze();
                        BackgroundImageSource = bmp;
                    } catch (Exception ex2) { Serilog.Log.Error(ex2, "[BG] BitmapImage failed"); }
                    Serilog.Log.Information("[BG] Background set OK, HasBg={H}", HasBackgroundImage);
                    return;'''
assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs','w',encoding='utf-8').write(c)
print('LoadBG OK')
