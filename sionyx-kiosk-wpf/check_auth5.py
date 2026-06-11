content = open(r'.\src\SionyxKiosk\Services\AuthService.cs', encoding='utf-8').read()
idx = content.find('IsLoggedInOnAnotherComputer')
while idx != -1:
    print(f"=== pos {idx} ===")
    print(content[idx-200:idx+300])
    print()
    idx = content.find('IsLoggedInOnAnotherComputer', idx+1)
