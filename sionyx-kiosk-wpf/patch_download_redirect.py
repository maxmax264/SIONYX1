import sys

path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''            using var http = new HttpClient();
            http.Timeout = TimeSpan.FromMinutes(10);

            using var response = await http.GetAsync(downloadUrl, HttpCompletionOption.ResponseHeadersRead);
            var totalBytes = response.Content.Headers.ContentLength ?? 0;'''

new = '''            using var http = new HttpClient(new HttpClientHandler { AllowAutoRedirect = true });
            http.Timeout = TimeSpan.FromMinutes(10);

            using var response = await http.GetAsync(downloadUrl, HttpCompletionOption.ResponseHeadersRead);
            var totalBytes = response.Content.Headers.ContentLength ?? 0;
            Logger.Information("[Update] Download size: {Bytes} bytes (Content-Length={CL})", totalBytes, response.Content.Headers.ContentLength);'''

if old not in content:
    print("ERROR: Target not found.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched successfully!")
