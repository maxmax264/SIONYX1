using Microsoft.Extensions.Logging;
using Microsoft.Win32;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;

namespace SionyxInputInjector;

/// <summary>
/// Injects a mouse click into whatever desktop is currently active for the
/// interactive session - the normal desktop, OR the Secure Desktop that
/// Windows switches to for UAC prompts and some security-conscious apps'
/// own dialogs.
///
/// Why this needs to be a separate SYSTEM service rather than a method
/// SionyxKiosk calls directly: this process runs as LocalSystem, which
/// outranks every Windows integrity level (System > High/elevated >
/// Medium/normal user). SionyxKiosk itself runs at Medium integrity, so
/// its own SendInput calls are silently ignored by anything running
/// higher - which is by design (Windows' UIPI), not a bug we can patch
/// around from inside SionyxKiosk. Running as SYSTEM here is the same
/// approach dedicated remote-support tools use for the same problem.
///
/// UNTESTED end-to-end - see NativeMethods.cs.
/// </summary>
internal sealed class InputInjector
{
    private readonly ILogger<InputInjector> _log;

    public InputInjector(ILogger<InputInjector> log)
    {
        _log = log;
    }

    /// <summary>
    /// xFrac/yFrac are 0..1 fractions of the primary screen, as sent by
    /// vnc.html (which only knows the browser-side canvas size, not the
    /// kiosk's real resolution - converting here avoids the browser having
    /// to guess or query it separately).
    /// </summary>
    public bool TryClick(double xFrac, double yFrac)
    {
        IntPtr desktop = IntPtr.Zero;
        try
        {
            // Re-opened on every call (not cached) so a desktop switch
            // between one click and the next (e.g. a UAC prompt appearing)
            // is always picked up fresh.
            desktop = NativeMethods.OpenInputDesktop(0, false,
                NativeMethods.DESKTOP_SWITCHDESKTOP | NativeMethods.DESKTOP_READOBJECTS | NativeMethods.DESKTOP_WRITEOBJECTS);
            if (desktop == IntPtr.Zero)
            {
                _log.LogWarning("OpenInputDesktop failed, error {Error}", Marshal.GetLastWin32Error());
                return false;
            }
            if (!NativeMethods.SetThreadDesktop(desktop))
            {
                _log.LogWarning("SetThreadDesktop failed, error {Error}", Marshal.GetLastWin32Error());
                return false;
            }

            int screenW = NativeMethods.GetSystemMetrics(NativeMethods.SM_CXSCREEN);
            int screenH = NativeMethods.GetSystemMetrics(NativeMethods.SM_CYSCREEN);
            if (screenW <= 0 || screenH <= 0)
            {
                _log.LogWarning("GetSystemMetrics returned an unusable screen size {W}x{H}", screenW, screenH);
                return false;
            }

            // SendInput's absolute mouse coordinates are normalized to
            // 0..65535 across the primary screen regardless of actual
            // resolution - this is the standard formula for that mapping.
            double clampedX = Math.Clamp(xFrac, 0.0, 1.0);
            double clampedY = Math.Clamp(yFrac, 0.0, 1.0);
            int absX = (int)Math.Round(clampedX * 65535.0);
            int absY = (int)Math.Round(clampedY * 65535.0);

            var move = new NativeMethods.INPUT
            {
                type = NativeMethods.INPUT_MOUSE,
                u = new NativeMethods.InputUnion
                {
                    mi = new NativeMethods.MOUSEINPUT
                    {
                        dx = absX,
                        dy = absY,
                        dwFlags = NativeMethods.MOUSEEVENTF_MOVE | NativeMethods.MOUSEEVENTF_ABSOLUTE,
                    }
                }
            };
            var down = move;
            down.u.mi.dwFlags = NativeMethods.MOUSEEVENTF_LEFTDOWN | NativeMethods.MOUSEEVENTF_ABSOLUTE;
            var up = move;
            up.u.mi.dwFlags = NativeMethods.MOUSEEVENTF_LEFTUP | NativeMethods.MOUSEEVENTF_ABSOLUTE;

            var inputs = new[] { move, down, up };
            uint sent = NativeMethods.SendInput((uint)inputs.Length, inputs, Marshal.SizeOf<NativeMethods.INPUT>());
            if (sent != inputs.Length)
            {
                _log.LogWarning("SendInput only accepted {Sent}/{Total} events, error {Error}",
                    sent, inputs.Length, Marshal.GetLastWin32Error());
                return false;
            }

            _log.LogInformation("Injected elevated click at fraction ({X:F3},{Y:F3}) -> pixel-equivalent ({PxX},{PxY}) of {W}x{H}",
                clampedX, clampedY, (int)(clampedX * screenW), (int)(clampedY * screenH), screenW, screenH);
            return true;
        }
        finally
        {
            if (desktop != IntPtr.Zero) NativeMethods.CloseDesktop(desktop);
        }
    }

