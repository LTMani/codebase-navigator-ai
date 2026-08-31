use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum PaymentError {
    #[error("Database error occurred: {0}")]
    DatabaseError(#[from] sqlx::Error),

    #[error("Payment processor gateway error: {0}")]
    GatewayError(String),

    #[error("Insufficient wallet balance: required {required}, available {available}")]
    InsufficientFunds { required: f64, available: f64 },

    #[error("Transaction not found: {0}")]
    NotFound(uuid::Uuid),

    #[error("Invalid transaction state transition from {from:?} to {to:?}")]
    InvalidStateTransition { from: String, to: String },

    #[error("Signature verification failed")]
    InvalidWebhookSignature,

    #[error("Validation failed: {0}")]
    ValidationError(String),
}

impl IntoResponse for PaymentError {
    fn into_response(self) -> Response {
        let (status, error_message) = match self {
            PaymentError::NotFound(_) => (StatusCode::NOT_FOUND, self.to_string()),
            PaymentError::InsufficientFunds { .. } => (StatusCode::UNPROCESSABLE_ENTITY, self.to_string()),
            PaymentError::InvalidWebhookSignature => (StatusCode::UNAUTHORIZED, self.to_string()),
            PaymentError::ValidationError(_) => (StatusCode::BAD_REQUEST, self.to_string()),
            PaymentError::InvalidStateTransition { .. } => (StatusCode::CONFLICT, self.to_string()),
            PaymentError::GatewayError(_) => (StatusCode::BAD_GATEWAY, self.to_string()),
            PaymentError::DatabaseError(_) => (StatusCode::INTERNAL_SERVER_ERROR, "Internal server error".into()),
        };

        let body = Json(json!({
            "success": false,
            "error": error_message,
        }));

        (status, body).into_response()
    }
}
