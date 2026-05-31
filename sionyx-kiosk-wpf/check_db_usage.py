import os, re
for root, dirs, files in os.walk(r'.\src\SionyxKiosk\Services'):
    for f in files:
        if f.endswith('.cs'):
            path = os.path.join(root, f)
            c = open(path, encoding='utf-8').read()
            if 'FirebaseConfig' in c or 'OnceSingleAsync' in c or '_db.Child' in c:
                print(f"\n=== {f} ===")
                for i, line in enumerate(c.splitlines()):
                    if 'FirebaseConfig' in line or 'OnceSingleAsync' in line or '_db.Child' in line:
                        print(f"  {i+1}: {line}")
