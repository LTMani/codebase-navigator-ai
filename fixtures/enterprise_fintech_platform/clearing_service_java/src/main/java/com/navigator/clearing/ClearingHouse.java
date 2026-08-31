package com.navigator.clearing;

import lombok.Builder;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
public class ClearingHouse {

    @Data
    @Builder
    public static class NetObligation {
        private String participantId;
        private String currency;
        private BigDecimal netAmount; // Positive = Receivable, Negative = Payable
        private int grossTransactionCount;
        private Instant calculatedAt;
    }

    private final Map<String, Map<String, BigDecimal>> participantBalances = new ConcurrentHashMap<>();

    public void processGrossTrade(String buyerId, String sellerId, String currency, BigDecimal amount) {
        participantBalances.putIfAbsent(buyerId, new ConcurrentHashMap<>());
        participantBalances.putIfAbsent(sellerId, new ConcurrentHashMap<>());

        // Buyer owes money (payable)
        participantBalances.get(buyerId).merge(currency, amount.negate(), BigDecimal::add);
        // Seller receives money (receivable)
        participantBalances.get(sellerId).merge(currency, amount, BigDecimal::add);

        log.debug("Cleared gross trade between {} and {} for {} {}", buyerId, sellerId, amount, currency);
    }

    public List<NetObligation> calculateMultilateralNetting() {
        List<NetObligation> obligations = new ArrayList<>();
        Instant now = Instant.now();

        for (Map.Entry<String, Map<String, BigDecimal>> participantEntry : participantBalances.entrySet()) {
            String participantId = participantEntry.getKey();
            for (Map.Entry<String, BigDecimal> currencyEntry : participantEntry.getValue().entrySet()) {
                obligations.add(NetObligation.builder()
                        .participantId(participantId)
                        .currency(currencyEntry.getKey())
                        .netAmount(currencyEntry.getValue())
                        .grossTransactionCount(1)
                        .calculatedAt(now)
                        .build());
            }
        }

        log.info("Calculated multilateral netting across {} participants", participantBalances.size());
        return obligations;
    }
}
