-- External DB: Schema and Dummy Data
-- This simulates an Odoo/ERP-style source database

CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    order_ref   VARCHAR(50)     NOT NULL,
    customer    VARCHAR(100)    NOT NULL,
    product     VARCHAR(100)    NOT NULL,
    quantity    INTEGER         NOT NULL,
    unit_price  NUMERIC(10, 2)  NOT NULL,
    status      VARCHAR(20)     NOT NULL,  -- 'confirmed', 'pending', 'cancelled'
    created_at  TIMESTAMP       DEFAULT NOW()
);

-- Insert dummy data (mix of statuses — ETL will only pull 'confirmed')
INSERT INTO orders (order_ref, customer, product, quantity, unit_price, status) VALUES
  ('ORD-001', 'Alice Corp',    'Widget A',  10, 25.00,  'confirmed'),
  ('ORD-002', 'Bob Ltd',       'Widget B',   5, 50.00,  'pending'),
  ('ORD-003', 'Charlie Inc',   'Widget C',  20, 15.00,  'confirmed'),
  ('ORD-004', 'Delta LLC',     'Widget A',   3, 25.00,  'cancelled'),
  ('ORD-005', 'Echo Pvt',      'Widget D',  15, 30.00,  'confirmed'),
  ('ORD-006', 'Foxtrot Co',    'Widget B',   8, 50.00,  'pending'),
  ('ORD-007', 'Golf GmbH',     'Widget C',  12, 15.00,  'confirmed'),
  ('ORD-008', 'Hotel SA',      'Widget A',   2, 25.00,  'cancelled'),
  ('ORD-009', 'India Pvt',     'Widget D',   7, 30.00,  'confirmed'),
  ('ORD-010', 'Juliet Corp',   'Widget B',   1, 50.00,  'pending');
