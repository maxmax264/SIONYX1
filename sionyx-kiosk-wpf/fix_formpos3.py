f = open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', encoding='utf-8')
c = f.read()
f.close()

# ביטול ההיפוך - formX ישירות כאחוז
old1 = 'public double FormXPixels => (1.0 - FormX / 100.0) * (1920 - FormWidth);'
new1 = 'public double FormXPixels => FormX / 100.0 * SystemParameters.PrimaryScreenWidth - FormWidth / 2;'

old2 = 'public double FormYPixels => (1.0 - FormY / 100.0) * (1080 - 700);'
new2 = 'public double FormYPixels => FormY / 100.0 * SystemParameters.PrimaryScreenHeight - 350;'

count1 = c.count(old1)
count2 = c.count(old2)
print(f'X match: {count1}, Y match: {count2}')
if count1 == 1 and count2 == 1:
    c = c.replace(old1, new1, 1)
    c = c.replace(old2, new2, 1)
    open(r'.\src\SionyxKiosk\ViewModels\AuthViewModel.cs', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print('NOT FOUND')
