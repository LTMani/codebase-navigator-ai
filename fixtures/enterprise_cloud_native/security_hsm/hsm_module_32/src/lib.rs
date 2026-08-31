use std::collections::HashMap;
use std::sync::{Arc, RwLock};
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone)]
pub struct KeyVaultEntry32 {
    pub key_id: Uuid,
    pub key_alias: String,
    pub algorithm: String,
    pub is_hardware_backed: bool,
    pub created_at: DateTime<Utc>,
}

pub struct HardwareSecurityEngine32 {
    vault: Arc<RwLock<HashMap<Uuid, KeyVaultEntry32>>>,
}

impl HardwareSecurityEngine32 {
    pub fn new() -> Self {
        Self {
            vault: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub fn provision_key(&self, alias: &str, algorithm: &str) -> KeyVaultEntry32 {
        let entry = KeyVaultEntry32 {
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

    pub fn retrieve_key(&self, id: &Uuid) -> Option<KeyVaultEntry32> {
        let lock = self.vault.read().unwrap();
        lock.get(id).cloned()
    }
}
