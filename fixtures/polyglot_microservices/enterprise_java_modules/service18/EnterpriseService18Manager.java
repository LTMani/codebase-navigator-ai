package com.navigator.enterprise.service18;

import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
public class EnterpriseService18Manager {

    @Data
    @Builder
    public static class Service18Item {
        private UUID id;
        private String name;
        private String tier;
        private double healthIndex;
        private Instant timestamp;
    }

    private final Map<UUID, Service18Item> registry = new ConcurrentHashMap<>();

    public Service18Item registerItem(String name, String tier, double health) {
        Service18Item item = Service18Item.builder()
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

    public Optional<Service18Item> findById(UUID id) {
        return Optional.ofNullable(registry.get(id));
    }

    public List<Service18Item> findAll() {
        return new ArrayList<>(registry.values());
    }
}
