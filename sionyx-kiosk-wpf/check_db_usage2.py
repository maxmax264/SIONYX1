import os
for root, dirs, files in os.walk(r'.\src\SionyxKiosk'):
    dirs[:] = [d for d in dirs if d != 'obj']
    for f in files:
        if f.endswith('.cs'):
            path = os.path.join(root, f)
            c = open(path, encoding='utf-8').read()
            if 'OnceSingleAsync' in c or 'FirebaseClient' in c:
                print(f"\n=== {f} ===")
                for i, line in enumerate(c.splitlines()):
                    if 'OnceSingleAsync' in line or 'FirebaseClient' in line or '_db' in line or '_client' in line:
                        print(f"  {i+1}: {line.strip()}")
