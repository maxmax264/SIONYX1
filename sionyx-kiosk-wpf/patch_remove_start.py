path = r"installer\CustomActions\KioskSetupActions.cs"

with open(path, "rb") as f:
    content = f.read().decode("utf-8")

# Find and show exact context
idx = content.find("timeout /t 3")
if idx == -1:
    print("NOT FOUND")
else:
    print("Found, context:")
    print(repr(content[idx-10:idx+60]))

    # Remove the two lines with 4-space indent
    for line in ['    timeout /t 3 /nobreak >nul', '    start """" ""{appExe}"""']:
        for ending in ['\r\n', '\n']:
            target = line + ending
            if target in content:
                content = content.replace(target, '', 1)
                print(f"Removed: {repr(line)}")
                break
        else:
            print(f"NOT FOUND: {repr(line)}")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done.")
