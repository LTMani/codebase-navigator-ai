use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone)]
pub struct KeyVaultEntry46 {
    pub key_id: Uuid,
    pub key_alias: String,
    pub algorithm: String,
    pub is_hardware_backed: bool,
    pub created_at: DateTime<Utc>,
}

pub struct HardwareSecurityEngine46 {
    vault: Arc<RwLock<HashMap<Uuid, KeyVaultEntry46>>>,
}

impl HardwareSecurityEngine46 {
    pub fn new() -> Self {
        Self {
            vault: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn provision_key(&self, alias: &str, algorithm: &str) -> KeyVaultEntry46 {
        let entry = KeyVaultEntry46 {
            key_id: Uuid::new_v4(),
            key_alias: alias.to_string(),
            algorithm: algorithm.to_string(),
            is_hardware_backed: true,
            created_at: Utc::now(),
        };
        let mut lock = self.vault.write().unwrap();
        lock.insert(entry.key_id, entry.clone());
        entry
    }

    pub fn retrieve_key(&self, id: &Uuid) -> Option<KeyVaultEntry46> {
        let lock = self.vault.read().unwrap();
        lock.get(id).cloned()
    }
}
