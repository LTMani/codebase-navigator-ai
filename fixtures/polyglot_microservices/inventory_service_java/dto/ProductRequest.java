package com.navigator.inventory.dto;

import jakarta.validation.constraints.*;
import lombok.Data;

import java.math.BigDecimal;

@Data
public class ProductRequest {

    @NotBlank(message = "SKU is required")
    @Size(min = 3, max = 64, message = "SKU must be between 3 and 64 characters")
    private String sku;

    @NotBlank(message = "Product name is required")
    @Size(min = 2, max = 255, message = "Name must be between 2 and 255 characters")
    private String name;

    private String description;

    @NotBlank(message = "Category is required")
    private String category;

    @NotNull(message = "Unit price is required")
    @DecimalMin(value = "0.01", message = "Unit price must be greater than zero")
    private BigDecimal unitPrice;

    @NotNull(message = "Reorder threshold is required")
    @Min(value = 0, message = "Threshold cannot be negative")
    private Integer reorderThreshold;
}
