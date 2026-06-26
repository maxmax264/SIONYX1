content = open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', encoding='utf-8').read()

old = '''_trayIcon.OpenControlPanelRequested += () =>
                              {
                                  Services.KioskPolicyService.RunWithControlPanel(() =>
                                      System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                                      {
                                          FileName = "control.exe",
                                          UseShellExecute = true
                                      }));
                              };'''

new = '''_trayIcon.OpenControlPanelRequested += async () =>
                              {
                                  var dialog = new Views.Dialogs.AdminExitDialog();
                                  dialog.Owner = null;
                                  dialog.WindowStartupLocation = System.Windows.WindowStartupLocation.CenterScreen;
                                  dialog.Topmost = true;
                                  if (dialog.ShowDialog() != true) return;
                                  var password = dialog.EnteredPassword;
                                  var orgMetadata = _host?.Services.GetService<OrganizationMetadataService>();
                                  var passwordResult = orgMetadata != null ? await orgMetadata.GetAdminExitPasswordAsync() : null;
                                  var firebasePassword = passwordResult?.IsSuccess == true && passwordResult.Data is string p ? p : null;
                                  var expectedPassword = firebasePassword ?? Infrastructure.AppConstants.GetAdminExitPassword();
                                  if (password != expectedPassword)
                                  {
                                      Views.Dialogs.AlertDialog.Show("שגיאה", "סיסמה שגויה", Views.Dialogs.AlertDialog.AlertType.Warning, null);
                                      return;
                                  }
                                  Services.KioskPolicyService.RunWithControlPanel(() =>
                                      System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
                                      {
                                          FileName = "control.exe",
                                          UseShellExecute = true
                                      }));
                              };'''

count = content.count(old)
print(f"Found {count} matches")
if count == 1:
    content = content.replace(old, new)
    open(r'C:\Users\user\Desktop\SIONYX-clean\sionyx-kiosk-wpf\src\SionyxKiosk\App.xaml.cs', 'w', encoding='utf-8').write(content)
    print('OK')
else:
    print("Not found")
