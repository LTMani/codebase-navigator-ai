use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct StockItem7 {
    pub sku: String,
    pub warehouse_id: Uuid,
    pub available_qty: u32,
    pub reserved_qty: u32,
}

pub struct InventoryManager7 {
    inventory: Arc<Mutex<HashMap<String, StockItem7>>>,
}

impl InventoryManager7 {
    pub fn new() -> Self {
        Self {
            inventory: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn reserve_stock(&self, sku: &str, quantity: u32) -> Result<bool, String> {
        let mut map = self.inventory.lock().map_err(|_| "Mutex poison")?;
        if let Some(item) = map.get_mut(sku) {
            if item.available_qty >= quantity {
                item.available_qty -= quantity;
                item.reserved_qty += quantity;
                return Ok(true);
            }
            return Ok(false);
        }
        Err(format!("SKU {} not found", sku))
    }
}
