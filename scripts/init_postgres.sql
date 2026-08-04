CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS app_records (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    app_type VARCHAR(50) NOT NULL,
    generated_files TEXT NOT NULL,
    security_checks TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS thought_records (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS connected_app_records (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    app_id VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_records (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    receipt_id VARCHAR(255) UNIQUE NOT NULL,
    amount VARCHAR(50) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    status VARCHAR(50) NOT NULL,
    paid_at VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_app_records_user_email ON app_records(user_email);
CREATE INDEX IF NOT EXISTS idx_thought_records_user_email ON thought_records(user_email);
CREATE INDEX IF NOT EXISTS idx_connected_app_records_user_email ON connected_app_records(user_email);
CREATE INDEX IF NOT EXISTS idx_payment_records_user_email ON payment_records(user_email);
