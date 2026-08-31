package com.navigator.enterprise.service17;

import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
public class EnterpriseService17Manager {

    @Data
    @Builder
    public static class Service17Item {
        private UUID id;
        private String name;
        private String tier;
        private double healthIndex;
        private Instant timestamp;
    }

    private final Map<UUID, Service17Item> registry = new ConcurrentHashMap<>();

    public Service17Item registerItem(String name, String tier, double health) {
        Service17Item item = Service17Item.builder()
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

    public Optional<Service17Item> findById(UUID id) {
        return Optional.ofNullable(registry.get(id));
    }

    public List<Service17Item> findAll() {
        return new ArrayList<>(registry.values());
    }
}
