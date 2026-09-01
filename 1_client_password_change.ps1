# ============================================================
# שינוי דרישת אורך סיסמה מינימלי: 6 -> 4 תווים
# עם טרנספורמציה מותנית ל-Firebase כדי לא לשבור משתמשים קיימים
# ============================================================
cd C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf

$results = @()

function Apply-Edit($path, $old, $new, $label) {
    $c = Get-Content $path -Raw
    $count = ([regex]::Matches($c, [regex]::Escape($old))).Count
    if ($count -ne 1) {
        Write-Host "[FAIL] $label -- נמצאו $count התאמות (צריך 1) ב-$path" -ForegroundColor Red
        $script:results += "FAIL: $label"
        return $false
    }
    $c = $c.Replace($old, $new)
    [System.IO.File]::WriteAllText((Resolve-Path $path), $c, [System.Text.UTF8Encoding]::new($false))
    Write-Host "[OK] $label" -ForegroundColor Green
    $script:results += "OK: $label"
    return $true
}

# --- 1. AuthService.cs ---
$p = "src\SionyxKiosk\Services\AuthService.cs"

Apply-Edit $p @'
    private static string PhoneToEmail(string phone)
    {
        var clean = new string(phone.Where(char.IsDigit).ToArray());
        return $"{clean}@sionyx.app";
    }
'@ @'
    private static string PhoneToEmail(string phone)
    {
        var clean = new string(phone.Where(char.IsDigit).ToArray());
        return $"{clean}@sionyx.app";
    }

    /// <summary>Ensures the password sent to Firebase meets its hard 6-char floor.
    /// Existing 6+ char passwords pass through unchanged (backward compatible);
    /// shorter PINs get a fixed prefix. Must match the Cloud Function's version exactly.</summary>
    private static string ToFirebasePassword(string raw) => raw.Length >= 6 ? raw : $"px_{raw}";
'@ "AuthService: הוספת helper ToFirebasePassword"

Apply-Edit $p 'if (password.Length < 6)' 'if (password.Length < 4)' "AuthService: סף ולידציה RegisterAsync"
Apply-Edit $p 'var result = await Firebase.SignUpAsync(firebaseEmail, password);' 'var result = await Firebase.SignUpAsync(firebaseEmail, ToFirebasePassword(password));' "AuthService: SignUpAsync + טרנספורמציה"
Apply-Edit $p 'var result = await Firebase.SignInAsync(email, password);' 'var result = await Firebase.SignInAsync(email, ToFirebasePassword(password));' "AuthService: SignInAsync + טרנספורמציה"
Apply-Edit $p 'var result = await Firebase.ChangePasswordAsync(newPassword);' 'var result = await Firebase.ChangePasswordAsync(ToFirebasePassword(newPassword));' "AuthService: ChangePasswordAsync + טרנספורמציה"

# --- 2. AuthViewModel.cs ---
$p = "src\SionyxKiosk\ViewModels\AuthViewModel.cs"
Apply-Edit $p 'if (Password.Length < 6)' 'if (Password.Length < 4)' "AuthViewModel: סף ולידציה"
Apply-Edit $p 'הסיסמה חייבת להכיל לפחות 6 תווים' 'הסיסמה חייבת להכיל לפחות 4 תווים' "AuthViewModel: טקסט הודעה"

# --- 3. ProfileViewModel.cs ---
$p = "src\SionyxKiosk\ViewModels\ProfileViewModel.cs"
Apply-Edit $p 'if (NewPassword.Length < 6)' 'if (NewPassword.Length < 4)' "ProfileViewModel: סף ולידציה"
Apply-Edit $p 'הסיסמא חייבת להכיל לפחות 6 תווים' 'הסיסמא חייבת להכיל לפחות 4 תווים' "ProfileViewModel: טקסט הודעה"

# --- 4. ErrorTranslations.cs ---
$p = "src\SionyxKiosk\Infrastructure\ErrorTranslations.cs"
Apply-Edit $p 'הסיסמה חייבת להכיל לפחות 6 תווים' 'הסיסמה חייבת להכיל לפחות 4 תווים' "ErrorTranslations: טקסט תרגום"

# --- 5. Tests: AuditFixTests.cs ---
$p = "tests\SionyxKiosk.Tests\AuditFixTests.cs"
Apply-Edit $p @'
        vm.Password = "12345";
        vm.FirstName = "Test";
        vm.LastName = "User";

        await vm.RegisterCommand.ExecuteAsync(null);

        vm.ErrorMessage.Should().Contain("6");
'@ @'
        vm.Password = "ab";
        vm.FirstName = "Test";
        vm.LastName = "User";

        await vm.RegisterCommand.ExecuteAsync(null);

        vm.ErrorMessage.Should().Contain("4");
'@ "AuditFixTests: עדכון טסט סיסמה קצרה"

# --- 6. Tests: AuthViewModelTests.cs ---
$p = "tests\SionyxKiosk.Tests\ViewModels\AuthViewModelTests.cs"
Apply-Edit $p '_vm.ErrorMessage.Should().Be("הסיסמה חייבת להכיל לפחות 6 תווים");' '_vm.ErrorMessage.Should().Be("הסיסמה חייבת להכיל לפחות 4 תווים");' "AuthViewModelTests: עדכון הודעה מצופה"

Write-Host ""
Write-Host "=== סיכום ===" -ForegroundColor Cyan
$results | ForEach-Object { Write-Host $_ }
if ($results -match "^FAIL") {
    Write-Host "יש כשלונות - אל תבנה עדיין, שלח לי את הפלט" -ForegroundColor Red
} else {
    Write-Host "כל 10 השינויים בוצעו. הרץ עכשיו: .\build.ps1" -ForegroundColor Green
}
