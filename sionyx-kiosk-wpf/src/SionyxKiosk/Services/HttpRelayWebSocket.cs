using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net.WebSockets;
using System.Text.Json;
using System.Threading.Channels;
using Serilog;

namespace SionyxKiosk.Services;

/// <summary>
/// A <see cref="WebSocket"/> that carries the relay protocol over plain HTTPS
/// requests instead of a real WebSocket. Added 2026-09-23 for kiosks behind
/// NetFree: it answers WebSocket upgrades to the relay host with
/// "418 Blocked by NetFree" (or lets them open and swallows the traffic), yet
/// ordinary HTTPS requests to the same host - including 20s long-polls - pass
/// fine (measured round trip ~0.4s).
///
/// It is a WebSocket subclass on purpose: VncRelayService's existing byte
/// pumps and control-channel loop only use State / ReceiveAsync / SendAsync /
/// CloseAsync, so they work unchanged whichever transport was chosen.
///
/// Protocol (see server.js, "HTTP long-poll fallback transport"):
///   POST /rt/&lt;role&gt;/&lt;token&gt;/send[?t=1]    body = one message
///   GET  /rt/&lt;role&gt;/&lt;token&gt;/recv?wait=N    -> { messages:[{data:b64,binary}], closed? }
///   POST /rt/&lt;role&gt;/&lt;token&gt;/close
///
/// Acknowledged delivery (added 2026-09-24) for the VNC byte-stream role
/// ("agent"): behind NetFree a /recv response can be blocked (418), truncated
/// or altered AFTER the relay answered it, which used to lose bytes and shift
/// the whole stream. Now every GET carries &amp;ack=&lt;bytes accepted so far&gt;
/// and the relay answers with the bytes starting exactly there (same ack =
/// same bytes, so a lost response is simply asked for again); every message
/// is accepted only if offset, length and CRC32 match. POSTs carry
/// ?off=&lt;bytes sent so far&gt; so a retried POST is never applied twice.
/// The control channel (JSON) is unchanged.
///
/// Ordering guarantees the VNC byte stream depends on: exactly one recv poll
/// is in flight at a time, and outgoing messages are POSTed strictly one at a
/// time, in order. Consecutive binary messages are merged into one POST (one
/// round trip per burst instead of per 16KB read) - fine for a byte stream;
/// text messages (control-channel JSON) are never merged.
/// </summary>
internal sealed class HttpRelayWebSocket : WebSocket
{
    private static readonly ILogger Logger = Log.ForContext<HttpRelayWebSocket>();

    // Timeout is per request (set via CancelAfter), not on the client, because
    // a recv long-poll legitimately takes ~20s.
    private static readonly HttpClient Http = CreateHttpClient();

    private const int RecvWaitMs = 20000;
    private static readonly TimeSpan RecvRequestTimeout = TimeSpan.FromSeconds(35);
    private static readonly TimeSpan SendRequestTimeout = TimeSpan.FromSeconds(30);
    private const int MaxRecvFailures = 12;
    private const int MaxSendAttempts = 6;
    private const int MaxBatchBytes = 1024 * 1024;
    // 64 x 16KB reads = 1MB of unsent data at most: when the uplink can't
    // keep up, SendAsync blocks and the TCP->relay pump stops reading from
    // TightVNC instead of buffering without limit.
    private const int OutboundCapacity = 64;

    private readonly record struct Message(byte[] Data, bool IsBinary);

    private readonly string _base;
    private readonly string _role;
    // Acknowledged byte-stream mode (see class remarks): only the raw VNC stream.
    private readonly bool _streamMode;
    private long _rxAck;   // bytes of the relay->kiosk stream accepted so far
    private long _txOff;   // bytes of the kiosk->relay stream the relay has confirmed
    private readonly CancellationTokenSource _cts;
    private readonly Channel<Message> _inbound = Channel.CreateUnbounded<Message>(
        new UnboundedChannelOptions { SingleReader = true, SingleWriter = true });
    private readonly Channel<Message> _outbound = Channel.CreateBounded<Message>(
        new BoundedChannelOptions(OutboundCapacity) { SingleReader = true, FullMode = BoundedChannelFullMode.Wait });

    private Task _sendLoop = Task.CompletedTask;
    private Message? _current;
    private int _currentOffset;
    private volatile WebSocketState _state = WebSocketState.Connecting;
    private int _closeNotified;
    private WebSocketCloseStatus? _closeStatus;
    private string? _closeDescription;

