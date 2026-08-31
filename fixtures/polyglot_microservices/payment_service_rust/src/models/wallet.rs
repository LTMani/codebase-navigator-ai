use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use super::currency::Currency;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Wallet {
    pub id: Uuid,
    pub owner_id: Uuid,
    pub currency: Currency,
    pub available_balance: f64,
    pub held_balance: f64,
    pub is_frozen: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

impl Wallet {
    pub fn new(owner_id: Uuid, currency: Currency) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            owner_id,
            currency,
            available_balance: 0.0,
            held_balance: 0.0,
            is_frozen: false,
            created_at: now,
            updated_at: now,
        }
    }

    pub fn total_balance(&self) -> f64 {
        self.available_balance + self.held_balance
    }

    pub fn can_debit(&self, amount: f64) -> bool {
        !self.is_frozen && self.available_balance >= amount && amount > 0.0
    }
}
