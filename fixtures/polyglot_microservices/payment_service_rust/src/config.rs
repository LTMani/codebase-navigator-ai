use std::env;

#[derive(Clone, Debug)]
pub struct AppConfig {
    pub host: String,
    pub port: u16,
    pub database_url: String,
    pub stripe_secret_key: String,
    pub stripe_webhook_secret: String,
    pub risk_score_threshold: f64,
}

impl AppConfig {
    pub fn from_env() -> Result<Self, String> {
        let host = env::var("APP_HOST").unwrap_or_else(|_| "0.0.0.0".to_string());
        let port = env::var("APP_PORT")
            .unwrap_or_else(|_| "8082".to_string())
            .parse::<u16>()
            .map_err(|e| format!("Invalid APP_PORT: {}", e))?;

        let database_url = env::var("DATABASE_URL")
            .unwrap_or_else(|_| "postgres://postgres:postgres@localhost:5432/payments_db".to_string());

        let stripe_secret_key = env::var("STRIPE_SECRET_KEY")
            .unwrap_or_else(|_| "sk_test_mock_stripe_key_994883".to_string());

        let stripe_webhook_secret = env::var("STRIPE_WEBHOOK_SECRET")
            .unwrap_or_else(|_| "whsec_mock_stripe_webhook_secret".to_string());

        let risk_score_threshold = env::var("RISK_SCORE_THRESHOLD")
            .unwrap_or_else(|_| "0.75".to_string())
            .parse::<f64>()
            .unwrap_or(0.75);

        Ok(Self {
            host,
            port,
            database_url,
            stripe_secret_key,
            stripe_webhook_secret,
            risk_score_threshold,
        })
    }
}
