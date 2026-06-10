-- Reference seed data for integration tests
INSERT INTO orders (client_order_id, symbol, side, quantity, price, order_type, status)
VALUES
    ('SEED-001', 'AAPL', 'BUY',  100, 150.00, 'LIMIT',  'NEW'),
    ('SEED-002', 'TSLA', 'SELL', 50,  NULL,   'MARKET', 'ROUTED'),
    ('SEED-003', 'MSFT', 'BUY',  200, 300.00, 'LIMIT',  'EXECUTED'),
    ('SEED-004', 'AMZN', 'SELL', 75,  NULL,   'MARKET', 'CANCELLED')
ON CONFLICT (client_order_id) DO NOTHING;
