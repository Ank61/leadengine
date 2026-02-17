# Seeds Directory

This directory contains seed scripts to populate the database with test data.

## Available Seed Scripts

### 1. `seed_users.py`
Creates test users in the `users` table.

**Test Users Created:**
- **test@example.com** (ID: `123e4567-e89b-12d3-a456-426614174000`)
  - Role: user
  - Password: password123
  
- **admin@example.com** (ID: `223e4567-e89b-12d3-a456-426614174001`)
  - Role: admin
  - Password: password123
  
- **demo@example.com** (ID: `323e4567-e89b-12d3-a456-426614174002`)
  - Role: user
  - Password: password123

### 2. `seed_subscriptions.py`
Creates test subscriptions for the test users.

**Subscriptions Created:**
- **Pro Plan** for test@example.com
  - 10,000 scrapes/month
  - 5,000 leads/month
  
- **Enterprise Plan** for admin@example.com
  - 100,000 scrapes/month
  - 50,000 leads/month
  
- **Free Plan** for demo@example.com
  - 100 scrapes/month
  - 50 leads/month

### 3. `seed_all.py`
Master script that runs all seed scripts in the correct order.

## Usage

### Run All Seeds
```bash
cd backend
.\venv\Scripts\python.exe seeds/seed_all.py
```

### Run Individual Seeds
```bash
# Seed users only
.\venv\Scripts\python.exe seeds/seed_users.py

# Seed subscriptions only
.\venv\Scripts\python.exe seeds/seed_subscriptions.py
```

## Notes

- Seeds are **idempotent** - running them multiple times won't create duplicates
- Seeds check if data already exists before inserting
- Foreign key constraints are respected (users must exist before subscriptions)
- All passwords are hashed using bcrypt

## After Seeding

You can use the test user ID in your API requests:

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "industry": "SaaS",
  "geography": "Sydney, Australia",
  "keywords": ["B2B", "enterprise"],
  "source_types": ["google"],
  "search_query": "saas companies sydney",
  "filters": {}
}
```
