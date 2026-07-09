
-- 1. TRIGGERS
-- ===========

-- Trigger to prevent negative balance
CREATE OR REPLACE FUNCTION prevent_negative_balance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.balance < 0 THEN
        RAISE EXCEPTION 'Insufficient funds: Cannot set negative balance';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_negative_balance
    BEFORE UPDATE OF balance ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION prevent_negative_balance();

-- Trigger to auto-capture timestamp (automatically handled by DEFAULT CURRENT_TIMESTAMP)
-- But we can create an update trigger to track last modified time
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add holder_name column to audit table if it doesn't exist
ALTER TABLE audit ADD COLUMN IF NOT EXISTS holder_name VARCHAR(100);

CREATE OR REPLACE FUNCTION update_account_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_account_time
    BEFORE UPDATE ON accounts
    FOR EACH ROW
    EXECUTE FUNCTION update_account_timestamp();

-- Trigger to store failed transactions
CREATE TABLE IF NOT EXISTS failed_transactions (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(50),
    action VARCHAR(100),
    amount DECIMAL(15, 2),
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);

CREATE OR REPLACE FUNCTION log_failed_transaction()
RETURNS TRIGGER AS $$
BEGIN
    -- This is a placeholder - in practice, you'd call this from application code
    -- when a transaction fails
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to block withdrawals above a limit (e.g., $10,000)
CREATE OR REPLACE FUNCTION check_withdrawal_limit()
RETURNS TRIGGER AS $$
BEGIN
    -- Check if this is a withdrawal (negative amount in audit)
    IF NEW.action = 'Amount withdrawn' AND NEW.amount > 10000 THEN
        INSERT INTO failed_transactions (account_number, action, amount, error_message)
        VALUES (NEW.account_number, NEW.action, NEW.amount, 'Withdrawal exceeds $10,000 limit');
        RAISE EXCEPTION 'Withdrawal amount exceeds $10,000 limit';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: We'll attach this to the audit table insert, but commented out for now
-- CREATE TRIGGER withdrawal_limit_check
--     BEFORE INSERT ON audit
--     FOR EACH ROW
--     EXECUTE FUNCTION check_withdrawal_limit();

-- 2. MATERIALIZED VIEWS
-- ===================

-- Materialized view for total deposits of each account
CREATE MATERIALIZED VIEW IF NOT EXISTS account_deposits AS
SELECT 
    account_number,
    holder_name,
    SUM(amount) as total_deposits,
    COUNT(*) as deposit_count
FROM audit 
WHERE action = 'Amount deposited'
GROUP BY account_number, holder_name
ORDER BY total_deposits DESC;

-- Materialized view for total withdrawals of each account
CREATE MATERIALIZED VIEW IF NOT EXISTS account_withdrawals AS
SELECT 
    account_number,
    holder_name,
    SUM(amount) as total_withdrawals,
    COUNT(*) as withdrawal_count
FROM audit 
WHERE action = 'Amount withdrawn'
GROUP BY account_number, holder_name
ORDER BY total_withdrawals DESC;

-- Materialized view for last 10 transactions
CREATE MATERIALIZED VIEW IF NOT EXISTS recent_transactions AS
SELECT 
    account_number,
    holder_name,
    action,
    amount,
    timestamp
FROM audit
ORDER BY timestamp DESC
LIMIT 10;

-- Materialized view for most active users (by transaction count)
CREATE MATERIALIZED VIEW IF NOT EXISTS most_active_users AS
SELECT 
    account_number,
    holder_name,
    COUNT(*) as transaction_count
FROM audit
GROUP BY account_number, holder_name
ORDER BY transaction_count DESC
LIMIT 20;

-- 3. RELATIONSHIPS
-- ===============
-- Already established: accounts (PK) → audit (FK)
-- One-to-many relationship: One account = multiple audit logs

-- 4. SUBQUERIES
-- ============

-- Find accounts with deposits > $10,000
SELECT DISTINCT a.account_number, a.name as holder_name
FROM accounts a
JOIN audit au ON a.account_number = au.account_number
WHERE au.action = 'Amount deposited'
AND a.account_number IN (
    SELECT account_number
    FROM audit
    WHERE action = 'Amount deposited'
    GROUP BY account_number
    HAVING SUM(amount) > 10000
);

-- Accounts with more than 5 audit logs
SELECT a.account_number, a.name as holder_name, COUNT(au.id) as audit_log_count
FROM accounts a
JOIN audit au ON a.account_number = au.account_number
GROUP BY a.account_number, a.name
HAVING COUNT(au.id) > 5
ORDER BY audit_log_count DESC;

