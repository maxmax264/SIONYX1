lines = open(r'.\src\SionyxKiosk\Services\SessionService.cs', encoding='utf-8').readlines()

# מצא את השורות
start = next(i for i,l in enumerate(lines) if 'Fetch fresh user data from Firebase' in l)
end = next(i for i,l in enumerate(lines) if 'if (!result.Success) return Error("Failed to start session")' in l)

print(f'Found block: lines {start+1} to {end+1}')
for i in range(start, end+1):
    print(f'{i+1}: {lines[i]}', end='')
