mod config;
mod errors;
mod handlers;
mod models;
mod repository;
mod services;

use axum::{
    routing::{get, post},
    Router,
};
use config::AppConfig;
use handlers::payment_handler::{create_payment_intent, get_payment, AppState};
use handlers::webhook_handler::handle_stripe_webhook;
use repository::payment_repo::InMemoryPaymentRepository;
use services::risk_engine::RiskEngine;
use services::stripe_adapter::StripeAdapter;
use std::sync::Arc;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

#[tokio::main]
async fn main() {
    tracing_subscriber::registry()
        .with(tracing_subscriber::EnvFilter::new("info"))
        .with(tracing_subscriber::fmt::layer())
        .init();

    let cfg = AppConfig::from_env().expect("Failed to parse configuration");

    let repo = InMemoryPaymentRepository::new();
    let stripe = Arc::new(StripeAdapter::new(cfg.stripe_secret_key.clone()));
    let risk_engine = Arc::new(RiskEngine::new(cfg.risk_score_threshold));

    let state = AppState {
        repo,
        stripe,
        risk_engine,
    };

    let app = Router::new()
        .route("/health", get(|| async { "Payment Service Healthy" }))
        .route("/api/v1/payments", post(create_payment_intent))
        .route("/api/v1/payments/:id", get(get_payment))
        .route("/api/v1/webhooks/stripe", post(handle_stripe_webhook))
        .with_state(state);

    let addr = format!("{}:{}", cfg.host, cfg.port);
    tracing::info!("Payment service listening on {}", addr);
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
