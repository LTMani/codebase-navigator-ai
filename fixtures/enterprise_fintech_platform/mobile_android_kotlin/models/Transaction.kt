package com.navigator.fintech.mobile.models

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.math.BigDecimal
import java.util.UUID

enum class TransactionStatus {
    PENDING,
    COMPLETED,
    DECLINED,
    REVERSED
}

@Entity(tableName = "account_transactions")
data class AccountTransaction(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val accountId: String,
    val counterpartyName: String,
    val amount: BigDecimal,
    val currency: String,
    val status: TransactionStatus,
    val referenceNote: String?,
    val timestampMs: Long = System.currentTimeMillis()
)
