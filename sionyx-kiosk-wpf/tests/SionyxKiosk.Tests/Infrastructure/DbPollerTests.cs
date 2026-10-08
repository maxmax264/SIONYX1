using System.Text.Json;
using FluentAssertions;
using SionyxKiosk.Infrastructure;

namespace SionyxKiosk.Tests.Infrastructure;

/// <summary>
/// DbPoller replaces permanent SSE connections (which count against Firebase's
/// simultaneous-connection cap) with short GETs. These tests pin the contract
/// the callers rely on: first value is delivered, unchanged values are not
/// re-delivered, changed values are, and failures are silent and non-fatal.
/// </summary>
public class DbPollerTests
{
    private const string Node = "computers/c1/powerCommand/requested";

    private static DbPoller Create(FirebaseClient client, List<JsonElement?> seen, bool absolute = false, string path = Node)
        => new(client, path, absolute, TimeSpan.FromSeconds(30), v => seen.Add(v), TimeSpan.Zero);

    [Fact]
    public async Task FirstPoll_DeliversCurrentValue()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenRaw(Node, "{\"type\":\"restart\",\"requestedAt\":5}");
        var seen = new List<JsonElement?>();

        await Create(client, seen).PollOnceAsync(CancellationToken.None);

        seen.Should().HaveCount(1);
        seen[0]!.Value.GetProperty("requestedAt").GetInt64().Should().Be(5);
    }

    [Fact]
    public async Task UnchangedValue_IsNotDeliveredAgain()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenRaw(Node, "{\"type\":\"restart\",\"requestedAt\":5}");
        var seen = new List<JsonElement?>();
        var poller = Create(client, seen);

        await poller.PollOnceAsync(CancellationToken.None);
        await poller.PollOnceAsync(CancellationToken.None);
        await poller.PollOnceAsync(CancellationToken.None);

        seen.Should().HaveCount(1);
    }

    [Fact]
    public async Task ChangedValue_IsDelivered()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenRaw(Node, "{\"type\":\"restart\",\"requestedAt\":5}");
        var seen = new List<JsonElement?>();
        var poller = Create(client, seen);

        await poller.PollOnceAsync(CancellationToken.None);
        handler.ClearHandlers();
        handler.WhenRaw(Node, "{\"type\":\"shutdown\",\"requestedAt\":9}");
        await poller.PollOnceAsync(CancellationToken.None);

        seen.Should().HaveCount(2);
        seen[1]!.Value.GetProperty("type").GetString().Should().Be("shutdown");
    }

    [Fact]
    public async Task MissingNode_DeliversJsonNullOnce()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenRaw(Node, "null");
        var seen = new List<JsonElement?>();
        var poller = Create(client, seen);

        await poller.PollOnceAsync(CancellationToken.None);
        await poller.PollOnceAsync(CancellationToken.None);

        seen.Should().HaveCount(1);
        seen[0]!.Value.ValueKind.Should().Be(JsonValueKind.Null);
    }

    [Fact]
    public async Task FailedRead_DeliversNothing_AndDoesNotThrow()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenError(Node);
        var seen = new List<JsonElement?>();

        var act = async () => await Create(client, seen).PollOnceAsync(CancellationToken.None);

        await act.Should().NotThrowAsync();
        seen.Should().BeEmpty();
    }

    [Fact]
    public async Task NetworkException_DeliversNothing_AndDoesNotThrow()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenThrows(Node);
        var seen = new List<JsonElement?>();

        var act = async () => await Create(client, seen).PollOnceAsync(CancellationToken.None);

        await act.Should().NotThrowAsync();
        seen.Should().BeEmpty();
    }

    [Fact]
    public async Task FailureThenRecovery_DeliversOnceRecovered()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenError(Node);
        var seen = new List<JsonElement?>();
        var poller = Create(client, seen);

        await poller.PollOnceAsync(CancellationToken.None);
        handler.ClearHandlers();
        handler.WhenRaw(Node, "{\"requestedAt\":7}");
        await poller.PollOnceAsync(CancellationToken.None);

        seen.Should().HaveCount(1);
    }

    [Fact]
    public async Task NoSession_SendsNoRequest()
    {
        var (client, handler) = TestFirebaseFactory.CreateUnauthenticated();
        var seen = new List<JsonElement?>();

        await Create(client, seen).PollOnceAsync(CancellationToken.None);

        seen.Should().BeEmpty();
        handler.SentRequests.Should().BeEmpty();
    }

    [Fact]
    public async Task AbsolutePath_IsNotOrgPrefixed()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenRaw("systemSettings/logShipping", "{}");
        var seen = new List<JsonElement?>();

        await Create(client, seen, absolute: true, path: "systemSettings/logShipping")
            .PollOnceAsync(CancellationToken.None);

        var url = handler.SentRequests.Last().RequestUri!.ToString();
        url.Should().Contain("/systemSettings/logShipping.json");
        url.Should().NotContain("organizations/");
        seen.Should().HaveCount(1);
    }

    [Fact]
    public async Task OrgPath_IsOrgPrefixed()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        var seen = new List<JsonElement?>();

        await Create(client, seen).PollOnceAsync(CancellationToken.None);

        handler.SentRequests.Last().RequestUri!.ToString().Should().Contain("organizations/");
    }

    [Fact]
    public async Task ThrowingCallback_IsSwallowed_AndNotRedelivered()
    {
        var (client, handler) = TestFirebaseFactory.Create();
        handler.WhenRaw(Node, "{\"requestedAt\":1}");
        var calls = 0;
        var poller = new DbPoller(client, Node, false, TimeSpan.FromSeconds(30),
            _ => { calls++; throw new InvalidOperationException("boom"); }, TimeSpan.Zero);

        await poller.PollOnceAsync(CancellationToken.None);
        await poller.PollOnceAsync(CancellationToken.None);

        calls.Should().Be(1);
    }

    [Fact]
    public void Stop_MarksNotRunning_AndIsIdempotent()
    {
        var (client, _) = TestFirebaseFactory.Create();
        var poller = client.DbPoll(Node, TimeSpan.FromSeconds(30), _ => { });

        poller.IsRunning.Should().BeTrue();
        poller.Stop();
        poller.IsRunning.Should().BeFalse();
        poller.Invoking(p => p.Stop()).Should().NotThrow();
    }
}
