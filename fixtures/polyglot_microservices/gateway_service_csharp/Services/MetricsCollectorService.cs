using System.Collections.Concurrent;

namespace GatewayService.Services;

public class MetricsCollectorService
{
    private readonly ConcurrentDictionary<string, long> _requestCounts = new();
    private readonly ConcurrentDictionary<string, long> _errorCounts = new();

    public void RecordRequest(string serviceId)
    {
        _requestCounts.AddOrUpdate(serviceId, 1, (_, count) => count + 1);
    }

    public void RecordError(string serviceId)
    {
        _errorCounts.AddOrUpdate(serviceId, 1, (_, count) => count + 1);
    }

    public IDictionary<string, long> GetRequestStats() => _requestCounts;
    public IDictionary<string, long> GetErrorStats() => _errorCounts;
}
