import os
for root, dirs, files in os.walk(r'.\sionyx-kiosk-wpf\src\SionyxKiosk'):
    for file in files:
        if file.endswith('.cs'):
            path = os.path.join(root, file)
            content = open(path, encoding='utf-8', errors='ignore').read()
            if 'OverlayGradient' in content or 'authDesign' in content or 'overlayColor' in content or 'buttonColor' in content:
                for i, line in enumerate(content.split('\n')):
                    if any(x in line for x in ['OverlayGradient', 'authDesign', 'overlayColor', 'buttonColor']):
                        print(f'{path}:{i+1}: {line.strip()}')
