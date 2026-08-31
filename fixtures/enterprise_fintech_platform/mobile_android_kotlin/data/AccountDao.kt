package com.navigator.fintech.mobile.data

import androidx.room.*
import com.navigator.fintech.mobile.models.BankAccount
import kotlinx.coroutines.flow.Flow

@Dao
interface AccountDao {
    @Query("SELECT * FROM bank_accounts ORDER BY createdAtEpochMs DESC")
    fun getAllAccounts(): Flow<List<BankAccount>>

    @Query("SELECT * FROM bank_accounts WHERE id = :accountId LIMIT 1")
    suspend fun getAccountById(accountId: String): BankAccount?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAccount(account: BankAccount)

    @Update
    suspend fun updateAccount(account: BankAccount)

    @Query("DELETE FROM bank_accounts WHERE id = :accountId")
    suspend fun deleteAccount(accountId: String)
}
