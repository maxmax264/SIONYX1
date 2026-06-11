content = open(r'.\tests\SionyxKiosk.Tests\Services\AuthServiceFinalCoverageTests.cs', encoding='utf-8').read()
old = """namespace SionyxKiosk.Tests.Services;

/// <summary>
/// Final coverage tests for AuthService targeting uncovered paths:"""
new = """namespace SionyxKiosk.Tests.Services;

[Collection("AuthServiceFinal")]
/// <summary>
/// Final coverage tests for AuthService targeting uncovered paths:"""
count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new, 1)
    open(r'.\tests\SionyxKiosk.Tests\Services\AuthServiceFinalCoverageTests.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print('NOT FOUND')