    private HttpRelayWebSocket(string httpBaseUrl, string role, string token, CancellationToken ct)
    {
        _base = $"{httpBaseUrl.TrimEnd('/')}/rt/{role}/{Uri.EscapeDataString(token)}";
        _role = role;
        _streamMode = role == "agent";
        _cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
    }

    /// <summary>Relay says the stream position is inconsistent - retrying can't help.</summary>
    private sealed class RelayStreamException : Exception
    {
        public RelayStreamException(string message) : base(message) { }
    }

    // CRC32 (zlib polynomial) - the relay sends one per message.
    private static readonly uint[] CrcTable = BuildCrcTable();
    private static uint[] BuildCrcTable()
    {
        var t = new uint[256];
        for (uint n = 0; n < 256; n++)
        {
            var c = n;
            for (var k = 0; k < 8; k++) c = (c & 1) != 0 ? 0xEDB88320u ^ (c >> 1) : c >> 1;
            t[n] = c;
        }
        return t;
    }
    private static uint Crc32(byte[] data)
    {
        var c = 0xFFFFFFFFu;
        foreach (var b in data) c = CrcTable[(c ^ b) & 0xFF] ^ (c >> 8);
        return c ^ 0xFFFFFFFFu;
    }

    /// <summary>
    /// Verifies the relay is reachable over HTTPS (one quick poll) and starts
    /// the send/receive loops. Throws if the relay can't be reached - so a
    /// caller never gets back a channel that silently does nothing.
    /// </summary>
    public static async Task<HttpRelayWebSocket> ConnectAsync(string httpBaseUrl, string role, string token, CancellationToken ct)
    {
        var ws = new HttpRelayWebSocket(httpBaseUrl, role, token, ct);
        try
        {
            // Reachability check. NetFree can block a single request, so try a
            // few times before giving up on this transport.
            for (var attempt = 1; ; attempt++)
            {
                try
                {
                    using var checkCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
                    checkCts.CancelAfter(RecvRequestTimeout);
                    using var resp = await Http.GetAsync($"{ws._base}/recv?wait=0{ws.AckQuery()}", checkCts.Token);
                    resp.EnsureSuccessStatusCode();
                    var json = await resp.Content.ReadAsStringAsync(checkCts.Token);
                    // In acknowledged mode nothing is consumed here: the ack is still 0,
                    // so the receive loop asks for the same bytes again.
                    if (!ws._streamMode) ws.HandleRecvPayload(json);
                    break;
                }
                catch (Exception) when (attempt < 3 && !ct.IsCancellationRequested)
                {
                    await Task.Delay(300 * attempt, ct);
                }
            }
        }
        catch
        {
            ws.Dispose();
            throw;
        }

        ws._state = WebSocketState.Open;
        _ = Task.Run(ws.RecvLoopAsync);
        ws._sendLoop = Task.Run(ws.SendLoopAsync);
        Logger.Information("HTTP relay transport ready for {Role} ({Base})", role, ws._base);
        return ws;
    }

    private static HttpClient CreateHttpClient()
    {
        var client = new HttpClient { Timeout = Timeout.InfiniteTimeSpan };
        client.DefaultRequestHeaders.UserAgent.ParseAdd("SionyxKiosk-VncRelay/1.0");
        client.DefaultRequestHeaders.CacheControl = new CacheControlHeaderValue { NoCache = true };
        return client;
    }

    // ---- WebSocket surface -------------------------------------------------

    public override WebSocketState State => _state;
    public override WebSocketCloseStatus? CloseStatus => _closeStatus;
    public override string? CloseStatusDescription => _closeDescription;
    public override string? SubProtocol => null;

    public override async Task<WebSocketReceiveResult> ReceiveAsync(ArraySegment<byte> buffer, CancellationToken cancellationToken)
    {
        while (_current is null)
        {
            if (_inbound.Reader.TryRead(out var next))
            {
                if (next.Data.Length == 0) continue;
                _current = next;
                _currentOffset = 0;
                break;
            }
            // Throws the failure exception if the transport died (Fail), which
            // surfaces through the caller's normal "session failed" handling.
            if (!await _inbound.Reader.WaitToReadAsync(cancellationToken))
            {
                if (_state == WebSocketState.Open) _state = WebSocketState.CloseReceived;
                _closeStatus = WebSocketCloseStatus.NormalClosure;
                _closeDescription = "relay peer closed";
                return new WebSocketReceiveResult(0, WebSocketMessageType.Close, true,
                    WebSocketCloseStatus.NormalClosure, _closeDescription);
            }
        }

        var msg = _current.Value;
        var remaining = msg.Data.Length - _currentOffset;
        var count = Math.Min(buffer.Count, remaining);
        Buffer.BlockCopy(msg.Data, _currentOffset, buffer.Array!, buffer.Offset, count);
        _currentOffset += count;
        var endOfMessage = _currentOffset >= msg.Data.Length;
        if (endOfMessage) _current = null;
        return new WebSocketReceiveResult(count, msg.IsBinary ? WebSocketMessageType.Binary : WebSocketMessageType.Text, endOfMessage);
    }

