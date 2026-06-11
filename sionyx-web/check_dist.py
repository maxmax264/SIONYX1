import os
dist = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\dist\assets'
files = [f for f in os.listdir(dist) if f.endswith('.js') and 'index' in f]
for f in files:
    content = open(os.path.join(dist, f), encoding='utf-8').read()
    if 'fromSupervisor' in content:
        print(f"FOUND in {f}")
    else:
        print(f"NOT FOUND in {f}")
