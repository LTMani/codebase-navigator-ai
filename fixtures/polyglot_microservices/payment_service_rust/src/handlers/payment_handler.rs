use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use chrono::Utc;
use serde_json::json;
use std::sync::Arc;
use uuid::Uuid;

use crate::errors::PaymentError;
use crate::models::currency::Currency;
use crate::models::payment::{CreatePaymentRequest, PaymentIntent, PaymentResponse, PaymentStatus};
use crate::repository::payment_repo::InMemoryPaymentRepository;
use crate::services::risk_engine::RiskEngine;
use crate::services::stripe_adapter::StripeAdapter;

#[derive(Clone)]
pub struct AppState {
    pub repo: InMemoryPaymentRepository,
    pub stripe: Arc<StripeAdapter>,
    pub risk_engine: Arc<RiskEngine>,
}

pub async fn create_payment_intent(
    State(state): State<AppState>,
    Json(payload): Json<CreatePaymentRequest>,
) -> Result<(StatusCode, Json<PaymentResponse>), PaymentError> {
    let currency = Currency::from_str(&payload.currency)
        .ok_or_else(|| PaymentError::ValidationError(format!("Unsupported currency: {}", payload.currency)))?;

    if payload.amount <= 0.0 {
        return Err(PaymentError::ValidationError("Payment amount must be greater than zero".into()));
    }

    let risk = state.risk_engine.evaluate_transaction(payload.customer_id, payload.amount, "US");
    if risk.is_suspicious {
        return Err(PaymentError::GatewayError(format!("Payment flagged by fraud detection rules: {:?}", risk.flags)));
    }

    let amount_cents = (payload.amount * 100.0).round() as i64;
    let provider_id = state.stripe.create_charge(amount_cents, &payload.currency, &payload.payment_method_id).await?;

    let now = Utc::now();
    let payment_id = Uuid::new_v4();
    let intent = PaymentIntent {
        id: payment_id,
        customer_id: payload.customer_id,
        amount: payload.amount,
        currency,
        status: PaymentStatus::Captured,
        provider_payment_id: Some(provider_id),
        client_secret: format!("pi_{}_secret_{}", payment_id.simple(), Uuid::new_v4().simple()),
        description: payload.description,
        metadata: payload.metadata.unwrap_or_else(|| json!({})),
        created_at: now,
        updated_at: now,
    };

    state.repo.insert(intent.clone()).await?;

    let response = PaymentResponse {
        payment_id: intent.id,
        amount: intent.amount,
        currency: intent.currency,
        status: intent.status,
        client_secret: intent.client_secret,
        created_at: intent.created_at,
    };

    Ok((StatusCode::CREATED, Json(response)))
}

pub async fn get_payment(
    State(state): State<AppState>,
    Path(id): Path<Uuid>,
) -> Result<Json<PaymentIntent>, PaymentError> {
    let payment = state.repo.find_by_id(id).await?
        .ok_or(PaymentError::NotFound(id))?;

    Ok(Json(payment))
}
