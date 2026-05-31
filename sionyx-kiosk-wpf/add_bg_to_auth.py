f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

old = 'using CommunityToolkit.Mvvm.ComponentModel;\nusing CommunityToolkit.Mvvm.Input;\nusing SionyxKiosk.Services;'
new = 'using CommunityToolkit.Mvvm.ComponentModel;\nusing CommunityToolkit.Mvvm.Input;\nusing SionyxKiosk.Services;\nusing System.Net.Http;'
assert c.count(old) == 1
c = c.replace(old, new, 1)

old2 = '    [ObservableProperty] private string _forgotPasswordInfo = "";'
new2 = '    [ObservableProperty] private string _forgotPasswordInfo = "";\n    [ObservableProperty] private string _backgroundImageUrl = "";\n    [ObservableProperty] private bool _hasBackgroundImage;'
assert c.count(old2) == 1
c = c.replace(old2, new2, 1)

old3 = '    public AuthViewModel(AuthService auth, OrganizationMetadataService? metadataService = null)\n    {\n        _auth = auth;\n        _metadataService = metadataService;\n    }'
new3 = '    public AuthViewModel(AuthService auth, OrganizationMetadataService? metadataService = null)\n    {\n        _auth = auth;\n        _metadataService = metadataService;\n        _ = LoadBackgroundAsync();\n    }\n\n    private async Task LoadBackgroundAsync()\n    {\n        try\n        {\n            var db = SionyxKiosk.Infrastructure.FirebaseConfig.Database;\n            var orgId = SionyxKiosk.Infrastructure.FirebaseConfig.OrgId;\n            var snap = await db.Child($"organizations/{orgId}/metadata").OnceSingleAsync<System.Collections.Generic.Dictionary<string, object>>();\n            if (snap != null\n                && snap.TryGetValue("kioskBackgroundEnabled", out var en) && en is bool enabled && enabled\n                && snap.TryGetValue("kioskBackgroundUrl", out var url) && url is string urlStr && !string.IsNullOrWhiteSpace(urlStr))\n            {\n                BackgroundImageUrl = urlStr;\n                HasBackgroundImage = true;\n            }\n            else\n            {\n                BackgroundImageUrl = "";\n                HasBackgroundImage = false;\n            }\n        }\n        catch\n        {\n            BackgroundImageUrl = "";\n            HasBackgroundImage = false;\n        }\n    }'
assert c.count(old3) == 1
c = c.replace(old3, new3, 1)

open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
print("OK")