    public override async Task SendAsync(ArraySegment<byte> buffer, WebSocketMessageType messageType, bool endOfMessage, CancellationToken cancellationToken)
    {
        if (_state != WebSocketState.Open)
            throw new WebSocketException(WebSocketError.InvalidState, $"HTTP relay transport is {_state}");
        if (messageType == WebSocketMessageType.Close) return;
        // Copy: callers reuse their buffer as soon as this returns.
        await _outbound.Writer.WriteAsync(new Message(buffer.ToArray(), messageType == WebSocketMessageType.Binary), cancellationToken);
    }

    public override async Task CloseAsync(WebSocketCloseStatus closeStatus, string? statusDescription, CancellationToken cancellationToken)
    {
        await CloseCoreAsync(closeStatus, statusDescription);
    }

    public override async Task CloseOutputAsync(WebSocketCloseStatus closeStatus, string? statusDescription, CancellationToken cancellationToken)
    {
        await CloseCoreAsync(closeStatus, statusDescription);
    }

    public override void Abort()
    {
        _state = WebSocketState.Aborted;
        _cts.Cancel();
        _inbound.Writer.TryComplete();
        NotifyClosedBestEffort();
    }

    public override void Dispose()
    {
        if (_state != WebSocketState.Closed && _state != WebSocketState.Aborted)
        {
            _state = WebSocketState.Closed;
        }
        NotifyClosedBestEffort();
        try { _cts.Cancel(); } catch (ObjectDisposedException) { }
        _inbound.Writer.TryComplete();
        _cts.Dispose();
    }

    private async Task CloseCoreAsync(WebSocketCloseStatus status, string? description)
    {
        if (_state is WebSocketState.Closed or WebSocketState.Aborted) return;
        _state = WebSocketState.CloseSent;
        _closeStatus = status;
        _closeDescription = description;

        // Let already-queued data go out first (bounded), then tell the relay.
        _outbound.Writer.TryComplete();
        try { await _sendLoop.WaitAsync(TimeSpan.FromSeconds(3)); } catch { /* best effort */ }

        NotifyClosedBestEffort();
        _state = WebSocketState.Closed;
        try { _cts.Cancel(); } catch (ObjectDisposedException) { }
        _inbound.Writer.TryComplete();
    }

    // ---- Loops -----------------------------------------------------------

    private async Task SendLoopAsync()
    {
        var ct = _cts.Token;
        var reader = _outbound.Reader;
        try
        {
            while (await reader.WaitToReadAsync(ct))
            {
                if (!reader.TryRead(out var first)) continue;

                byte[] body;
                var isText = !first.IsBinary;
                if (isText)
                {
                    body = first.Data;
                }
                else
                {
                    using var ms = new MemoryStream();
                    ms.Write(first.Data, 0, first.Data.Length);
                    while (ms.Length < MaxBatchBytes && reader.TryPeek(out var peek) && peek.IsBinary && reader.TryRead(out var more))
                    {
                        ms.Write(more.Data, 0, more.Data.Length);
                    }
                    body = ms.ToArray();
                }

                // ?off= makes a retry after a lost/blocked response idempotent.
                long? off = _streamMode && !isText ? _txOff : null;
                await PostWithRetryAsync(isText ? "send?t=1" : (off is null ? "send" : $"send?off={off}"), body, isText, ct);
                if (off is not null) _txOff += body.Length;
            }
        }
        catch (OperationCanceledException) { /* closed/disposed */ }
        catch (Exception ex) { Fail(ex); }
    }

    private async Task PostWithRetryAsync(string relativeUrl, byte[] body, bool isText, CancellationToken ct)
    {
        for (var attempt = 1; ; attempt++)
        {
            try
            {
                using var reqCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
                reqCts.CancelAfter(SendRequestTimeout);
                using var content = new ByteArrayContent(body);
                content.Headers.ContentType = new MediaTypeHeaderValue(isText ? "text/plain" : "application/octet-stream");
                using var resp = await Http.PostAsync($"{_base}/{relativeUrl}", content, reqCts.Token);
                if (resp.StatusCode == HttpStatusCode.Conflict)
                    throw new RelayStreamException("relay reports a gap in the kiosk->relay stream (409)");
                resp.EnsureSuccessStatusCode();
                return;
            }
            catch (OperationCanceledException) when (ct.IsCancellationRequested)
            {
                throw;
            }
            catch (Exception ex) when (attempt < MaxSendAttempts && ex is not RelayStreamException)
            {
                // Never skip a chunk: dropping bytes would corrupt the VNC stream.
                await Task.Delay(300 * attempt, ct);
            }
        }
    }

