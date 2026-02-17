# LeadEngine Database Schema

## Overview
Complete database schema for the LeadEngine application with 7 core tables.

## Tables Created

### 1. **users** 
User authentication and management
- UUID primary key
- Email (unique), password hash, role
- Active status and timestamps

### 2. **subscriptions**
User subscription plans and limits
- Links to users
- Plan name, monthly scrape/lead limits
- Status, start/expiry dates

### 3. **scrape_jobs**
Tracks each frontend scrape request
- Links to users
- Status (queued, processing, completed)
- Source type, search query, filters (JSONB)
- Total found/processed counts
- Timestamps: created, started, completed

**Indexes:**
- `idx_scrape_jobs_user` on user_id
- `idx_scrape_jobs_status` on status

### 4. **raw_leads**
Unprocessed scraped data storage
- Links to users and scrape_jobs
- Raw payload (JSONB) - stores complete scraped data
- Source URL, unique data hash
- Scraped timestamp

**Indexes:**
- `idx_raw_leads_user` on user_id
- `idx_raw_leads_job` on scrape_job_id
- `idx_raw_leads_payload` GIN index on raw_payload (for fast JSON queries)

**Example raw_payload structure:**
```json
{
  "company_name": "Acme Corp",
  "website": "https://acme.com",
  "industry": "SaaS",
  "company_size": "50-100",
  "location": "Sydney, Australia",
  "contact": {
    "full_name": "John Smith",
    "job_title": "Head of Marketing",
    "email": "john@acme.com",
    "phone": "+61 400 000 000",
    "linkedin": "https://linkedin.com/in/johnsmith"
  },
  "metadata": {
    "source_url": "https://directory.com/acme",
    "scraped_at": "2026-02-15T10:00:00",
    "confidence": 0.82
  }
}
```

### 5. **leads**
Normalized, cleaned lead data
- Links to users
- Company info: name, domain, industry, size, location
- Contact info: first/last name, job title, seniority
- Contact details: email, phone, LinkedIn URL
- Confidence score, source
- Timestamps: created, updated
- **Unique constraint:** (user_id, email) - prevents duplicate emails per user

**Indexes:**
- `idx_leads_user` on user_id
- `idx_leads_email` on email
- `idx_leads_domain` on domain

### 6. **lead_enrichment**
AI intelligence and scoring layer
- Links to leads (one-to-one)
- Predicted score, intent level
- AI summary text
- Buying signal (boolean)
- Recommended channel
- Enriched timestamp

**Index:**
- `idx_enrichment_lead` on lead_id

### 7. **usage_tracking**
Monthly quota tracking per user
- Links to users
- Scrapes used, leads generated counts
- Period start/end dates

**Index:**
- `idx_usage_user` on user_id

## Relationships

```
users (1) ──< (N) subscriptions
users (1) ──< (N) scrape_jobs
users (1) ──< (N) raw_leads
users (1) ──< (N) leads
users (1) ──< (N) usage_tracking

scrape_jobs (1) ──< (N) raw_leads

leads (1) ──── (1) lead_enrichment
```

## Model Files Location

All models are in: `backend/app/models/`

- `user.py` - User model
- `subscription.py` - Subscription model
- `scrape_job.py` - ScrapeJob model
- `raw_lead.py` - RawLead model
- `lead.py` - Lead model
- `lead_enrichment.py` - LeadEnrichment model
- `usage_tracking.py` - UsageTracking model

## Usage

### Import models:
```python
from app.models import User, Subscription, ScrapeJob, RawLead, Lead, LeadEnrichment, UsageTracking
```

### Create tables:
```bash
# From backend directory
.\venv\Scripts\python.exe create_tables.py
```

### Query example:
```python
from app.db.session import SessionLocal
from app.models import Lead, LeadEnrichment

db = SessionLocal()

# Get all high-intent leads for a user
leads = db.query(Lead).join(LeadEnrichment).filter(
    Lead.user_id == user_id,
    LeadEnrichment.intent_level == "high"
).all()
```

## Notes

- All tables use UUID primary keys with `gen_random_uuid()`
- CASCADE delete ensures data integrity
- JSONB fields enable flexible schema for scraped data
- GIN indexes on JSONB enable fast JSON queries
- Timestamps use `NOW()` server defaults
- Unique constraints prevent duplicate data
