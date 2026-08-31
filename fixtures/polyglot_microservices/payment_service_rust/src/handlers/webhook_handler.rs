use axum::{
    extract::State,
    http::{HeaderMap, StatusCode},
    Json,
};
use serde_json::Value;
use crate::errors::PaymentError;
use crate::handlers::payment_handler::AppState;

pub async fn handle_stripe_webhook(
    State(_state): State<AppState>,
    headers: HeaderMap,
    Json(payload): Json<Value>,
) -> Result<StatusCode, PaymentError> {
    let sig = headers.get("stripe-signature")
        .and_then(|v| v.to_str().ok())
        .ok_or(PaymentError::InvalidWebhookSignature)?;

    if sig.is_empty() {
        return Err(PaymentError::InvalidWebhookSignature);
    }

    let event_type = payload.get("type")
        .and_then(|v| v.as_str())
        .unwrap_or("unknown");

    tracing::info!("Received Stripe Webhook Event: {}", event_type);

    Ok(StatusCode::OK)
}
