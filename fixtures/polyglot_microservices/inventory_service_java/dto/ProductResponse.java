package com.navigator.inventory.dto;

import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
public class ProductResponse {
    private UUID id;
    private String sku;
    private String name;
    private String description;
    private String category;
    private BigDecimal unitPrice;
    private Integer reorderThreshold;
    private Boolean active;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
