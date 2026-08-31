package com.navigator.enterprise.service16;

import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
public class EnterpriseService16Manager {

    @Data
    @Builder
    public static class Service16Item {
        private UUID id;
        private String name;
        private String tier;
        private double healthIndex;
        private Instant timestamp;
    }

    private final Map<UUID, Service16Item> registry = new ConcurrentHashMap<>();

    public Service16Item registerItem(String name, String tier, double health) {
        Service16Item item = Service16Item.builder()
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

    public Optional<Service16Item> findById(UUID id) {
        return Optional.ofNullable(registry.get(id));
    }

    public List<Service16Item> findAll() {
        return new ArrayList<>(registry.values());
    }
}
