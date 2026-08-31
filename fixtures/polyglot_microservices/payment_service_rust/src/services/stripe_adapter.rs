use crate::errors::PaymentError;
use reqwest::Client;
use serde_json::json;

pub struct StripeAdapter {
    client: Client,
    secret_key: String,
}

impl StripeAdapter {
    pub fn new(secret_key: String) -> Self {
        Self {
            client: Client::new(),
            secret_key,
        }
    }

    pub async fn create_charge(&self, amount_cents: i64, currency: &str, source_token: &str) -> Result<String, PaymentError> {
        let payload = json!({
            "amount": amount_cents,
            "currency": currency,
            "source": source_token,
            "capture": true
        });

        // Simulate gateway network call
        if source_token.starts_with("tok_err") {
            return Err(PaymentError::GatewayError("Card declined: insufficient balance or invalid card number".into()));
        }

        let mock_ch_id = format!("ch_mock_{}", uuid::Uuid::new_v4().simple());
        Ok(mock_ch_id)
    }

    pub async fn refund_charge(&self, charge_id: &str, amount_cents: i64) -> Result<String, PaymentError> {
        if charge_id.is_empty() {
            return Err(PaymentError::GatewayError("Invalid charge ID for refund".into()));
        }
        let mock_re_id = format!("re_mock_{}", uuid::Uuid::new_v4().simple());
        Ok(mock_re_id)
    }
}
