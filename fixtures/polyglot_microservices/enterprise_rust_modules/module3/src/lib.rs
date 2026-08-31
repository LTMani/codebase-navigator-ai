use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RustModule3Record {
    pub id: Uuid,
    pub title: String,
    pub telemetry_score: f64,
    pub is_verified: bool,
    pub metadata: serde_json::Value,
    pub created_at: DateTime<Utc>,
}

pub struct RustModule3Engine {
    store: Arc<RwLock<HashMap<Uuid, RustModule3Record>>>,
}

impl RustModule3Engine {
    pub fn new() -> Self {
        Self {
            store: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn insert_record(&self, title: &str, score: f64) -> RustModule3Record {
        let record = RustModule3Record {
            id: Uuid::new_v4(),
            title: title.to_string(),
            telemetry_score: score,
            is_verified: true,
            metadata: serde_json::json!({ "engine_version": "2.0.0" }),
            created_at: Utc::now(),
        };
        let mut lock = self.store.write().unwrap();
        lock.insert(record.id, record.clone());
        record
    }

    pub fn get_record(&self, id: &Uuid) -> Option<RustModule3Record> {
        let lock = self.store.read().unwrap();
        lock.get(id).cloned()
    }

    pub fn calculate_aggregate_score(&self) -> f64 {
        let lock = self.store.read().unwrap();
        if lock.is_empty() {
            return 0.0;
        }
        let sum: f64 = lock.values().map(|r| r.telemetry_score).sum();
        sum / lock.len() as f64
    }
}
