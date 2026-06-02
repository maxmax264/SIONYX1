f = open(r'.\src\SionyxKiosk\Views\Windows\AuthWindow.xaml', encoding='utf-8')
c = f.read()
f.close()
idx = c.find('FormCanvas')
# חפש את סוף ה-Viewbox
end_idx = c.find('</Viewbox>', idx)
print(f'</Viewbox> at offset: {end_idx - idx}')
print(c[end_idx-50:end_idx+100])
