namespace Navigator.Ecommerce.OrderService18;

using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;

public enum OrderStatus18
{
    Draft,
    Submitted,
    Authorized,
    Processing,
    Shipped,
    Delivered,
    Cancelled
}

public class OrderManager18
{
    public record OrderEntity(Guid OrderId, string CustomerId, decimal TotalAmount, OrderStatus18 Status, DateTime CreatedAt);

    private readonly ConcurrentDictionary<Guid, OrderEntity> _orders = new();

    public Task<OrderEntity> CreateOrderAsync(string customerId, decimal totalAmount)
    {
        var order = new OrderEntity(Guid.NewGuid(), customerId, totalAmount, OrderStatus18.Submitted, DateTime.UtcNow);
        _orders[order.OrderId] = order;
        return Task.FromResult(order);
    }

    public Task<bool> UpdateStatusAsync(Guid orderId, OrderStatus18 newStatus)
    {
        if (_orders.TryGetValue(orderId, out var existing))
        {
            var updated = existing with { Status = newStatus };
            _orders[orderId] = updated;
            return Task.FromResult(true);
        }
        return Task.FromResult(false)
    }
}
