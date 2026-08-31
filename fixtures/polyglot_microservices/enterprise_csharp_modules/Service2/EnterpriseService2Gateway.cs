namespace Navigator.Enterprise.Gateway.Service2;

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

public class EnterpriseService2Gateway
{
    public record Service2Descriptor(Guid Id, string ServiceKey, string RoutePattern, int LatencyMs, bool IsHealthy);

    private readonly ConcurrentDictionary<Guid, Service2Descriptor> _catalog = new();

    public Task<Service2Descriptor> RegisterRouteAsync(string serviceKey, string routePattern, int latencyMs)
    {
        var descriptor = new Service2Descriptor(Guid.NewGuid(), serviceKey, routePattern, latencyMs, true);
        _catalog[descriptor.Id] = descriptor;
        return Task.FromResult(descriptor);
    }

    public Task<IEnumerable<Service2Descriptor>> GetHealthyRoutesAsync()
    {
        var healthy = _catalog.Values.Where(r => r.IsHealthy);
        return Task.FromResult<IEnumerable<Service{i}Descriptor>>(healthy);
    }
}
