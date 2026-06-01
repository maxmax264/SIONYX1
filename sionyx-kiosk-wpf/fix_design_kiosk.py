# שלב 1 - תקן XAML
f=open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c=f.read()
f.close()
old='Stretch="UniformToFill"\n               Visibility="{Binding HasBackgroundImage, Converter={StaticResource BoolToVis}}"\n               Opacity="0.55"'
new='Stretch="{Binding BgStretch}"\n               Visibility="{Binding HasBackgroundImage, Converter={StaticResource BoolToVis}}"\n               Opacity="{Binding BgOpacity}"'
assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml','w',encoding='utf-8').write(c)
print('XAML OK')

# שלב 2 - הוסף properties ל-ViewModel
f=open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c=f.read()
f.close()
old='    [ObservableProperty] private bool _hasBackgroundImage;'
new='    [ObservableProperty] private bool _hasBackgroundImage;\n    [ObservableProperty] private double _bgOpacity = 0.55;\n    [ObservableProperty] private string _bgStretch = "UniformToFill";'
assert c.count(old)==1
c=c.replace(old,new,1)

# שלב 3 - קרא kioskDesign מ-Firebase
old='                    Serilog.Log.Information("[BG] Background set OK, HasBg={H}", HasBackgroundImage);'
new='''                    try {
                        using var http2 = new System.Net.Http.HttpClient();
                        var cfg = SionyxKiosk.Infrastructure.FirebaseConfig.Load();
                        var durl = $"{cfg.DatabaseUrl}/organizations/{cfg.OrgId}/metadata/kioskDesign.json";
                        var djson = await http2.GetStringAsync(durl);
                        if (djson != "null" && !string.IsNullOrEmpty(djson)) {
                            var d = System.Text.Json.JsonDocument.Parse(djson).RootElement;
                            System.Windows.Application.Current.Dispatcher.Invoke(() => {
                                if (d.TryGetProperty("opacity", out var op)) BgOpacity = op.GetDouble();
                                if (d.TryGetProperty("stretch", out var st)) BgStretch = st.GetString() ?? "UniformToFill";
                            });
                        }
                    } catch { }
                    Serilog.Log.Information("[BG] Background set OK, HasBg={H}", HasBackgroundImage);'''
assert c.count(old)==1
c=c.replace(old,new,1)
open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs','w',encoding='utf-8').write(c)
print('VM OK')
