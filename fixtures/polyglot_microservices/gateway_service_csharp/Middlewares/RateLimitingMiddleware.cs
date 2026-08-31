using System.Collections.Concurrent;

namespace GatewayService.Middlewares;

public class RateLimitingMiddleware
{
    private readonly RequestDelegate _next;
    private static readonly ConcurrentDictionary<string, (int Count, DateTime WindowStart)> ClientRequests = new();
    private const int MaxRequestsPerMinute = 120;

    public RateLimitingMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var clientIp = context.Connection.RemoteIpAddress?.ToString() ?? "unknown";
        var now = DateTime.UtcNow;

        var requestInfo = ClientRequests.AddOrUpdate(
            clientIp,
            _ => (1, now),
            (_, current) =>
            {
                if (now - current.WindowStart > TimeSpan.FromMinutes(1))
                {
                    return (1, now);
                }
                return (current.Count + 1, current.WindowStart);
            });

        if (requestInfo.Count > MaxRequestsPerMinute)
        {
            context.Response.StatusCode = StatusCodes.Status429TooManyRequests;
            context.Response.ContentType = "application/json";
            await context.Response.WriteAsync("{\"error\": \"Rate limit exceeded. Please retry in 1 minute.\"}");
            return;
        }

        await _next(context);
    }
}
