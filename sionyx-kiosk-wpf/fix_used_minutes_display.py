content = open(r'.\src\SionyxKiosk\Models\SessionLogItem.cs', encoding='utf-8').read()

old = "public string UsedMinutesDisplay => UsedSeconds > 0 ? $\"{UsedSeconds / 60} דק'\" : \"-\";"
new = """public string UsedMinutesDisplay => UsedSeconds switch
    {
        <= 0 => "-",
        < 60 => $"{UsedSeconds} שנ'",
        < 3600 => $"{UsedSeconds / 60} דק'",
        _ => $"{UsedSeconds / 3600}:{(UsedSeconds % 3600) / 60:D2} שע'"
    };"""

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Models\SessionLogItem.cs', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    print("NOT FOUND")
