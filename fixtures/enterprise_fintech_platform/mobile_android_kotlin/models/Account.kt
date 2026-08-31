package com.navigator.fintech.mobile.models

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.math.BigDecimal
import java.util.UUID

enum class AccountType {
    CHECKING,
    SAVINGS,
    INVESTMENT,
    CREDIT
}

@Entity(tableName = "bank_accounts")
data class BankAccount(
    @PrimaryKey val id: String = UUID.randomUUID().toString(),
    val accountNumber: String,
    val accountHolderName: String,
    val accountType: AccountType,
    val balance: BigDecimal,
    val currency: String = "USD",
    val isFrozen: Boolean = false,
    val createdAtEpochMs: Long = System.currentTimeMillis()
)
