content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
idx = 0
count = 0
while True:
    idx = content.find('currentComputerId', idx)
    if idx == -1:
        break
    count += 1
    print(f"=== {count} (pos {idx}) ===")
    print(content[idx-100:idx+200])
    print()
    idx += 1