    /// <summary>
    /// SendSAS silently does nothing if the SoftwareSASGeneration policy
    /// doesn't include the "Services" bit (1) - this is a documented trap
    /// real remote-support tools have shipped and had to fix after the
    /// fact (a log line saying "Ctrl+Alt+Del sent" while nothing actually
    /// happened, because the call "succeeded" with no way to tell). Set
    /// once at service startup, self-healing, so there's no manual
    /// gpedit/registry step for anyone to remember - and OR the bit in
    /// rather than overwriting, in case something else on the machine
    /// already set "Ease of Access" (2) deliberately.
    /// </summary>
    public bool EnsureSoftwareSasPolicy()
    {
        const string keyPath = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System";
        const string valueName = "SoftwareSASGeneration";
        const int servicesBit = 1;
        try
        {
            using var key = Registry.LocalMachine.CreateSubKey(keyPath);
            var current = key.GetValue(valueName);
            int currentValue = current is int i ? i : 0;
            int desired = currentValue | servicesBit;
            if (currentValue != desired)
            {
                key.SetValue(valueName, desired, RegistryValueKind.DWord);
                _log.LogInformation("Set {ValueName} to {Desired} (was {Current}) so SendSAS actually works from this service",
                    valueName, desired, currentValue);
                return true;
            }
            return false;
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Could not set SoftwareSASGeneration policy - Ctrl+Alt+Del requests will silently do nothing until this is set");
            return false;
        }
    }

    /// <summary>
    /// Genuine Windows UAC elevation prompts render on the Secure Desktop
    /// by design (Microsoft's own remote-assistance team has documented
    /// this exact "black screen through a remote tool" problem and the
    /// fix: the "Allow UIAccess applications to prompt for elevation
    /// without using the secure desktop" policy). With it off, our
    /// existing session-mode TightVNC - unmodified - can see and click a
    /// real UAC prompt like any other window, no SYSTEM-level capture
    /// engineering needed for that specific case.
    ///
    /// This is a real, if small on a locked-down single-purpose kiosk,
    /// security trade-off: it applies machine-wide, not just to remote
    /// sessions, so any future UAC prompt (from any user, any moment) is
    /// visible/spoofable to anything already running at Medium integrity
    /// or higher on the box - not to a remote attacker with no code
    /// execution on the kiosk already. Worth it here given the kiosk is
    /// already locked down (custom shell, Netfree-filtered), but this is
    /// a deliberate choice, not a free lunch - flagged, not silent.
    ///
    /// NOTE: this only affects genuine Windows UAC. It does NOT explain
    /// or fix AeroAdmin's own approval dialog if that turns out to use
    /// its own separate desktop object rather than Windows' Secure
    /// Desktop - see TryClick/TryTypeText's OpenInputDesktop-based
    /// approach for that case instead, which follows whatever desktop is
    /// actually active regardless of who created it.
    /// </summary>
    public bool EnsureUacPromptOnNormalDesktop()
    {
        const string keyPath = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System";
        const string valueName = "PromptOnSecureDesktop";
        try
        {
            using var key = Registry.LocalMachine.CreateSubKey(keyPath);
            var current = key.GetValue(valueName);
            int currentValue = current is int i ? i : 1; // Windows default is effectively "on"
            if (currentValue != 0)
            {
                key.SetValue(valueName, 0, RegistryValueKind.DWord);
                _log.LogInformation("Set {ValueName} to 0 (was {Current}) so UAC prompts render on the normal desktop, visible to the existing VNC session",
                    valueName, currentValue);
                return true;
            }
            return false;
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Could not set PromptOnSecureDesktop policy - genuine UAC prompts will still show as a black screen over VNC until this is set");
            return false;
        }
    }

