-- Default Nodal Escrow and Merchant accounts
INSERT INTO ledger_accounts (id, account_number, account_type, currency, current_balance, created_at, updated_at)
VALUES 
('a0000000-0000-0000-0000-000000000001', 'ESCROW_NODAL_INR_01', 'NODAL_ESCROW', 'INR', 10000000.0000, NOW(), NOW()),
('a0000000-0000-0000-0000-000000000002', 'PLATFORM_REVENUE_01', 'PLATFORM_FEE', 'INR', 0.0000, NOW(), NOW()),
('a0000000-0000-0000-0000-000000000003', 'REFUND_RESERVE_01', 'REFUND_RESERVE', 'INR', 500000.0000, NOW(), NOW());

INSERT INTO merchants (id, api_key, business_name, webhook_url, active, created_at, updated_at)
VALUES 
('m0000000-0000-0000-0000-000000000001', 'mk_live_bharat_pay_998877', 'Flipkart India Pvt Ltd', 'https://webhook.site/test', TRUE, NOW(), NOW());
