use payment_service_rust::models::currency::Currency;
use payment_service_rust::models::wallet::Wallet;
use uuid::Uuid;

#[test]
fn test_wallet_creation_and_balance() {
    let owner = Uuid::new_v4();
    let mut wallet = Wallet::new(owner, Currency::USD);
    assert_eq!(wallet.available_balance, 0.0);
    assert_eq!(wallet.total_balance(), 0.0);

    wallet.available_balance += 150.0;
    assert!(wallet.can_debit(100.0));
    assert!(!wallet.can_debit(200.0));
}
