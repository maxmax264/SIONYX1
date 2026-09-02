# Changelog


## [3.11.32] - 2026-09-02

### Bug Fixes
- ShieldWindow creation crashed app silently before logging was initialized (ca240681)


## [3.11.31] - 2026-09-02


## [3.11.30] - 2026-09-02


## [3.11.29] - 2026-09-02


## [3.11.28] - 2026-09-01


## [3.11.27] - 2026-09-01


## [3.11.26] - 2026-09-01

### Other
- v3.11.25 (5add2953)
- route resetUserPassword to Render bridge instead of Firebase Function (Blaze plan requirement) (f21599f3)


## [3.11.25] - 2026-09-01

### Other
- route resetUserPassword to Render bridge instead of Firebase Function (Blaze plan requirement) (f21599f3)


## [3.11.24] - 2026-09-01

### Bug Fixes
- lower password minimum to 4 chars (client+server), fix Hebrew encoding corruption in AuthService/functions (2680518c)


## [3.11.11] - 2026-08-28


## [3.11.10] - 2026-08-28


## [3.11.9] - 2026-08-28

### Other
- resolve version.json conflict (7ebd2329)


## [3.11.6] - 2026-08-28

### Other
- check DbUpdateAsync result before logging success (a8d2dcc3)


## [3.11.5] - 2026-08-26


## [3.11.4] - 2026-08-26


## [3.11.3] - 2026-08-26

### Other
- הפעמון נדלק כשהמנהל שולח הודעה (במקום רק כשמתקבלת) והוסרה הזרקת [מחשב: X] אוטומטית לתוך תוכן ההודעה (71a0b1c0)
- רשימת השיחות בדשבורד הראתה הודעות שהמנהל עצמו שלח כאילו התקבלו - עכשיו מתבסס נכון על תגובות המשתמש (userReplies) ומסמן כנקרא כשנפתחת השיחה (b1d717a4)


## [3.11.2] - 2026-08-23

### Other
- כשל ברענון מטא-דאטה (בדיקת enabled) לא ימחק תמונת רקע שכבר נטענה מהקאש המקומי (307c81e9)


## [3.11.1] - 2026-08-21

### Bug Fixes
- revert saved-card charge back to proven DebitKeva path (5522b07b)


## [3.11.0] - 2026-08-20

### Features
- **owner dashboard**: reorganize into categorized org detail drawer (7e9d9a03)
- call the Render backend for registerOrganization instead of the Firebase Cloud Function (a95dd845)
- make Nedarim credentials optional during registration (sionyx-web/src/components/settings/PaymentSettings.jsx) (5fdc2e80)
- make Nedarim credentials optional during registration (sionyx-web/src/services/paymentSettingsService.js) (066fc819)
- make Nedarim credentials optional during registration (sionyx-web/src/pages/LandingPage.jsx) (2ffc29eb)
- make Nedarim credentials optional during registration (functions/index.js) (977eb500)
- developer dashboard - view/edit any user's balance across all orgs (511f02c8)

### Bug Fixes
- **rtl**: tab gutter now lands on the visible side in RTL layout (ba92c496)
- **owner dashboard**: add spacing between drawer tab labels (2a28a8e6)
- **owner dashboard**: breathing room in overview cards + group/filter users table by org (2115a517)
- correct BRIDGE_BASE_URL fallback - understood-n5ok, not sionyx-payment-bridge (e9933624)

### Other
- try new chargeWithSavedCardRegular from kiosk UI (temp switch) (f45853d8)
- resolve conflict, keep origin/main's env-var-driven bridge URL (004bc408)
- route organization registration to Render bridge instead of Firebase Function (ad15e384)


## [3.10.2] - 2026-08-18

### Bug Fixes
- cache background image to disk, stop blanking out on network hiccups (45f12156)


## [3.10.1] - 2026-08-17

### Other
- remove payment debug/test screens now that real flow works (0ee2332e)


## [3.10.0] - 2026-08-17

### Features
- add DebitIframe=1 test button to payment test screen (4b109ccc)
- capture and forward card Tokef for real saved-card charging (47dc2bc7)


## [3.9.0] - 2026-08-13

### Features
- add DebitKeva StartFrom date-format variant buttons (c020d01a)
- add real-Tokef input to payment test screen (raw API + iframe) (00f3980e)

### Other
- remove dead-end strategy buttons from payment test screen (5af88975)


## [3.8.0] - 2026-08-11

### Features
- label each iframe token-test result with the PaymentType tried (ce7de5b3)

### Bug Fixes
- register payment-token-test.html in the MSI installer (41489c08)


## [3.7.0] - 2026-08-11

### Features
- add iframe-based token charge test (not raw API) (076afbd7)

### Bug Fixes
- don't escape Hebrew text as \uXXXX in payment test result panel (b02c074d)


## [3.6.0] - 2026-08-10

### Features
- add payment test screen to sidebar for debugging Nedarim charges (48f8b3ba)


## [3.5.13] - 2026-07-30

### Bug Fixes
- force real OS foreground on AuthWindow via AttachThreadInput (6e1209af)


## [3.5.12] - 2026-07-29

### Bug Fixes
- explicitly Activate() AuthWindow after Show() in the logout path (dab4ef62)


## [3.5.11] - 2026-07-29

### Bug Fixes
- reapply phone-field focus on Activated, not just Loaded (aee779f6)


## [3.5.10] - 2026-07-29

### Other
- log AppVersion and which login Enter handler actually fires (ad375f95)


## [3.5.9] - 2026-07-28

### Bug Fixes
- make login phone-field focus/Enter handling actually reliable (67195327)
- memoize DeviceInfo.GetDeviceId() to stop flaky test failures (18418ec0)
- Enter in login phone field advances to password instead of submitting (a0b9d397)
- never credit a purchase from CreateToken's OK alone (c78b7533)


## [3.5.8] - 2026-07-28

### Bug Fixes
- remove Timeout attribute unsupported by WiX v6 CustomAction schema (e70e7253)
- embed VC++ x64 redist in installer, auto-install if missing (6b007309)


## [3.5.7] - 2026-07-10

### Bug Fixes
- add CallBack param to TashlumBodedNew requests; check 4 possible token field names (ccdb6940)
- restore Out-Host on upload_release.py call (regression) (8ef8138f)
- restore Out-Host on upload_release.py call (regression) (40aba604)


## [3.5.6] - 2026-07-05

### Bug Fixes
- always use the Nedarim-confirmed iframe ApiValid (QWtE4M6uVn), not just when save-card is checked (c4cc8ae7)


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