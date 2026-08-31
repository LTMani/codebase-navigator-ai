use crate::errors::PaymentError;
use crate::models::payment::PaymentIntent;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use uuid::Uuid;

#[derive(Clone)]
pub struct InMemoryPaymentRepository {
    storage: Arc<RwLock<HashMap<Uuid, PaymentIntent>>>,
}

impl InMemoryPaymentRepository {
    pub fn new() -> Self {
        Self {
            storage: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    pub async fn insert(&self, payment: PaymentIntent) -> Result<(), PaymentError> {
        let mut map = self.storage.write().await;
        map.insert(payment.id, payment);
        Ok(())
    }

    pub async fn find_by_id(&self, id: Uuid) -> Result<Option<PaymentIntent>, PaymentError> {
        let map = self.storage.read().await;
        Ok(map.get(&id).cloned())
    }

    pub async fn update(&self, payment: PaymentIntent) -> Result<(), PaymentError> {
        let mut map = self.storage.write().await;
        map.insert(payment.id, payment);
        Ok(())
    }
}
