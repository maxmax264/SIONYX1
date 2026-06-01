import os
for root, dirs, files in os.walk(r'.\src\SionyxKiosk\Infrastructure\Logging'):
    for f in files:
        path = os.path.join(root, f)
        print(path)
        print(open(path, encoding='utf-8').read()[:500])
        print("---")
