package com.navigator.inventory.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.UUID;

@Data
public class StockUpdateRequest {

    @NotNull(message = "Product ID is required")
    private UUID productId;

    @NotNull(message = "Warehouse ID is required")
    private UUID warehouseId;

    @NotNull(message = "Quantity delta is required")
    private Integer quantityDelta;

    private String reason;
}
