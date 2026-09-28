using System.Reflection;
using System.Text.Json;
using FluentAssertions;
using SionyxKiosk.Services;

namespace SionyxKiosk.Tests.Services;

/// <summary>
/// Protects the dashboard shutdown/restart path. The bug class these guard
/// against: Firebase replays the still-present powerCommand/requested node
/// as an initial "put" every time a listener (re)starts - including the
/// first one after the very reboot the command caused. If that node was
/// still there (its delete used to run only AFTER shutdown.exe was
/// launched, inside a 5-second window, on a flaky network) and the kiosk
/// had forgotten it had already handled it, the kiosk restarted itself
/// again, forever.
///
/// Nothing here can touch the machine: shutdown.exe, the clock and the
/// registry are all replaced through the service's internal seams.
/// </summary>
public class RemoteCommandServiceTests
{
    private const long Now = 1_800_000_000_000;

    private sealed class Rig
    {
        public RemoteCommandService Service { get; }
        public MockHttpHandler Handler { get; }
        public List<string> Actions { get; } = new();
        public List<string> HttpMethodsSeenWhenActionRan { get; } = new();
        public long Persisted { get; set; }
        public int Saves { get; private set; }

        public Rig(long persisted = 0)
        {
            Persisted = persisted;
            Service = new RemoteCommandService(TestFirebaseFactory.CreateConfig());

            var (client, handler) = TestFirebaseFactory.Create();
            Handler = handler;

            // The service builds its own FirebaseClient (private readonly) -
            // swap in an authenticated one backed by the mock handler.
            typeof(RemoteCommandService)
                .GetField("_firebase", BindingFlags.NonPublic | BindingFlags.Instance)!
                .SetValue(Service, client);
            typeof(RemoteCommandService)
                .GetField("_computerId", BindingFlags.NonPublic | BindingFlags.Instance)!
                .SetValue(Service, "test-computer");

            Service.NowMs = () => Now;
            Service.LoadLastHandled = () => Persisted;
            Service.SaveLastHandled = v => { Persisted = v; Saves++; };
            Service.RunPowerAction = type =>
            {
                lock (Actions)
                {
                    HttpMethodsSeenWhenActionRan.AddRange(Handler.SentRequests.Select(r => r.Method.Method));
                    Actions.Add(type);
                }
            };
        }

        public void Send(string? type, long? requestedAt, string eventType = "put")
        {
            var payload = new Dictionary<string, object?>();
            if (type != null) payload["type"] = type;
            if (requestedAt != null) payload["requestedAt"] = requestedAt;
            Service.OnCommandRequested(eventType, TestFirebaseFactory.ToJsonElement(payload));
        }

        public async Task<bool> WaitForActionAsync(int expectedCount = 1, int timeoutMs = 3000)
        {
            var until = DateTime.UtcNow.AddMilliseconds(timeoutMs);
            while (DateTime.UtcNow < until)
            {
                lock (Actions) { if (Actions.Count >= expectedCount) return true; }
                await Task.Delay(20);
            }
            return false;
        }

        /// <summary>For "must NOT run" assertions: give the fire-and-forget
        /// task a fair chance to (wrongly) run before we check.</summary>
        public Task LetItSettleAsync() => Task.Delay(300);
    }

    // ── IsStale (pure) ───────────────────────────────────────────────

    [Theory]
    [InlineData(0, 0, false)]
    [InlineData(0, 600_000, false)]   // exactly at the limit is still fresh
    [InlineData(0, 600_001, true)]    // 1 ms past it is stale
    [InlineData(60_000, 0, false)]    // slightly in the future = clock skew, fine
    [InlineData(700_000, 0, true)]    // wildly in the future = bogus clock
    public void IsStale_UsesMaxAgeInBothDirections(long requestedAt, long now, bool expected)
    {
        RemoteCommandService.IsStale(requestedAt, now, TimeSpan.FromMinutes(10)).Should().Be(expected);
    }

    // ── Happy path ───────────────────────────────────────────────────

    [Theory]
    [InlineData("restart")]
    [InlineData("shutdown")]
    public async Task FreshCommand_IsExecutedOnce_AndRememberedBeforeAnythingElse(string type)
    {
        var rig = new Rig();

        rig.Send(type, Now - 1000);

        (await rig.WaitForActionAsync()).Should().BeTrue();
        rig.Actions.Should().Equal(type);
        rig.Persisted.Should().Be(Now - 1000);
        rig.Saves.Should().Be(1);
    }

