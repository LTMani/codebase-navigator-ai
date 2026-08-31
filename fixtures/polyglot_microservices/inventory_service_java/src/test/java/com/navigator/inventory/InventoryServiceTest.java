package com.navigator.inventory;

import com.navigator.inventory.dto.ProductRequest;
import com.navigator.inventory.dto.ProductResponse;
import com.navigator.inventory.models.Product;
import com.navigator.inventory.repositories.ProductRepository;
import com.navigator.inventory.services.ProductService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class InventoryServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductService productService;

    private ProductRequest sampleRequest;
    private Product sampleProduct;

    @BeforeEach
    void setUp() {
        sampleRequest = new ProductRequest();
        sampleRequest.setSku("PROD-1001");
        sampleRequest.setName("Enterprise Wireless Router");
        sampleRequest.setCategory("Networking");
        sampleRequest.setUnitPrice(new BigDecimal("199.99"));
        sampleRequest.setReorderThreshold(10);

        sampleProduct = Product.builder()
                .id(UUID.randomUUID())
                .sku(sampleRequest.getSku())
                .name(sampleRequest.getName())
                .category(sampleRequest.getCategory())
                .unitPrice(sampleRequest.getUnitPrice())
                .reorderThreshold(sampleRequest.getReorderThreshold())
                .active(true)
                .build();
    }

    @Test
    void testCreateProductSuccess() {
        when(productRepository.existsBySku(sampleRequest.getSku())).thenReturn(false);
        when(productRepository.save(any(Product.class))).thenReturn(sampleProduct);

        ProductResponse response = productService.createProduct(sampleRequest);

        assertNotNull(response);
        assertEquals(sampleRequest.getSku(), response.getSku());
        verify(productRepository, times(1)).save(any(Product.class));
    }
}
