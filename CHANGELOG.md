# Changelog


## [3.5.5] - 2026-07-05

### Bug Fixes
- extend purchase-status polling timeout to 80s to avoid racing confirmPayment on Render cold start (cd9841b0)

### Other
- bump version to 3.5.7 (bc6bb006)
- validate event.origin before trusting TransactionResponse; send real phone/name to Nedarim (b6859210)


## [3.5.4] - 2026-07-04

### Bug Fixes
- hide Tokef field in iframe when creating a token (save card checked) (c97889f4)
- re-ignore understood-payment-bridge (was accidentally re-tracked) (47e40b1e)


## [3.5.2] - 2026-07-03

### Bug Fixes
- PaymentDialog InjectConfigAsync expected JsonElement but got plain object from in-process metadata result (c1bc7537)


## [3.5.0] - 2026-07-03

### Features
- configure auto-login during installation (96a75dff)
- require administrator privileges via app.manifest (a52b4d5d)
- restart explorer after Registry policy change for immediate effect (b2248b22)
- block Control Panel during kiosk session via Registry policy (f8c534cb)
- connect PrintHistoryPage to Firebase printLogs (7b97f968)
- connect PrintHistoryPage to Firebase printLogs (e0b3b0fd)
- tray menu Hebrew fix + check/force update + about dialog fix (d881a6d0)
- auto-update via GitHub Releases + Render endpoint (c58543bf)
- auto-update via Render server + Firebase Storage, version in Tray menu (dfc588e6)
- show version in Tray menu (7e4eab0f)
- AutoUpdateService - check GitHub Releases on startup and install silently (f2534e46)
- Startup Settings dialog - manage which users kiosk auto-starts on (f59d1f87)
- Tray freeze - restore client session on admin return instead of showing auth (c0468640)
- Cleanup Engine - clean browser/downloads only if user entered desktop (fb5534c9)
- add SessionStateService - tracks active session in Registry, handles power outage cleanup (ee19c678)
- migrate to single-user architecture - remove SionyxUser, add HKLM Run + LaunchKiosk (90b6dd8e)

### Bug Fixes
- track app.manifest (was excluded by blanket *.manifest gitignore rule, breaking CI builds) (12d821dc)
- SafeGet crashes on numeric JSON values; DecodeData falls back to raw value for unencoded metadata; make AdminExitPassword test production-aware (ac98503c)
- hide taskbar icon and remove desktop shortcut (f284163b)
- control panel stays open until admin dismisses dialog; add KP1-KP6 guard tests (ff913975)
- SIONYX_LaunchOnce task - add LogonTrigger for auto-start on login (c9990ed4)
- installer - detect logged-in user for auto-login configuration (7ac09ed5)
- SetAutoLogin - fix null warnings, single user auto-login (e6e88665)
- filter system accounts from startup users list (8cba08a2)
- StartupSettingsDialog - configure AutoAdminLogon and HKLM Run key per selected user (ab21102a)
- auto-login without username dependency (f03a3dc8)
- remove tray icon from MainWindow — managed by App.xaml.cs only (2228118f)
- use KioskPolicyService.RunWithControlPanel in App.xaml.cs tray menu (4da16667)
- run kiosk task with HighestAvailable privileges for Registry access (e4bb7840)
- restore upload_release.py with correct UTF-8 encoding (87ae0cb8)
- restore upload_release.py (2c4bce98)
- SessionStateService - write to ProgramData JSON instead of HKLM registry (52e80ac9)
- silent update MSI_PATH delayed expansion, OrgId/ComputerName RegistrySearch preservation on upgrade, remove UAC runas from schtasks trigger (7266c6aa)
- increase taskkill timeout before msiexec to ensure process fully closes (ac45bd52)
- replace machine restart with kiosk-only restart after update (521291ff)
- admin exit password always from Firebase (public read) (3c21d022)
- set ContentRoot to AppContext.BaseDirectory to prevent crash when launched from MSI temp dir (a39467bd)
- resolve all MessagesPage merge conflicts; feat: LaunchKiosk logs via SionyxLogger (f05ab627)
- add IsUserReply to message loading from Firebase (2157e441)
- LaunchKiosk as immediate action - kiosk starts right after install (c8121eb9)
- clear stored tokens on stale session cleanup - prevent auto-login after power outage (0e7f6aec)
- add DevMode guard to BrowserCleanupService and ProcessCleanupService (60d1505b)

### Other
- remove leftover debug scripts and build temp files (7c26f27a)
- local state for review (85c1dfc4)
- ensure plain env file is gitignored (076e0c7e)
- saved-card payment fixes - credit logic, CVV removal, default-on (fde2b92e)
- add AU9-AU14 flow guard tests for AutoUpdateService (51d7d935)
- KioskPolicyAndStartupTests - guard LogonTrigger and HKLM Run key (784fa58c)
- remove temp python scripts (0876312c)
- before fixing exit shortcut bug in customer interface (8678de8d)
- before fixing exit shortcut bug in customer interface (4d44a8a6)
- before [תיאור] (be70028d)
- before adding logging calls (6c812a28)
- before adding logger (2105a93a)
- fix MessagesPage chat bubbles left/right + supervisor name (9cb2e580)
- fix MessagesPage chat bubbles left/right + supervisor name (c024bb38)

All notable changes to the SIONYX Kiosk installer are documented here.
This file is auto-generated from [Conventional Commits](https://www.conventionalcommits.org/).