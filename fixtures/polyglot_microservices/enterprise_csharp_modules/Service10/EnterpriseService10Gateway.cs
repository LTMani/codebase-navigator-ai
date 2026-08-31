namespace Navigator.Enterprise.Gateway.Service10;

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

public class EnterpriseService10Gateway
{
    public record Service10Descriptor(Guid Id, string ServiceKey, string RoutePattern, int LatencyMs, bool IsHealthy);

    private readonly ConcurrentDictionary<Guid, Service10Descriptor> _catalog = new();

    public Task<Service10Descriptor> RegisterRouteAsync(string serviceKey, string routePattern, int latencyMs)
    {
        var descriptor = new Service10Descriptor(Guid.NewGuid(), serviceKey, routePattern, latencyMs, true);
        _catalog[descriptor.Id] = descriptor;
        return Task.FromResult(descriptor);
    }

    public Task<IEnumerable<Service10Descriptor>> GetHealthyRoutesAsync()
    {
        var healthy = _catalog.Values.Where(r => r.IsHealthy);
        return Task.FromResult<IEnumerable<Service{i}Descriptor>>(healthy);
    }
}
