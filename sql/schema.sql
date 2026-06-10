CREATE TABLE IF NOT EXISTS orders (
    id               SERIAL PRIMARY KEY,
    client_order_id  VARCHAR(64)    NOT NULL UNIQUE,
    symbol           VARCHAR(16)    NOT NULL,
    side             VARCHAR(4)     NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity         NUMERIC(18,6)  NOT NULL CHECK (quantity > 0),
    price            NUMERIC(18,6),
    order_type       VARCHAR(16)    NOT NULL CHECK (order_type IN ('MARKET', 'LIMIT')),
    status           VARCHAR(32)    NOT NULL DEFAULT 'NEW',
    venue            VARCHAR(32),
    rejection_reason TEXT,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_orders_status        ON orders (status);
CREATE INDEX IF NOT EXISTS idx_orders_symbol        ON orders (symbol);
CREATE INDEX IF NOT EXISTS idx_orders_client_order  ON orders (client_order_id);