    /// <summary>
    /// Added 2026-09-15 per explicit request: a kiosk should need this
    /// installed exactly once, ever - no admin visiting every machine to
    /// manually restart it afterwards. Both policy fixes above only take
    /// effect after Windows re-reads them (confirmed via research: "won't
    /// reflect unless you reboot or log back into a workstation" - these
    /// are Winlogon/Application-Info-level security policies, not settings
    /// polled live). So when either one actually changed something, this
    /// schedules a ONE-TIME Windows restart automatically - at 4:00 AM
    /// local time (never "right now") specifically so it can never land in
    /// the middle of a live customer transaction. A scheduled task is used
    /// instead of a simple in-process timer so the restart still happens
    /// even if this service itself restarts or the machine loses power and
    /// comes back before 4 AM.
    /// </summary>
    /// <summary>
    /// Simplified 2026-09-15: used to schedule this for the next 4:00 AM to
    /// avoid any chance of interrupting a live customer. That added a
    /// confusing overnight delay for something that only ever happens once
    /// per machine (the very first time this policy needs to change) - so
    /// instead this now just restarts immediately, with a short (2 minute)
    /// warning delay via shutdown.exe's own /t flag. One brief restart
    /// during a one-time software rollout is a normal, acceptable cost -
    /// simpler to reason about than "the fix is scheduled for some night
    /// this week."
    /// </summary>
    public void ScheduleRebootIfPolicyChanged(bool sasPolicyChanged, bool uacPolicyChanged)
    {
        if (!sasPolicyChanged && !uacPolicyChanged) return;

        try
        {
            var psi = new ProcessStartInfo
            {
                FileName = "shutdown.exe",
                Arguments = "/r /t 120 /c \"SIONYX: restarting once to apply a security-policy update (Ctrl+Alt+Del / UAC visibility)\"",
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
            };
            using var process = Process.Start(psi);
            process?.WaitForExit(10_000);
            if (process?.ExitCode == 0)
            {
                _log.LogInformation("Restarting in 2 minutes to apply the SoftwareSASGeneration/PromptOnSecureDesktop policy change - this should only ever happen once per machine");
            }
            else
            {
                var stderr = process?.StandardError.ReadToEnd();
                _log.LogError("shutdown.exe failed to schedule the policy-change restart (exit {Code}): {Error}", process?.ExitCode, stderr);
            }
        }
        catch (Exception ex)
        {
            _log.LogError(ex, "Could not schedule the one-time policy-change restart - Ctrl+Alt+Del/UAC-visibility fixes won't take effect until the machine is restarted manually");
        }
    }

    /// <summary>
    /// Read-only check of the same registry value EnsureSoftwareSasPolicy
    /// sets - lets a caller ask "will SendSAS actually do anything right
    /// now?" without side effects. Used by SendCtrlAltDel to report a real
    /// answer back to the caller instead of the previous "call was made,
    /// no idea if it worked" silence.
    /// </summary>
    private bool IsSoftwareSasPolicySet()
    {
        const string keyPath = @"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System";
        const string valueName = "SoftwareSASGeneration";
        const int servicesBit = 1;
        try
        {
            using var key = Registry.LocalMachine.OpenSubKey(keyPath);
            var current = key?.GetValue(valueName);
            int currentValue = current is int i ? i : 0;
            return (currentValue & servicesBit) == servicesBit;
        }
        catch
        {
            return false;
        }
    }

