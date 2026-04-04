-- PostgreSQL sample schema and data for Month 1 task

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    order_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL
);

INSERT INTO users (name, email)
VALUES
    ('Alice Johnson', 'alice@example.com'),
    ('Bob Smith', 'bob@example.com'),
    ('Carol Lee', 'carol@example.com');

INSERT INTO orders (user_id, order_date, total_amount, status)
VALUES
    (1, '2026-04-01 10:15:00+00', 125.50, 'pending'),
    (1, '2026-04-02 14:30:00+00', 75.00, 'completed'),
    (2, '2026-04-03 09:00:00+00', 210.99, 'shipped'),
    (3, '2026-04-04 16:45:00+00', 55.25, 'completed');
