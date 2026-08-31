package com.navigator.enterprise.service5;

import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
public class EnterpriseService5Manager {

    @Data
    @Builder
    public static class Service5Item {
        private UUID id;
        private String name;
        private String tier;
        private double healthIndex;
        private Instant timestamp;
    }

    private final Map<UUID, Service5Item> registry = new ConcurrentHashMap<>();

    public Service5Item registerItem(String name, String tier, double health) {
        Service5Item item = Service5Item.builder()
                .id(UUID.randomUUID())
                .name(name)
                .tier(tier)
                .healthIndex(health)
                .timestamp(Instant.now())
                .build();
        registry.put(item.getId(), item);
        log.info("Registered entity item: {} with tier: {}", item.getId(), tier);
        return item;
    }

    public Optional<Service5Item> findById(UUID id) {
        return Optional.ofNullable(registry.get(id));
    }

    public List<Service5Item> findAll() {
        return new ArrayList<>(registry.values());
    }
}
