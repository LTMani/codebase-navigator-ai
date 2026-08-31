namespace Navigator.Enterprise.Gateway.Service15;

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

public class EnterpriseService15Gateway
{
    public record Service15Descriptor(Guid Id, string ServiceKey, string RoutePattern, int LatencyMs, bool IsHealthy);

    private readonly ConcurrentDictionary<Guid, Service15Descriptor> _catalog = new();

    public Task<Service15Descriptor> RegisterRouteAsync(string serviceKey, string routePattern, int latencyMs)
    {
        var descriptor = new Service15Descriptor(Guid.NewGuid(), serviceKey, routePattern, latencyMs, true);
        _catalog[descriptor.Id] = descriptor;
        return Task.FromResult(descriptor);
    }

    public Task<IEnumerable<Service15Descriptor>> GetHealthyRoutesAsync()
    {
        var healthy = _catalog.Values.Where(r => r.IsHealthy);
        return Task.FromResult<IEnumerable<Service{i}Descriptor>>(healthy);
    }
}
