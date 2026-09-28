using FluentAssertions;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Tests.Infrastructure;

[Collection("AnonymousAuthCoordinator")]
public class AnonymousAuthCoordinatorTests
{
    private static readonly Random Rng = new(42);

    public AnonymousAuthCoordinatorTests() => AnonymousAuthCoordinator.ResetForTests();

    [Theory]
    [InlineData(1, 60, 72)]
    [InlineData(2, 120, 144)]
    [InlineData(3, 240, 288)]
    [InlineData(4, 480, 576)]
    public void NextCooldown_DoublesWithJitterUpTo20Percent(int failures, int min, int max)
    {
        var s = AnonymousAuthCoordinator.NextCooldown(failures, Rng).TotalSeconds;
        s.Should().BeInRange(min, max);
    }

    [Fact]
    public void NextCooldown_IsCappedAtTenMinutesPlusJitter()
    {
        var s = AnonymousAuthCoordinator.NextCooldown(50, Rng).TotalSeconds;
        s.Should().BeInRange(600, 720);
    }

    [Fact]
    public void NextCooldown_ZeroOrNegativeFailures_TreatedAsFirst()
    {
        AnonymousAuthCoordinator.NextCooldown(0, Rng).TotalSeconds.Should().BeInRange(60, 72);
    }

    [Fact]
    public void RegisterFailure_StartsCooldown_AndRemembersError()
    {
        AnonymousAuthCoordinator.RegisterFailure("TOO_MANY_ATTEMPTS", Rng);

        AnonymousAuthCoordinator.CooldownRemaining.Should().BeGreaterThan(TimeSpan.FromSeconds(30));
        AnonymousAuthCoordinator.LastError.Should().Be("TOO_MANY_ATTEMPTS");
        AnonymousAuthCoordinator.FailureCount.Should().Be(1);
    }

    [Fact]
    public void RegisterFailure_Repeated_GrowsCooldown()
    {
        AnonymousAuthCoordinator.RegisterFailure("x", Rng);
        var first = AnonymousAuthCoordinator.CooldownRemaining;
        AnonymousAuthCoordinator.RegisterFailure("x", Rng);
        AnonymousAuthCoordinator.CooldownRemaining.Should().BeGreaterThan(first);
    }

    [Fact]
    public void RegisterSuccess_ClearsCooldownAndFailures()
    {
        AnonymousAuthCoordinator.RegisterFailure("x", Rng);
        AnonymousAuthCoordinator.RegisterSuccess(
            new AnonymousAuthCoordinator.Session("id", "refresh", "uid", DateTime.UtcNow.AddHours(1)));

        AnonymousAuthCoordinator.CooldownRemaining.Should().Be(TimeSpan.Zero);
        AnonymousAuthCoordinator.FailureCount.Should().Be(0);
        AnonymousAuthCoordinator.LastError.Should().BeNull();
        AnonymousAuthCoordinator.Cached.Should().NotBeNull();
        AnonymousAuthCoordinator.ClearPersisted(); // don't leave a fake token in the dev machine's registry
    }

    [Fact]
    public void SignInRetryMs_UsesBaseWhenNoCooldown()
    {
        FirebaseClient.SignInRetryMs(30).Should().Be(30_000);
    }

    [Fact]
    public void SignInRetryMs_WaitsForCooldownWhenLonger()
    {
        AnonymousAuthCoordinator.RegisterFailure("x", Rng); // >= 60s
        FirebaseClient.SignInRetryMs(30).Should().BeGreaterThan(60_000);
    }

    [Fact]
    public void PickStartupJitter_IsWithinBounds()
    {
        for (var i = 0; i < 50; i++)
            AnonymousAuthCoordinator.PickStartupJitter(Rng).TotalSeconds.Should().BeInRange(0, 180);
    }
}
