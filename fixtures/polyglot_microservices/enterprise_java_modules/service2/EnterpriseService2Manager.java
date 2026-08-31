package com.navigator.enterprise.service2;

import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
public class EnterpriseService2Manager {

    @Data
    @Builder
    public static class Service2Item {
        private UUID id;
        private String name;
        private String tier;
        private double healthIndex;
        private Instant timestamp;
    }

    private final Map<UUID, Service2Item> registry = new ConcurrentHashMap<>();

    public Service2Item registerItem(String name, String tier, double health) {
        Service2Item item = Service2Item.builder()
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

    public Optional<Service2Item> findById(UUID id) {
        return Optional.ofNullable(registry.get(id));
    }

    public List<Service2Item> findAll() {
        return new ArrayList<>(registry.values());
    }
}
