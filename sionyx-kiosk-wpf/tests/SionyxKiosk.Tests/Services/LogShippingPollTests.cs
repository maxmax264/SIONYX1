using System.Text.Json;
using FluentAssertions;
using SionyxKiosk.Services;

namespace SionyxKiosk.Tests.Services;

/// <summary>
/// LogShippingControlService now reads systemSettings/logShipping with one
/// poll instead of three permanent SSE streams. The split of the polled node
/// into config / triggerAll / triggers/{id} must tolerate every shape the node
/// can have, including none at all.
/// </summary>
public class LogShippingPollTests
{
    private static LogShippingControlService Create()
    {
        var (client, _) = TestFirebaseFactory.Create();
        return new LogShippingControlService(client, Path.GetTempPath());
    }

    private static JsonElement? Json(string raw) => JsonSerializer.Deserialize<JsonElement>(raw);

    [Fact]
    public void NullRoot_DoesNotThrow()
        => Create().Invoking(s => s.OnLogShippingPolled(null)).Should().NotThrow();

    [Fact]
    public void JsonNullRoot_DoesNotThrow()
        => Create().Invoking(s => s.OnLogShippingPolled(Json("null"))).Should().NotThrow();

    [Fact]
    public void EmptyObject_DoesNotThrow()
        => Create().Invoking(s => s.OnLogShippingPolled(Json("{}"))).Should().NotThrow();

    [Fact]
    public void NonObjectRoot_DoesNotThrow()
        => Create().Invoking(s => s.OnLogShippingPolled(Json("42"))).Should().NotThrow();

    [Fact]
    public void TriggersOfOtherComputers_AreIgnored()
        => Create().Invoking(s => s.OnLogShippingPolled(Json("{\"triggers\":{\"someone-else\":123}}"))).Should().NotThrow();

    [Fact]
    public void RepeatedIdenticalConfig_DoesNotThrow()
    {
        var s = Create();
        var cfg = Json("{\"config\":{\"mode\":\"internal\",\"autoEnabled\":false}}");
        s.Invoking(x => { x.OnLogShippingPolled(cfg); x.OnLogShippingPolled(cfg); }).Should().NotThrow();
    }
}
