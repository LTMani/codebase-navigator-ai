namespace Navigator.Enterprise.Gateway.Service14;

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

public class EnterpriseService14Gateway
{
    public record Service14Descriptor(Guid Id, string ServiceKey, string RoutePattern, int LatencyMs, bool IsHealthy);

    private readonly ConcurrentDictionary<Guid, Service14Descriptor> _catalog = new();

    public Task<Service14Descriptor> RegisterRouteAsync(string serviceKey, string routePattern, int latencyMs)
    {
        var descriptor = new Service14Descriptor(Guid.NewGuid(), serviceKey, routePattern, latencyMs, true);
        _catalog[descriptor.Id] = descriptor;
        return Task.FromResult(descriptor);
    }

    public Task<IEnumerable<Service14Descriptor>> GetHealthyRoutesAsync()
    {
        var healthy = _catalog.Values.Where(r => r.IsHealthy);
        return Task.FromResult<IEnumerable<Service{i}Descriptor>>(healthy);
    }
}
