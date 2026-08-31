package com.navigator.ledger

import java.sql.Timestamp
import java.util.UUID

sealed trait EntryType
case object Debit extends EntryType
case object Credit extends EntryType

case class JournalEntry(
    entryId: String,
    transactionId: String,
    accountId: String,
    entryType: String,
    amount: Double,
    currency: String,
    recordedAt: Timestamp
)

case class AccountReconciliationResult(
    accountId: String,
    calculatedBalance: Double,
    reportedBalance: Double,
    discrepancy: Double,
    isBalanced: Boolean,
    reconciledAt: Timestamp
)
