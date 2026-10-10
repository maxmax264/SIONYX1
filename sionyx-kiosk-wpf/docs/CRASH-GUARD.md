# Crash Guard (SionyxGuard)

Replaces the "watchdog" idea in `CRASH-RECOVERY.md` for the *security* half of the problem:
if `SionyxKiosk.exe` crashes, freezes, or is killed, the Windows desktop must never be left
usable. (Session-time recovery - `session.json` / Firebase sync - is unchanged.)

## Why a SYSTEM service
The kiosk app runs as the logged-on user with Explorer as the shell. Everything that protects
the desktop (`ProcessRestrictionService`, keyboard hook, lock UI) lives *inside* that process
and dies with it. `SionyxGuard` is a separate `LocalSystem` auto-start service (same MSI
pattern as `SionyxInputInjector`), so a normal user cannot stop it and it needs nothing from the app.

## How it works
1. `GuardBeacon` (in the app) writes `C:\ProgramData\SIONYX\guard\app.beat` every 2s: pid, start time,
   last time the UI thread answered a ping, `ready`, `kiosk`. On intentional exit (`App.OnExit`) it writes `app.clean`.
2. The service ticks every second and classifies the app (`GuardPolicy.Classify`, pure + unit-tested):
   `Healthy / Starting / CleanExit / Maintenance / Crashed / Hung / NeverStarted`.
   - **Crashed**: process gone, no clean-exit marker. **Hung**: UI thread or whole process silent >15s,
     or not `ready` within 60s. **NeverStarted**: user logged on but no app after 90s.
   - Installer running (`Global\_MSIExecute` mutex) = maintenance, never a fault. Runs without `--kiosk` are ignored.
3. On a fault it **locks at once**: runs `SionyxGuard.exe --lock` in the user's session
   (black topmost window on every monitor, keyboard hook), and kills `taskmgr/cmd/powershell/regedit/mmc` while locked.
4. It **relaunches** the app (`--kiosk`, elevated token if the user has one), kills a hung one first,
   and lifts the lock only when a *new* healthy heartbeat arrives.
5. No recovery after 2 launches x 20s -> **forced logoff** (`WTSLogoffSession`); AutoAdminLogon + the logon
   task bring everything back clean. More than 3 forced logoffs in 15 min -> **fail closed** (stays locked, logged).

Fail-safes: the lock window exits by itself if `lock.flag` stops being refreshed (a dead guard can't leave a
permanent lock); the lock is released when the service stops; the service restarts itself on failure.

## Operations
- Logs: `C:\ProgramData\SIONYX\logs\guard-YYYYMMDD.log` (search for `INCIDENT`).
- **Kill switch**: `reg add HKLM\SOFTWARE\SIONYX\Guard /v Disabled /t REG_DWORD /d 1 /f` (HKLM, so users can't set it).
  Remove the value or set 0 to re-enable.
- Optional `HKLM\SOFTWARE\SIONYX\Guard\AppPath` overrides the kiosk exe path (default `..\SionyxKiosk.exe` relative to the guard).
- Build: `build.ps1` publishes it to `installer\guard\SionyxGuard\` and passes `HasGuard=true` to WiX.

## Verification status
- `GuardPolicy` / `Heartbeat`: 35 unit tests in `tests/SionyxGuard.Tests` pass.
- The service, `CreateProcessAsUser` launcher, lock screen, WiX component and app hooks were written without a
  Windows machine and **have not been compiled or run**. Before rolling out: build, install on ONE test kiosk,
  then (a) `taskkill /F /IM SionyxKiosk.exe` -> lock appears, app returns, lock lifts; (b) suspend the process
  (`pssuspend`) -> hang detected; (c) admin exit and an auto-update do NOT trigger a lock.
