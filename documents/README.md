# LeadEngine Documentation

Welcome to the LeadEngine documentation! This directory contains comprehensive documentation for all aspects of the application.

## 📚 Documentation Index

### Getting Started
- **[QUICK_START.md](QUICK_START.md)** - Quick start guide for running the application
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - Initial setup completion guide
- **[SEED_DATA_COMPLETE.md](SEED_DATA_COMPLETE.md)** - Seed data information

### System Architecture
- **[SCRAPE_JOB_SYSTEM.md](SCRAPE_JOB_SYSTEM.md)** - Complete scrape job system documentation
- **[RABBITMQ_INTEGRATION.md](RABBITMQ_INTEGRATION.md)** - RabbitMQ integration guide
- **[WORKER_GUIDE.md](WORKER_GUIDE.md)** - Worker setup and usage

### API Documentation
- **[API_SCRAPE_JOBS.md](API_SCRAPE_JOBS.md)** - Scrape job API endpoints
- **[DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)** - Database schema reference

### Database
- **[MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md)** - Database migration guide
- **[UPDATE_SUMMARY.md](UPDATE_SUMMARY.md)** - Recent updates summary

---

## 🚀 Quick Links

### For Developers

**Starting the Application:**
```bash
# Terminal 1 - API Server
cd backend
.\start_api.ps1

# Terminal 2 - Worker
cd backend
.\start_worker.ps1
```

**Testing:**
- Swagger UI: http://localhost:8000/docs
- RabbitMQ Management: http://localhost:15672

**Database:**
```bash
# Seed data
.\venv\Scripts\python.exe seeds\seed_all.py

# Run migration
.\venv\Scripts\python.exe migrations\your_migration.py upgrade
```

### For Understanding the System

1. **Start Here:** [QUICK_START.md](QUICK_START.md)
2. **Understand Architecture:** [SCRAPE_JOB_SYSTEM.md](SCRAPE_JOB_SYSTEM.md)
3. **Learn RabbitMQ:** [RABBITMQ_INTEGRATION.md](RABBITMQ_INTEGRATION.md)
4. **Setup Worker:** [WORKER_GUIDE.md](WORKER_GUIDE.md)
5. **API Reference:** [API_SCRAPE_JOBS.md](API_SCRAPE_JOBS.md)

---

## 📖 Documentation by Topic

### Architecture & Design

| Document | Description |
|----------|-------------|
| [SCRAPE_JOB_SYSTEM.md](SCRAPE_JOB_SYSTEM.md) | Complete system architecture, data flow, and code examples |
| [RABBITMQ_INTEGRATION.md](RABBITMQ_INTEGRATION.md) | Message queue integration, patterns, and best practices |
| [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) | Database tables, relationships, and indexes |

### Development

| Document | Description |
|----------|-------------|
| [WORKER_GUIDE.md](WORKER_GUIDE.md) | Worker setup, scaling, and troubleshooting |
| [API_SCRAPE_JOBS.md](API_SCRAPE_JOBS.md) | API endpoints, request/response formats |
| [MIGRATION_COMPLETE.md](MIGRATION_COMPLETE.md) | Database migration process |

### Setup & Configuration

| Document | Description |
|----------|-------------|
| [QUICK_START.md](QUICK_START.md) | Step-by-step startup guide |
| [SETUP_COMPLETE.md](SETUP_COMPLETE.md) | Initial setup verification |
| [SEED_DATA_COMPLETE.md](SEED_DATA_COMPLETE.md) | Test data and credentials |

---

## 🎯 Common Tasks

### Create a Scrape Job

1. Open Swagger: http://localhost:8000/docs
2. Navigate to `POST /api/v1/jobs/scrape`
3. Use this payload:
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

### Check Job Status

```bash
GET /api/v1/jobs/scrape/{job_id}
```

### Monitor RabbitMQ

1. Open: http://localhost:15672
2. Login: guest / guest
3. Check queue: `scrape_jobs`

### View Database

```sql
-- Check jobs
SELECT * FROM scrape_jobs ORDER BY created_at DESC LIMIT 5;

-- Check raw leads
SELECT * FROM raw_leads ORDER BY scraped_at DESC LIMIT 5;
```

---

## 🔧 Troubleshooting

### Worker Not Consuming Messages

**Problem:** Messages stuck in queue

**Solution:**
1. Check worker is running
2. Verify RabbitMQ connection
3. Check worker logs

**See:** [WORKER_GUIDE.md](WORKER_GUIDE.md#troubleshooting)

### Database Connection Failed

**Problem:** Can't connect to PostgreSQL

**Solution:**
1. Check PostgreSQL is running
2. Verify `.env` configuration
3. Test connection

**See:** [QUICK_START.md](QUICK_START.md#troubleshooting)

### API Returns 500 Error

**Problem:** Internal server error

**Solution:**
1. Check API logs
2. Verify database schema
3. Check seed data exists

**See:** [API_SCRAPE_JOBS.md](API_SCRAPE_JOBS.md#error-handling)

---

## 📝 Contributing

When adding new features:

1. **Update Documentation** - Keep docs in sync with code
2. **Add Examples** - Provide code examples
3. **Document APIs** - Update API documentation
4. **Migration Scripts** - Create migration for schema changes

---

## 🎊 Need Help?

- **Architecture Questions:** See [SCRAPE_JOB_SYSTEM.md](SCRAPE_JOB_SYSTEM.md)
- **RabbitMQ Issues:** See [RABBITMQ_INTEGRATION.md](RABBITMQ_INTEGRATION.md)
- **Worker Problems:** See [WORKER_GUIDE.md](WORKER_GUIDE.md)
- **API Questions:** See [API_SCRAPE_JOBS.md](API_SCRAPE_JOBS.md)
- **Database Issues:** See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

---

## 📅 Last Updated

This documentation was last updated on: **2026-02-17**

For the latest updates, check the individual documentation files.
