f = open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', encoding='utf-8')
c = f.read()
f.close()

old = '''                            <controls:PurchaseCard
                                PackageName="{Binding PackageName}"
                                PurchaseDate="{Binding CreatedAt}"
                                Amount="{Binding Amount, StringFormat='\u20aa{0:F2}'}"
                                Status="{Binding Status}"
                                Minutes="{Binding Minutes}"
                                PrintBudget="{Binding PrintBudget}"
                                ValidityDays="{Binding ValidityDays}" />'''

new = '''                            <controls:PurchaseCard
                                PackageName="{Binding PackageName}"
                                PurchaseDate="{Binding CreatedAt}"
                                Amount="{Binding Amount, StringFormat='\u20aa{0:F2}'}"
                                Status="{Binding Status}"
                                Minutes="{Binding Minutes}"
                                PrintBudget="{Binding PrintBudget}"
                                ValidityDays="{Binding ValidityDays}"
                                IsOperatorTopup="{Binding IsOperatorTopup}" />'''

count = c.count(old)
print(f'Found {count} matches')
if count == 1:
    c = c.replace(old, new, 1)
    open(r'.\src\SionyxKiosk\Views\Pages\HistoryPage.xaml', 'w', encoding='utf-8').write(c)
    print('OK')
else:
    print(f'NOT FOUND')
    # הצג את מה שיש
    idx = c.find('PurchaseCard')
    print(repr(c[idx:idx+300]))
