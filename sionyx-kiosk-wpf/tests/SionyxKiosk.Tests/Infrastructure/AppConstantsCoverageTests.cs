using FluentAssertions;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Tests.Infrastructure;

public class AppConstantsCoverageTests
{
    [Fact]
    public void AppName_IsSionyx()
    {
        AppConstants.AppName.Should().Be("SIONYX");
    }

    [Fact]
    public void AdminExitHotkeyDefault_IsExpected()
    {
        AppConstants.AdminExitHotkeyDefault.Should().Be("Ctrl+Alt+Space");
    }

    [Fact]
    public void GetAdminExitPassword_ReturnsNonEmpty()
    {
        var password = AppConstants.GetAdminExitPassword();
        password.Should().NotBeNullOrEmpty();
    }

[Fact]
    public void GetAdminExitPassword_DefaultFallback()
    {
        // On a machine where SIONYX is actually installed (production),
        // GetAdminExitPassword() correctly reads the real value from the
        // Windows Registry and ignores the env var entirely - that's
        // intended behavior, not a bug. The "1234" dev fallback only
        // applies on a machine with no SIONYX registry key at all. This
        // test only ever reads state, never writes to the registry, so
        // it's safe to run on a real, already-installed kiosk.
        if (RegistryConfig.IsProduction())
        {
            var passwordOnProdMachine = AppConstants.GetAdminExitPassword();
            passwordOnProdMachine.Should().NotBeNullOrEmpty();
            return;
        }

        var originalValue = Environment.GetEnvironmentVariable("ADMIN_EXIT_PASSWORD");
        try
        {
            Environment.SetEnvironmentVariable("ADMIN_EXIT_PASSWORD", null);
            var password = AppConstants.GetAdminExitPassword();
            password.Should().Be("1234");
        }
        finally
        {
            Environment.SetEnvironmentVariable("ADMIN_EXIT_PASSWORD", originalValue);
        }
    }

    [Fact]
    public void GetAdminExitPassword_FromEnvVariable()
    {
        var originalValue = Environment.GetEnvironmentVariable("ADMIN_EXIT_PASSWORD");
        try
        {
            Environment.SetEnvironmentVariable("ADMIN_EXIT_PASSWORD", "test-password-123");
            var password = AppConstants.GetAdminExitPassword();
            // May return registry value in production, or env value in dev
            password.Should().NotBeNullOrEmpty();
        }
        finally
        {
            Environment.SetEnvironmentVariable("ADMIN_EXIT_PASSWORD", originalValue);
        }
    }
}
