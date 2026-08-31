package com.navigator.fintech.mobile.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.navigator.fintech.mobile.data.AccountDao
import com.navigator.fintech.mobile.models.BankAccount
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

sealed class AccountUiState {
    object Loading : AccountUiState()
    data class Success(val accounts: List<BankAccount>) : AccountUiState()
    data class Error(val message: String) : AccountUiState()
}

class AccountViewModel(private val accountDao: AccountDao) : ViewModel() {
    private val _uiState = MutableStateFlow<AccountUiState>(AccountUiState.Loading)
    val uiState: StateFlow<AccountUiState> = _uiState.asStateFlow()

    init {
        loadAccounts()
    }

    fun loadAccounts() {
        viewModelScope.launch {
            try {
                accountDao.getAllAccounts().collect { accounts ->
                    _uiState.value = AccountUiState.Success(accounts)
                }
            } catch (e: Exception) {
                _uiState.value = AccountUiState.Error(e.localizedMessage ?: "Unknown error loading accounts")
            }
        }
    }
}
