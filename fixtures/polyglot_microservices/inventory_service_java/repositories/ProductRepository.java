package com.navigator.inventory.repositories;

import com.navigator.inventory.models.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface ProductRepository extends JpaRepository<Product, UUID> {

    Optional<Product> findBySku(String sku);

    boolean existsBySku(String sku);

    Page<Product> findByCategoryIgnoreCase(String category, Pageable pageable);

    @Query("SELECT p FROM Product p WHERE p.active = true")
    Page<Product> findAllActive(Pageable pageable);
}
