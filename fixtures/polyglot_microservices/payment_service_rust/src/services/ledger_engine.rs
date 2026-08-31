use crate::models::currency::Currency;
use crate::models::transaction::{LedgerEntry, TransactionType};
use chrono::Utc;
use std::sync::Arc;
use tokio::sync::Mutex;
use uuid::Uuid;

pub struct LedgerEngine {
    entries: Arc<Mutex<Vec<LedgerEntry>>>,
}

impl LedgerEngine {
    pub fn new() -> Self {
        Self {
            entries: Arc::new(Mutex::new(Vec::new())),
        }
    }

    pub async fn record_entry(
        &self,
        transaction_id: Uuid,
        account_id: Uuid,
        entry_type: TransactionType,
        amount: f64,
        currency: Currency,
        balance_after: f64,
    ) -> LedgerEntry {
        let entry = LedgerEntry {
            id: Uuid::new_v4(),
            transaction_id,
            account_id,
            entry_type,
            amount,
            currency,
            balance_after,
            timestamp: Utc::now(),
        };

        let mut lock = self.entries.lock().await;
        lock.push(entry.clone());
        entry
    }

    pub async fn get_account_entries(&self, account_id: Uuid) -> Vec<LedgerEntry> {
        let lock = self.entries.lock().await;
        lock.iter()
            .filter(|e| e.account_id == account_id)
            .cloned()
            .collect()
    }
}
