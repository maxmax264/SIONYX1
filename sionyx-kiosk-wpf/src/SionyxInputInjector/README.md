# SionyxInputInjector

Added 2026-09-14. A minimal Windows Service that runs as **LocalSystem** and
injects a single mouse click on request, over a local named pipe. It exists
for exactly one problem: some UI (AeroAdmin's connection-approval dialog,
Windows UAC/Secure-Desktop prompts) ignores input injected by a process
running at a lower privilege level than the target - which is what
`VncRelayService` + TightVNC does today (runs as the interactive kiosk
user, Medium integrity). Running the injector as SYSTEM outranks that
restriction, the same way dedicated remote-support tools handle it.

**This is genuinely new infrastructure** - the first Windows Service in
this codebase (everything else runs as a normal process in the kiosk's own
session). It was written and reviewed without access to a Windows machine
to compile, install, or run it, so none of the following has actually been
verified:

- That the project builds cleanly (`dotnet publish` for `net8.0-windows`,
  worker-service SDK, the `NamedPipeServerStreamAcl` API surface).
- That `OpenInputDesktop`/`SetThreadDesktop` correctly reach the Secure
  Desktop for a UAC prompt (vs. only the normal interactive desktop).
- That the pipe's ACL actually grants the interactive user connect access
  in practice, not just on paper.
- That a SYSTEM-injected click really does get through where a
  Medium-integrity one didn't - the UIPI theory fits the symptoms
  described (Chrome Remote Desktop, which runs as SYSTEM, works; our
  session-mode TightVNC, which doesn't, fails on the same dialog) but
  hasn't been confirmed against the actual dialog.

**Before relying on this on any real kiosk:**

1. Build and publish this project on a real Windows dev machine.
2. Install it as a service manually to test first:
   `sc create SionyxInputInjector binPath= "C:\path\to\SionyxInputInjector.exe" start= auto obj= LocalSystem`
   `sc start SionyxInputInjector`
3. Confirm `VncRelayService`'s control-channel connection reaches it (see
   `RunControlChannelAsync` in `VncRelayService.cs`) and that a real click
   sent from the "V מוגבר" button in the VNC toolbar actually lands.
4. Only then wire `install-input-injector.ps1` into the MSI
   (`CA_InstallInputInjector` in `Package.wxs`) for fleet rollout.

If step 2-3 don't work, the fallback is a physical input device at the
kiosk (e.g. a small USB HID dongle) for the rare case an elevated dialog
needs a real human click - genuinely bypassing software injection entirely
rather than continuing to fight UIPI/Secure Desktop from software.
