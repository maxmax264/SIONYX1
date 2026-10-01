using FluentAssertions;
using SionyxKiosk.Services;

namespace SionyxKiosk.Tests.Services;

public class LogShippingDumpFilterTests
{
    [Fact]
    public void FilterDumpLines_DropsDebugEntries_KeepsInformationAndAbove()
    {
        var log = string.Join("\n",
            "2026-10-01 10:00:00.000 +03:00 [DBG] SSE keep-alive received for x",
            "2026-10-01 10:00:01.000 +03:00 [INF] Update available",
            "2026-10-01 10:00:02.000 +03:00 [DBG] DB raw read: systemSettings/failover",
            "2026-10-01 10:00:03.000 +03:00 [WRN] Something odd");

        var kept = LogShippingControlService.FilterDumpLines(log, 100);

        kept.Should().Equal(
            "2026-10-01 10:00:01.000 +03:00 [INF] Update available",
            "2026-10-01 10:00:03.000 +03:00 [WRN] Something odd");
    }

    [Fact]
    public void FilterDumpLines_KeepsStackTraceOfKeptEntry_DropsTraceOfDebugEntry()
    {
        var log = string.Join("\r\n",
            "2026-10-01 10:00:00.000 +03:00 [ERR] Boom",
            "System.InvalidOperationException: Not authenticated",
            "   at Foo.Bar()",
            "2026-10-01 10:00:01.000 +03:00 [DBG] noisy",
            "   at Hidden.Frame()");

        var kept = LogShippingControlService.FilterDumpLines(log, 100);

        kept.Should().Equal(
            "2026-10-01 10:00:00.000 +03:00 [ERR] Boom",
            "System.InvalidOperationException: Not authenticated",
            "   at Foo.Bar()");
    }

    [Fact]
    public void FilterDumpLines_ReturnsOnlyTheLastLines()
    {
        var log = string.Join("\n", Enumerable.Range(1, 10)
            .Select(i => $"2026-10-01 10:00:{i:00}.000 +03:00 [INF] line {i}"));

        var kept = LogShippingControlService.FilterDumpLines(log, 3);

        kept.Should().HaveCount(3);
        kept[0].Should().EndWith("line 8");
        kept[2].Should().EndWith("line 10");
    }
}
