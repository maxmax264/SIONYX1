using System.Runtime.InteropServices;
using Serilog;

namespace SionyxGuard;

/// <summary>Starts a process on the interactive desktop of a user session from the SYSTEM service.</summary>
internal static class SessionLauncher
{
    private static readonly ILogger Logger = Log.ForContext(typeof(SessionLauncher));

    public static int? Launch(uint sessionId, string exePath, string arguments)
    {
        IntPtr userToken = IntPtr.Zero, primary = IntPtr.Zero, env = IntPtr.Zero;
        try
        {
            if (!Native.WTSQueryUserToken(sessionId, out userToken))
            {
                Logger.Warning("WTSQueryUserToken failed for session {Session}: {Err}", sessionId, Marshal.GetLastWin32Error());
                return null;
            }

            // Prefer the elevated half of a split token so the app runs exactly like the
            // RunLevel=HighestAvailable logon task would run it. Standard users have no
            // linked token - the call just fails and we use the normal token.
            var source = userToken;
            IntPtr linked = IntPtr.Zero;
            if (Native.GetTokenInformation(userToken, Native.TokenLinkedToken, out linked, IntPtr.Size, out _) && linked != IntPtr.Zero)
                source = linked;

            try
            {
                if (!Native.DuplicateTokenEx(source, Native.MaximumAllowed, IntPtr.Zero, Native.SecurityImpersonation, Native.TokenPrimary, out primary))
                {
                    Logger.Warning("DuplicateTokenEx failed: {Err}", Marshal.GetLastWin32Error());
                    return null;
                }
            }
            finally
            {
                if (linked != IntPtr.Zero) Native.CloseHandle(linked);
            }

            if (!Native.CreateEnvironmentBlock(out env, primary, false)) env = IntPtr.Zero;

            var si = new Native.STARTUPINFO { cb = Marshal.SizeOf<Native.STARTUPINFO>(), lpDesktop = @"winsta0\default" };
            var cmd = string.IsNullOrEmpty(arguments) ? $"\"{exePath}\"" : $"\"{exePath}\" {arguments}";
            var cwd = Path.GetDirectoryName(exePath);

            if (!Native.CreateProcessAsUser(primary, null, cmd, IntPtr.Zero, IntPtr.Zero, false,
                    Native.CreateUnicodeEnvironment, env, cwd, ref si, out var pi))
            {
                Logger.Warning("CreateProcessAsUser failed for {Exe}: {Err}", exePath, Marshal.GetLastWin32Error());
                return null;
            }

            Native.CloseHandle(pi.hThread);
            Native.CloseHandle(pi.hProcess);
            return pi.dwProcessId;
        }
        catch (Exception ex)
        {
            Logger.Error(ex, "Launch of {Exe} failed", exePath);
            return null;
        }
        finally
        {
            if (env != IntPtr.Zero) Native.DestroyEnvironmentBlock(env);
            if (primary != IntPtr.Zero) Native.CloseHandle(primary);
            if (userToken != IntPtr.Zero) Native.CloseHandle(userToken);
        }
    }
}
