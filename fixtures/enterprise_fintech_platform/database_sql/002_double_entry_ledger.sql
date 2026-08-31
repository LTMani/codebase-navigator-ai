-- Double Entry Ledger Stored Procedures and Triggers
CREATE TABLE IF NOT EXISTS journal_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL REFERENCES transactions(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    entry_type VARCHAR(16) NOT NULL CHECK (entry_type IN ('DEBIT', 'CREDIT')),
    amount NUMERIC(18, 4) NOT NULL CHECK (amount > 0),
    balance_after NUMERIC(18, 4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION post_ledger_entry(
    p_transaction_id UUID,
    p_account_id UUID,
    p_entry_type VARCHAR,
    p_amount NUMERIC
) RETURNS UUID AS $$
DECLARE
    v_current_balance NUMERIC(18, 4);
    v_new_balance NUMERIC(18, 4);
    v_entry_id UUID;
BEGIN
    SELECT balance INTO v_current_balance FROM accounts WHERE id = p_account_id FOR UPDATE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Account % not found', p_account_id;
    END IF;

    IF p_entry_type = 'CREDIT' THEN
        v_new_balance := v_current_balance + p_amount;
    ELSIF p_entry_type = 'DEBIT' THEN
        IF v_current_balance < p_amount THEN
            RAISE EXCEPTION 'Insufficient balance in account %', p_account_id;
        END IF;
        v_new_balance := v_current_balance - p_amount;
    ELSE
        RAISE EXCEPTION 'Invalid entry type %', p_entry_type;
    END IF;

    UPDATE accounts SET balance = v_new_balance, updated_at = CURRENT_TIMESTAMP WHERE id = p_account_id;

    INSERT INTO journal_entries (transaction_id, account_id, entry_type, amount, balance_after)
    VALUES (p_transaction_id, p_account_id, p_entry_type, p_amount, v_new_balance)
    RETURNING id INTO v_entry_id;

    RETURN v_entry_id;
END;
$$ LANGUAGE plpgsql;
