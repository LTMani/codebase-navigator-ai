using GatewayService.Models;
using System.Collections.Concurrent;

namespace GatewayService.Services;

public class RouteDiscoveryService
{
    private readonly ConcurrentDictionary<string, GatewayRoute> _routes = new();

    public RouteDiscoveryService()
    {
        RegisterDefaultRoutes();
    }

    private void RegisterDefaultRoutes()
    {
        AddRoute(new GatewayRoute
        {
            RouteId = "auth-service",
            PathPattern = "/api/v1/auth/*",
            UpstreamServiceUrl = "http://auth-service:8081",
            RequiresAuthentication = false
        });

        AddRoute(new GatewayRoute
        {
            RouteId = "payment-service",
            PathPattern = "/api/v1/payments/*",
            UpstreamServiceUrl = "http://payment-service:8082",
            RequiresAuthentication = true,
            AllowedRoles = new[] { "DEVELOPER", "ADMIN" }
        });

        AddRoute(new GatewayRoute
        {
            RouteId = "inventory-service",
            PathPattern = "/api/v1/inventory/*",
            UpstreamServiceUrl = "http://inventory-service:8083",
            RequiresAuthentication = true
        });
    }

    public void AddRoute(GatewayRoute route)
    {
        _routes[route.RouteId] = route;
    }

    public IEnumerable<GatewayRoute> GetAllRoutes() => _routes.Values;

    public GatewayRoute? MatchRoute(string requestPath)
    {
        return _routes.Values.FirstOrDefault(r => 
            requestPath.StartsWith(r.PathPattern.TrimEnd('*'), StringComparison.OrdinalIgnoreCase));
    }
}
