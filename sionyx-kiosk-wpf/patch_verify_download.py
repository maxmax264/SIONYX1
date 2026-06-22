path = r"src\SionyxKiosk\Services\AutoUpdateService.cs"

with open(path, "rb") as f:
    content = f.read().decode("utf-8")

old = 'Logger.Information("[Update] Download complete ({MB} MB)", downloaded / 1024 / 1024);\r\n            ProgressChanged?.Invoke(90, "מתקין עדכון...");'

new = '''Logger.Information("[Update] Download complete ({MB} MB)", downloaded / 1024 / 1024);

            // Verify downloaded file size matches expected
            var fileInfo = new FileInfo(tempPath);
            if (totalBytes > 0 && fileInfo.Length != totalBytes)
            {
                Logger.Error("[Update] Size mismatch: expected {Expected}, got {Actual} — deleting corrupt file", totalBytes, fileInfo.Length);
                try { File.Delete(tempPath); } catch { }
                await LogUpdateToFirebase("failed", newVersion);
                return;
            }
            Logger.Information("[Update] Download verified OK: {Bytes} bytes", fileInfo.Length);
            ProgressChanged?.Invoke(90, "מתקין עדכון...");'''

if old in content:
    content = content.replace(old, new, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched successfully!")
else:
    print("ERROR: not found")
    print(repr(old[:80]))
