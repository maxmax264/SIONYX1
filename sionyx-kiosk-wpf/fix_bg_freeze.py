f=open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c=f.read()
f.close()

old='''                    try {
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
                    } catch (Exception ex2) { Serilog.Log.Error(ex2, "[BG] BitmapImage failed"); }'''

new='''                    try {
                        System.Windows.Application.Current.Dispatcher.Invoke(() => {
                            var bmp = new System.Windows.Media.Imaging.BitmapImage();
                            bmp.BeginInit();
                            if (url.StartsWith("data:image")) {
                                var b64 = url.Substring(url.IndexOf(',')+1);
                                var bytes = System.Convert.FromBase64String(b64);
                                bmp.StreamSource = new System.IO.MemoryStream(bytes);
                                bmp.CacheOption = System.Windows.Media.Imaging.BitmapCacheOption.OnLoad;
                            } else {
                                bmp.UriSource = new Uri(url, UriKind.Absolute);
                                bmp.CacheOption = System.Windows.Media.Imaging.BitmapCacheOption.OnLoad;
                            }
                            bmp.EndInit();
                            BackgroundImageSource = bmp;
                        });
                    } catch (Exception ex2) { Serilog.Log.Error(ex2, "[BG] BitmapImage failed"); }'''

assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs','w',encoding='utf-8').write(c)
print("OK")
