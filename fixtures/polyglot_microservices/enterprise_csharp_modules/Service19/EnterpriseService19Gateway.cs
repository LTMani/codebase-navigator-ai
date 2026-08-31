namespace Navigator.Enterprise.Gateway.Service19;

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

public class EnterpriseService19Gateway
{
    public record Service19Descriptor(Guid Id, string ServiceKey, string RoutePattern, int LatencyMs, bool IsHealthy);

    private readonly ConcurrentDictionary<Guid, Service19Descriptor> _catalog = new();

    public Task<Service19Descriptor> RegisterRouteAsync(string serviceKey, string routePattern, int latencyMs)
    {
        var descriptor = new Service19Descriptor(Guid.NewGuid(), serviceKey, routePattern, latencyMs, true);
        _catalog[descriptor.Id] = descriptor;
        return Task.FromResult(descriptor);
    }

    public Task<IEnumerable<Service19Descriptor>> GetHealthyRoutesAsync()
    {
        var healthy = _catalog.Values.Where(r => r.IsHealthy);
        return Task.FromResult<IEnumerable<Service{i}Descriptor>>(healthy);
    }
}
