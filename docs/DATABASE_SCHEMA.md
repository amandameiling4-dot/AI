# Database Schema

## Users
- id: integer primary key
- email: varchar unique
- password_hash: varchar
- created_at: timestamp

## App Records
- id: integer primary key
- user_email: varchar
- project_name: varchar
- description: text
- app_type: varchar
- generated_files: text
- security_checks: text
- created_at: timestamp

## Thought Records
- id: integer primary key
- user_email: varchar
- content: text
- source: varchar
- created_at: timestamp

## Connected App Records
- id: integer primary key
- user_email: varchar
- app_name: varchar
- app_id: varchar unique
- created_at: timestamp

## Payment Records
- id: integer primary key
- user_email: varchar
- receipt_id: varchar unique
- amount: varchar
- currency: varchar
- status: varchar
- paid_at: varchar
- created_at: timestamp
