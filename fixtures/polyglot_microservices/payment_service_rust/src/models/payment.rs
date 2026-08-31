use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
use super::currency::Currency;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum PaymentStatus {
    Pending,
    Authorized,
    Captured,
    Failed,
    Refunded,
    PartiallyRefunded,
    Cancelled,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PaymentIntent {
    pub id: Uuid,
    pub customer_id: Uuid,
    pub amount: f64,
    pub currency: Currency,
    pub status: PaymentStatus,
    pub provider_payment_id: Option<String>,
    pub client_secret: String,
    pub description: Option<String>,
    pub metadata: serde_json::Value,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct CreatePaymentRequest {
    pub customer_id: Uuid,
    pub amount: f64,
    pub currency: String,
    pub description: Option<String>,
    pub payment_method_id: String,
    pub metadata: Option<serde_json::Value>,
}

#[derive(Debug, Clone, Serialize)]
pub struct PaymentResponse {
    pub payment_id: Uuid,
    pub amount: f64,
    pub currency: Currency,
    pub status: PaymentStatus,
    pub client_secret: String,
    pub created_at: DateTime<Utc>,
}
