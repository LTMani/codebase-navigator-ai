use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use super::currency::Currency;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum TransactionType {
    Debit,
    Credit,
    Hold,
    Release,
    Fee,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LedgerEntry {
    pub id: Uuid,
    pub transaction_id: Uuid,
    pub account_id: Uuid,
    pub entry_type: TransactionType,
    pub amount: f64,
    pub currency: Currency,
    pub balance_after: f64,
    pub timestamp: DateTime<Utc>,
}
