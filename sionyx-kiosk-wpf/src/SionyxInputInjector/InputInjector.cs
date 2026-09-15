using Microsoft.Extensions.Logging;
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
}
