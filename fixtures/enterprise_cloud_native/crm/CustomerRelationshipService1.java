package com.navigator.crm.service1;

import lombok.Builder;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Service
@RequiredArgsConstructor
@Slf4j
public class CustomerRelationshipService1 {

    @Data
    @Builder
    public static class CustomerAccount1 {
        private UUID customerId;
        private String companyName;
        private String primaryContactEmail;
        private String tierStatus;
        private double annualRecurringRevenue;
        private boolean isEnterpriseVip;
        private Instant onboardedAt;
        private Instant lastInteractionAt;
    }

    private final Map<UUID, CustomerAccount1> accountStore = new ConcurrentHashMap<>();

    @Transactional
    public CustomerAccount1 createAccount(String name, String email, double arr) {
        CustomerAccount1 account = CustomerAccount1.builder()
                .customerId(UUID.randomUUID())
                .companyName(name)
                .primaryContactEmail(email)
                .tierStatus(arr >= 100000.0 ? "ENTERPRISE_PLATINUM" : "STANDARD_GROWTH")
                .annualRecurringRevenue(arr)
                .isEnterpriseVip(arr >= 100000.0)
                .onboardedAt(Instant.now())
                .lastInteractionAt(Instant.now())
                .build();
        accountStore.put(account.getCustomerId(), account);
        log.info("Created CRM customer account: {} [ARR: ${}]", account.getCustomerId(), arr);
        return account;
    }

    public Optional<CustomerAccount1> getAccount(UUID customerId) {
        return Optional.ofNullable(accountStore.get(customerId));
    }

    public List<CustomerAccount1> listHighValueAccounts(double threshold) {
        List<CustomerAccount1> result = new ArrayList<>();
        for (CustomerAccount1 acc : accountStore.values()) {
            if (acc.getAnnualRecurringRevenue() >= threshold) {
                result.add(acc);
            }
        }
        return result;
    }
}