-- Most active user (max audits logged)
SELECT a.account_number, a.name as holder_name, COUNT(au.id) as transaction_count
FROM accounts a
JOIN audit au ON a.account_number = au.account_number
GROUP BY a.account_number, a.name
ORDER BY COUNT(au.id) DESC
LIMIT 1;

-- 5. INDEXING
-- ==========

-- Create index on account_number for better performance
CREATE INDEX IF NOT EXISTS idx_accounts_account_number ON accounts(account_number);
CREATE INDEX IF NOT EXISTS idx_audit_account_number ON audit(account_number);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit(action);

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_audit_account_action ON audit(account_number, action);

-- 6. TRANSACTIONS (ACID Properties Example)
-- ======================================

-- BEGIN/COMMIT example for transferring money between accounts
/*
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE account_number = 'ACCOUNT1';
UPDATE accounts SET balance = balance + 500 WHERE account_number = 'ACCOUNT2';
COMMIT;
*/

-- ROLLBACK example
/*
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE account_number = 'ACCOUNT1';
-- Something goes wrong...
ROLLBACK;
-- The transaction is rolled back, no changes are made
*/

-- 7. USER MANAGEMENT (Optional)
-- ===========================

-- Create a read-only user for reporting
/*
CREATE USER bank_report_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE BankData TO bank_report_user;
GRANT USAGE ON SCHEMA public TO bank_report_user;
GRANT SELECT ON accounts, audit TO bank_report_user;
GRANT SELECT ON account_deposits, account_withdrawals, recent_transactions, most_active_users TO bank_report_user;
*/

-- Create an admin user with full privileges
/*
CREATE USER bank_admin WITH PASSWORD 'admin_secure_password';
GRANT ALL PRIVILEGES ON DATABASE BankData TO bank_admin;
GRANT ALL PRIVILEGES ON TABLE accounts, audit, failed_transactions TO bank_admin;
GRANT ALL PRIVILEGES ON SEQUENCE accounts_account_number_seq, audit_id_seq, failed_transactions_id_seq TO bank_admin;
*/

-- 8. PROCEDURES & FUNCTIONS
-- =======================

-- Function for interest calculation (5% annual interest)
CREATE OR REPLACE FUNCTION calculate_interest(principal DECIMAL, rate DECIMAL, time_years DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
    RETURN principal * rate * time_years;
END;
$$ LANGUAGE plpgsql;

-- Procedure to bulk-delete old audits (older than 1 year)
CREATE OR REPLACE PROCEDURE delete_old_audits(cutoff_date DATE DEFAULT CURRENT_DATE - INTERVAL '1 year')
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM audit WHERE timestamp < cutoff_date;
    COMMIT;
END;
$$;

-- Procedure for monthly report
CREATE OR REPLACE PROCEDURE generate_monthly_report(report_month DATE DEFAULT CURRENT_DATE)
LANGUAGE plpgsql AS $$
DECLARE
    total_deposits DECIMAL(15,2);
    total_withdrawals DECIMAL(15,2);
    active_accounts INTEGER;
BEGIN
    -- Calculate total deposits for the month
    SELECT COALESCE(SUM(amount), 0) INTO total_deposits
    FROM audit 
    WHERE action = 'Amount deposited' 
    AND DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', report_month);
    
    -- Calculate total withdrawals for the month
    SELECT COALESCE(SUM(amount), 0) INTO total_withdrawals
    FROM audit 
    WHERE action = 'Amount withdrawn' 
    AND DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', report_month);
    
    -- Count active accounts
    SELECT COUNT(DISTINCT account_number) INTO active_accounts
    FROM audit 
    WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', report_month);
    
    -- Output the report (in a real scenario, you might insert this into a report table)
    RAISE NOTICE 'Monthly Report for %', DATE_TRUNC('month', report_month);
    RAISE NOTICE 'Total Deposits: $%', total_deposits;
    RAISE NOTICE 'Total Withdrawals: $%', total_withdrawals;
    RAISE NOTICE 'Active Accounts: %', active_accounts;
END;
$$;

-- 9. BACKUP & RESTORE COMMANDS (For pgAdmin)
-- =======================================

-- Backup command (to be run in pgAdmin or psql)
-- pg_dump -U postgres -d BankData -f bank_backup.backup

-- Restore command (to be run in pgAdmin or psql)
-- pg_restore -U postgres -d BankData bank_backup.backup

-- Refresh materialized views
REFRESH MATERIALIZED VIEW account_deposits;
REFRESH MATERIALIZED VIEW account_withdrawals;
REFRESH MATERIALIZED VIEW recent_transactions;
REFRESH MATERIALIZED VIEW most_active_users;