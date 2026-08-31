namespace GatewayService.Models;

public class GatewayRoute
{
    public string RouteId { get; set; } = string.Empty;
    public string PathPattern { get; set; } = string.Empty;
    public string UpstreamServiceUrl { get; set; } = string.Empty;
    public bool RequiresAuthentication { get; set; } = true;
    public int TimeoutSeconds { get; set; } = 30;
    public string[] AllowedRoles { get; set; } = Array.Empty<string>();
}
