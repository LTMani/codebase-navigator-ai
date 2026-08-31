using GatewayService.Models;
using GatewayService.Services;
using Microsoft.AspNetCore.Mvc;

namespace GatewayService.Controllers;

[ApiController]
[Route("api/v1/gateway")]
public class GatewayController : ControllerBase
{
    private readonly RouteDiscoveryService _routeDiscovery;
    private readonly MetricsCollectorService _metrics;

    public GatewayController(RouteDiscoveryService routeDiscovery, MetricsCollectorService metrics)
    {
        _routeDiscovery = routeDiscovery;
        _metrics = metrics;
    }

    [HttpGet("routes")]
    public ActionResult<IEnumerable<GatewayRoute>> GetRoutes()
    {
        return Ok(_routeDiscovery.GetAllRoutes());
    }

    [HttpGet("metrics")]
    public ActionResult GetMetrics()
    {
        return Ok(new
        {
            Requests = _metrics.GetRequestStats(),
            Errors = _metrics.GetErrorStats()
        });
    }
}
