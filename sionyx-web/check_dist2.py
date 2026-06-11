import os
dist = r'C:\Users\user\Desktop\SIONYX-clean\sionyx-web\dist\assets'
files = [f for f in os.listdir(dist) if 'supervisor' in f.lower() and f.endswith('.js')]
for f in files:
    content = open(os.path.join(dist, f), encoding='utf-8').read()
    if 'fromSupervisor' in content:
        print(f"FOUND in {f}")
        idx = content.find('fromSupervisor')
        print(content[idx-50:idx+100])
    else:
        print(f"NOT FOUND in {f}")
