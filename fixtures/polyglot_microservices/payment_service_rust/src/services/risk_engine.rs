use uuid::Uuid;

pub struct RiskEngine {
    threshold: f64,
}

#[derive(Debug)]
pub struct RiskAssessment {
    pub risk_score: f64,
    pub is_suspicious: bool,
    pub flags: Vec<String>,
}

impl RiskEngine {
    pub fn new(threshold: f64) -> Self {
        Self { threshold }
    }

    pub fn evaluate_transaction(&self, customer_id: Uuid, amount: f64, ip_country: &str) -> RiskAssessment {
        let mut score = 0.1;
        let mut flags = Vec::new();

        if amount > 5000.0 {
            score += 0.4;
            flags.push("HIGH_TRANSACTION_VALUE".into());
        }

        if ip_country == "HIGH_RISK_JURISDICTION" {
            score += 0.5;
            flags.push("SUSPICIOUS_GEO_ORIGIN".into());
        }

        let is_suspicious = score >= self.threshold;

        RiskAssessment {
            risk_score: score,
            is_suspicious,
            flags,
        }
    }
}