    [Fact]
    public async Task RequestNode_IsDeleted_BeforeThePowerActionRuns()
    {
        var rig = new Rig();

        rig.Send("restart", Now);

        (await rig.WaitForActionAsync()).Should().BeTrue();
        // By the time shutdown.exe would be launched, the DELETE of
        // powerCommand/requested has already been sent.
        rig.HttpMethodsSeenWhenActionRan.Should().Contain("DELETE");
    }

    [Fact]
    public async Task DeleteFailing_DoesNotStopTheCommand()
    {
        var rig = new Rig();
        rig.Handler.WhenError("powerCommand/requested");

        rig.Send("shutdown", Now);

        (await rig.WaitForActionAsync()).Should().BeTrue();
        rig.Actions.Should().Equal("shutdown");
    }

    // ── The reboot-loop protections ──────────────────────────────────

    [Fact]
    public async Task SameCommandReplayedByTheSseStream_RunsOnlyOnce()
    {
        var rig = new Rig();

        rig.Send("restart", Now);
        rig.Send("restart", Now);
        rig.Send("restart", Now, eventType: "patch");
        await rig.WaitForActionAsync();
        await rig.LetItSettleAsync();

        rig.Actions.Should().Equal("restart");
    }

    [Fact]
    public async Task LeftoverNodeAfterReboot_IsNotExecutedAgain()
    {
        // New process after the reboot: nothing in memory, but the value
        // persisted by the previous process is the same command.
        var rig = new Rig(persisted: Now - 5000);

        rig.Send("restart", Now - 5000);
        await rig.LetItSettleAsync();

        rig.Actions.Should().BeEmpty();
    }

    [Fact]
    public async Task StaleCommand_IsNotExecuted_ButIsClearedAndRemembered()
    {
        var rig = new Rig();
        var elevenMinutesAgo = Now - 11 * 60 * 1000;

        rig.Send("restart", elevenMinutesAgo);
        await rig.LetItSettleAsync();

        rig.Actions.Should().BeEmpty();
        rig.Persisted.Should().Be(elevenMinutesAgo);
        rig.Handler.SentRequests.Select(r => r.Method.Method).Should().Contain("DELETE");
    }

    [Fact]
    public async Task NewCommand_WithAnOlderLookingTimestamp_StillRuns()
    {
        // Admin PCs can have skewed clocks; only the *same* command may be
        // treated as already handled - not "anything not newer than it".
        var rig = new Rig(persisted: Now);

        rig.Send("shutdown", Now - 60_000);

        (await rig.WaitForActionAsync()).Should().BeTrue();
        rig.Actions.Should().Equal("shutdown");
    }

    // ── Things that must be ignored, never throw ─────────────────────

    [Fact]
    public async Task UnknownCommandType_IsIgnored()
    {
        var rig = new Rig();

        rig.Send("format-disk", Now);
        await rig.LetItSettleAsync();

        rig.Actions.Should().BeEmpty();
    }

    [Fact]
    public async Task MalformedOrIrrelevantEvents_DoNothingAndDoNotThrow()
    {
        var rig = new Rig();

        var act = () =>
        {
            rig.Service.OnCommandRequested("put", null);
            rig.Service.OnCommandRequested("put", TestFirebaseFactory.ToJsonElement("just a string"));
            rig.Service.OnCommandRequested("put", TestFirebaseFactory.ToJsonElement(new { type = 5, requestedAt = Now }));
            rig.Service.OnCommandRequested("put", TestFirebaseFactory.ToJsonElement(new { type = "restart" }));      // no requestedAt
            rig.Service.OnCommandRequested("put", TestFirebaseFactory.ToJsonElement(new { requestedAt = Now }));     // no type
            rig.Send("restart", Now, eventType: "cancel");
            rig.Send("restart", Now, eventType: "keep-alive");
            rig.Send("restart", Now, eventType: "auth_revoked");
        };

        act.Should().NotThrow();
        await rig.LetItSettleAsync();
        rig.Actions.Should().BeEmpty();
        rig.Saves.Should().Be(0);
    }
}
