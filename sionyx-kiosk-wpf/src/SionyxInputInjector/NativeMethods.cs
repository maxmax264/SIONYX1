using System.Runtime.InteropServices;

namespace SionyxInputInjector;

/// <summary>
/// Raw Win32 calls this service needs. Kept in one file so the P/Invoke
/// surface is easy to audit - this process runs as LocalSystem, so any bug
/// here has full-machine reach.
///
/// UNTESTED: none of this has been run on a real Windows machine yet (this
/// was written and reviewed on a Linux sandbox with no way to compile or
/// exercise Win32 APIs). Treat every signature and constant here as
/// "looks right on paper" until it's actually been exercised - see the
/// project README before trusting this on a production kiosk.
/// </summary>
internal static class NativeMethods
{
    public const int SM_CXSCREEN = 0;
    public const int SM_CYSCREEN = 1;

    public const uint DESKTOP_SWITCHDESKTOP = 0x0100;
    public const uint DESKTOP_READOBJECTS = 0x0001;
    public const uint DESKTOP_WRITEOBJECTS = 0x0080;
    public const uint GENERIC_ALL = 0x10000000;

    public const int INPUT_MOUSE = 0;
    public const int INPUT_KEYBOARD = 1;
    public const uint MOUSEEVENTF_MOVE = 0x0001;
    public const uint MOUSEEVENTF_ABSOLUTE = 0x8000;
    public const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    public const uint MOUSEEVENTF_LEFTUP = 0x0004;
    public const uint KEYEVENTF_KEYUP = 0x0002;

    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr OpenInputDesktop(uint dwFlags, bool fInherit, uint dwDesiredAccess);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetThreadDesktop(IntPtr hDesktop);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool CloseDesktop(IntPtr hDesktop);

    [DllImport("user32.dll")]
    public static extern int GetSystemMetrics(int nIndex);

    [StructLayout(LayoutKind.Sequential)]
    public struct MOUSEINPUT
    {
        public int dx;
        public int dy;
        public uint mouseData;
        public uint dwFlags;
        public uint time;
        public IntPtr dwExtraInfo;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct KEYBDINPUT
    {
        public ushort wVk;
        public ushort wScan;
        public uint dwFlags;
        public uint time;
        public IntPtr dwExtraInfo;
    }

    [StructLayout(LayoutKind.Explicit)]
    public struct InputUnion
    {
        [FieldOffset(0)] public MOUSEINPUT mi;
        [FieldOffset(0)] public KEYBDINPUT ki;
    }

    [StructLayout(LayoutKind.Sequential)]
    public struct INPUT
    {
        public int type;
        public InputUnion u;
    }

    [DllImport("user32.dll", SetLastError = true)]
    public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);

    // Declared explicitly at process start (see Program.cs) rather than
    // via an embedded app manifest, since a .NET single-file/self-contained
    // publish doesn't reliably carry a custom manifest without extra csproj
    // wiring I can't verify without a real build. Without this, this
    // process would be subject to the exact same DPI-virtualization bug
    // that EnsureTightVncDpiCompatibility() fixes for tvnserver.exe -
    // GetSystemMetrics and SendInput would report/act on a scaled,
    // non-physical coordinate space instead of true screen pixels.
    public static readonly IntPtr DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = new IntPtr(-4);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetProcessDpiAwarenessContext(IntPtr value);
}