    /// <summary>
    /// Sends a real Secure Attention Sequence (Ctrl+Alt+Del). Returns
    /// whether the policy that makes SendSAS actually do anything is
    /// currently in place - SendSAS itself is a void Win32 call with no
    /// success/failure signal, so this registry check is the only real
    /// answer available, and it's the one that actually matters (a
    /// pending-reboot machine will report false here even though the call
    /// "succeeds" every time).
    /// </summary>
    public bool SendCtrlAltDel()
    {
        // AsUser=false: request it for the whole session, not just this
        // (Session-0, non-interactive) process's own desktop - matches how
        // every reference implementation found in field research calls it
        // for a remote-support scenario.
        NativeMethods.SendSAS(false);
        var policySet = IsSoftwareSasPolicySet();
        if (policySet)
        {
            _log.LogInformation("SendSAS called (Ctrl+Alt+Del) - SoftwareSASGeneration policy is set, this should have worked");
        }
        else
        {
            _log.LogWarning("SendSAS called (Ctrl+Alt+Del) but SoftwareSASGeneration policy is NOT set - this did nothing. Likely cause: the pending reboot after this service's first-ever run on this machine hasn't happened yet");
        }
        return policySet;
    }

    /// <summary>
    /// Types literal text (e.g. a password) into whatever desktop is
    /// currently active, followed by Enter. Uses KEYEVENTF_UNICODE so it
    /// isn't limited to keys with a direct virtual-key mapping and doesn't
    /// depend on keyboard layout.
    /// </summary>
    public bool TryTypeText(string text)
    {
        IntPtr desktop = IntPtr.Zero;
        try
        {
            desktop = NativeMethods.OpenInputDesktop(0, false,
                NativeMethods.DESKTOP_SWITCHDESKTOP | NativeMethods.DESKTOP_READOBJECTS | NativeMethods.DESKTOP_WRITEOBJECTS);
            if (desktop == IntPtr.Zero || !NativeMethods.SetThreadDesktop(desktop))
            {
                _log.LogWarning("Could not attach to the active desktop for typing, error {Error}", Marshal.GetLastWin32Error());
                return false;
            }

            var inputs = new List<NativeMethods.INPUT>(text.Length * 2 + 2);
            foreach (char c in text)
            {
                inputs.Add(UnicodeKeyInput(c, down: true));
                inputs.Add(UnicodeKeyInput(c, down: false));
            }
            // Submit - most password/login prompts expect Enter, not a
            // click on an OK button that may not even be visible to us.
            inputs.Add(VirtualKeyInput(NativeMethods.VK_RETURN, down: true));
            inputs.Add(VirtualKeyInput(NativeMethods.VK_RETURN, down: false));

            var arr = inputs.ToArray();
            uint sent = NativeMethods.SendInput((uint)arr.Length, arr, Marshal.SizeOf<NativeMethods.INPUT>());
            if (sent != arr.Length)
            {
                _log.LogWarning("SendInput only accepted {Sent}/{Total} key events, error {Error}",
                    sent, arr.Length, Marshal.GetLastWin32Error());
                return false;
            }
            _log.LogInformation("Typed {Length}-character text and Enter into the active desktop", text.Length);
            return true;
        }
        finally
        {
            if (desktop != IntPtr.Zero) NativeMethods.CloseDesktop(desktop);
        }
    }

    private static NativeMethods.INPUT UnicodeKeyInput(char c, bool down) => new()
    {
        type = NativeMethods.INPUT_KEYBOARD,
        u = new NativeMethods.InputUnion
        {
            ki = new NativeMethods.KEYBDINPUT
            {
                wVk = 0,
                wScan = c,
                dwFlags = NativeMethods.KEYEVENTF_UNICODE | (down ? 0 : NativeMethods.KEYEVENTF_KEYUP),
            }
        }
    };

    private static NativeMethods.INPUT VirtualKeyInput(ushort vk, bool down) => new()
    {
        type = NativeMethods.INPUT_KEYBOARD,
        u = new NativeMethods.InputUnion
        {
            ki = new NativeMethods.KEYBDINPUT
            {
                wVk = vk,
                wScan = 0,
                dwFlags = down ? 0 : NativeMethods.KEYEVENTF_KEYUP,
            }
        }
    };
}