    private async Task RecvLoopAsync()
    {
        var ct = _cts.Token;
        var failures = 0;
        while (!ct.IsCancellationRequested)
        {
            try
            {
                using var reqCts = CancellationTokenSource.CreateLinkedTokenSource(ct);
                reqCts.CancelAfter(RecvRequestTimeout);
                using var resp = await Http.GetAsync($"{_base}/recv?wait={RecvWaitMs}{AckQuery()}", reqCts.Token);
                if (resp.StatusCode == HttpStatusCode.Conflict)
                    throw new RelayStreamException("relay lost track of the stream (bad ack, 409) - a new session is needed");
                resp.EnsureSuccessStatusCode();
                var json = await resp.Content.ReadAsStringAsync(reqCts.Token);
                // A blocked (418), truncated or altered response throws here or
                // in HandleRecvPayload; the SAME ack is then requested again.
                var peerClosed = HandleRecvPayload(json);
                failures = 0;
                if (peerClosed)
                {
                    // Peer said it's gone: end of stream (normal close).
                    _inbound.Writer.TryComplete();
                    return;
                }
            }
            catch (OperationCanceledException) when (ct.IsCancellationRequested)
            {
                return;
            }
            catch (RelayStreamException ex)
            {
                Fail(ex);
                return;
            }
            catch (Exception ex)
            {
                Logger.Debug(ex, "HTTP relay recv ({Role}) failed, asking again from offset {Ack}", _role, _rxAck);
                if (++failures >= MaxRecvFailures)
                {
                    Fail(ex);
                    return;
                }
                try { await Task.Delay(Math.Min(2000, 300 * failures), ct); }
                catch (OperationCanceledException) { return; }
            }
        }
    }

    /// <returns>true if the server reported the peer has closed.</returns>
    private bool HandleRecvPayload(string json)
    {
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;
        if (root.TryGetProperty("messages", out var messages))
        {
            foreach (var m in messages.EnumerateArray())
            {
                var data = Convert.FromBase64String(m.GetProperty("data").GetString() ?? "");
                var binary = m.TryGetProperty("binary", out var b) && b.GetBoolean();
                if (_streamMode && binary)
                {
                    // Accept ONLY exactly the next bytes, intact. Anything else is
                    // discarded (never reaches TightVNC) and requested again.
                    if (!m.TryGetProperty("off", out var offEl) || !offEl.TryGetInt64(out var off) || off != _rxAck)
                        throw new InvalidDataException($"unexpected offset in /recv (want {_rxAck})");
                    if (!m.TryGetProperty("len", out var lenEl) || !lenEl.TryGetInt32(out var len) || len != data.Length)
                        throw new InvalidDataException($"length mismatch in /recv at {off}");
                    if (m.TryGetProperty("crc", out var crcEl) && crcEl.TryGetUInt32(out var crc) && Crc32(data) != crc)
                        throw new InvalidDataException($"crc mismatch in /recv at {off}");
                    _rxAck += data.Length;
                }
                _inbound.Writer.TryWrite(new Message(data, binary));
            }
        }
        return root.TryGetProperty("closed", out var closed) && closed.ValueKind == JsonValueKind.True;
    }

    private void Fail(Exception ex)
    {
        if (_state is WebSocketState.Closed or WebSocketState.Aborted) return;
        Logger.Warning(ex, "HTTP relay transport ({Role}) failed - giving up on this session", _role);
        _state = WebSocketState.Aborted;
        _cts.Cancel();
        _inbound.Writer.TryComplete(new WebSocketException(WebSocketError.ConnectionClosedPrematurely,
            "HTTP relay transport failed: " + ex.Message, ex));
    }

    private string AckQuery() => _streamMode ? $"&ack={_rxAck}" : "";

    private void NotifyClosedBestEffort()
    {
        if (Interlocked.Exchange(ref _closeNotified, 1) == 1) return;
        var url = $"{_base}/close";
        _ = Task.Run(async () =>
        {
            try
            {
                using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
                using var resp = await Http.PostAsync(url, new ByteArrayContent(Array.Empty<byte>()), cts.Token);
            }
            catch { /* best effort - the relay also expires idle HTTP roles on its own */ }
        });
    }
}
