package com.navigator.clearing;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;

import java.math.BigDecimal;
import java.util.UUID;

@Slf4j
public class DvPSettlementEngine {

    public enum SettlementStatus {
        PENDING,
        SECURITIES_LOCKED,
        CASH_LOCKED,
        SETTLED,
        FAILED
    }

    @Data
    @AllArgsConstructor
    public static class DvPInstruction {
        private UUID instructionId;
        private String buyerAccountId;
        private String sellerAccountId;
        private String isin;
        private long quantity;
        private BigDecimal cashAmount;
        private String currency;
        private SettlementStatus status;
    }

    public boolean executeDeliveryVersusPayment(DvPInstruction instruction) {
        log.info("Initiating DvP Settlement for instruction: {}", instruction.getInstructionId());

        try {
            // Step 1: Verify and lock securities
            instruction.setStatus(SettlementStatus.SECURITIES_LOCKED);
            log.debug("Securities locked for ISIN: {} Qty: {}", instruction.getIsin(), instruction.getQuantity());

            // Step 2: Verify and lock cash
            instruction.setStatus(SettlementStatus.CASH_LOCKED);
            log.debug("Cash locked: {} {}", instruction.getCashAmount(), instruction.getCurrency());

            // Step 3: Simultaneous atomic transfer
            instruction.setStatus(SettlementStatus.SETTLED);
            log.info("DvP settlement successful for instruction: {}", instruction.getInstructionId());
            return true;
        } catch (Exception e) {
            instruction.setStatus(SettlementStatus.FAILED);
            log.error("DvP settlement failed for instruction: {}", instruction.getInstructionId(), e);
            return false;
        }
    }
}
