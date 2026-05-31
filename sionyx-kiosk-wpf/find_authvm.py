import os
for root, dirs, files in os.walk(r'.\src\SionyxKiosk'):
    for f in files:
        if 'Auth' in f and f.endswith('.cs'):
            print(os.path.join(root, f))
