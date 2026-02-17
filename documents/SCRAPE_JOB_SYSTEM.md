# Scrape Job System - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [Message Queue](#message-queue)
6. [Worker Process](#worker-process)
7. [Data Flow](#data-flow)
8. [Code Examples](#code-examples)

---

## Overview

The Scrape Job System is a distributed, event-driven architecture for managing web scraping tasks. It uses:
- **FastAPI** for the REST API
- **PostgreSQL** for data persistence
- **RabbitMQ** for message queuing
- **Async Python Workers** for job processing

### Key Features
- ✅ Asynchronous job processing
- ✅ Point-to-point message pattern
- ✅ Real-time status tracking
- ✅ Automatic deduplication
- ✅ Scalable worker architecture
- ✅ Comprehensive logging

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT (Swagger/Frontend)                │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP POST
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Server                          │
│  POST /api/v1/jobs/scrape                                   │
│  - Validates request                                         │
│  - Creates job in database (status: queued)                 │
│  - Publishes message to RabbitMQ                            │
│  - Returns job details                                       │
└─────────────────────────────────────────────────────────────┘
                              ↓ AMQP Message
┌─────────────────────────────────────────────────────────────┐
│                       RabbitMQ Queue                         │
│  Queue: scrape_jobs                                          │
│  - Durable queue                                             │
│  - Persistent messages                                       │
│  - Point-to-point delivery                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓ Consumer
┌─────────────────────────────────────────────────────────────┐
│                      Worker Process                          │
│  - Listens to queue 24/7                                    │
│  - Updates job status to "running"                          │
│  - Executes scraping logic                                  │
│  - Saves results to raw_leads table                         │
│  - Updates job status to "completed"                        │
└─────────────────────────────────────────────────────────────┘
                              ↓ Results
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  - scrape_jobs: Job metadata and status                     │
│  - raw_leads: Scraped data                                  │
│  - users: User information                                   │
│  - subscriptions: User plans and limits                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### scrape_jobs Table

Stores job metadata and status information.

```sql
CREATE TABLE scrape_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'queued',  -- queued, running, completed, failed
    
    -- Scrape criteria
    industry VARCHAR(255),
    geography VARCHAR(255),
    keywords JSONB,
    source_types JSONB,
    search_query TEXT,
    filters JSONB,
    
    -- Metrics
    total_found INTEGER DEFAULT 0,
    total_processed INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_scrape_jobs_user ON scrape_jobs(user_id);
CREATE INDEX idx_scrape_jobs_status ON scrape_jobs(status);
```

**Status Values:**
- `queued` - Job created, waiting for worker
- `running` - Worker is processing the job
- `completed` - Job finished successfully
- `failed` - Job encountered an error

### raw_leads Table

Stores unprocessed scraped data.

```sql
CREATE TABLE raw_leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scrape_job_id UUID REFERENCES scrape_jobs(id) ON DELETE CASCADE,
    
    -- Data
    raw_payload JSONB NOT NULL,
    source_url TEXT,
    data_hash TEXT UNIQUE NOT NULL,
    
    -- Timestamp
    scraped_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_raw_leads_user ON raw_leads(user_id);
CREATE INDEX idx_raw_leads_job ON raw_leads(scrape_job_id);
CREATE INDEX idx_raw_leads_payload ON raw_leads USING GIN(raw_payload);
```

**raw_payload Structure:**
```json
{
  "company_name": "Acme Corp",
  "website": "https://acme.com",
  "industry": "SaaS",
  "location": "Sydney, Australia",
  "email": "contact@acme.com",
  "phone": "+1-555-0100",
  "source_url": "https://example.com/acme",
  "matched_keywords": ["B2B", "enterprise"],
  "confidence": 0.85
}
```

---

## API Endpoints

### 1. Create Scrape Job

**Endpoint:** `POST /api/v1/jobs/scrape`

**Request Body:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "industry": "SaaS",
  "geography": "Sydney, Australia",
  "keywords": ["B2B", "enterprise", "cloud"],
  "source_types": ["google", "linkedin"],
  "search_query": "saas companies sydney",
  "filters": {
    "company_size": "50-200",
    "revenue": ">1M"
  }
}
```

**Response:** `201 Created`
```json
{
  "job_id": "987fcdeb-51a2-43d7-b123-456789abcdef",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "queued",
  "industry": "SaaS",
  "geography": "Sydney, Australia",
  "keywords": ["B2B", "enterprise", "cloud"],
  "source_types": ["google", "linkedin"],
  "search_query": "saas companies sydney",
  "filters": {"company_size": "50-200", "revenue": ">1M"},
  "total_found": 0,
  "total_processed": 0,
  "created_at": "2026-02-17T16:43:24.123456",
  "started_at": null,
  "completed_at": null
}
```

**Code Location:** `app/api/v1/endpoints/scrape_jobs.py`

**Function:** `create_scrape_job()`

**What It Does:**
1. Validates request data
2. Generates unique job ID
3. Creates job record in database (status: queued)
4. Publishes message to RabbitMQ
5. Returns job details

### 2. Get Job Status

**Endpoint:** `GET /api/v1/jobs/scrape/{job_id}`

**Response:** `200 OK`
```json
{
  "job_id": "987fcdeb-51a2-43d7-b123-456789abcdef",
  "status": "completed",
  "total_found": 25,
  "total_processed": 25,
  "created_at": "2026-02-17T16:43:24.123456",
  "started_at": "2026-02-17T16:43:25.789012",
  "completed_at": "2026-02-17T16:43:30.345678"
}
```

**Code Location:** `app/api/v1/endpoints/scrape_jobs.py`

**Function:** `get_scrape_job_status()`

### 3. Get User's Jobs

**Endpoint:** `GET /api/v1/jobs/scrape/user/{user_id}`

**Query Parameters:**
- `limit` (default: 10)
- `offset` (default: 0)

**Response:** `200 OK`
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "total": 5,
  "jobs": [...]
}
```

**Code Location:** `app/api/v1/endpoints/scrape_jobs.py`

**Function:** `get_user_scrape_jobs()`

---

## Message Queue

### RabbitMQ Configuration

**Queue Name:** `scrape_jobs`

**Properties:**
- **Durable:** Yes (survives broker restart)
- **Delivery Mode:** Persistent (messages saved to disk)
- **Pattern:** Point-to-Point (one message → one consumer)
- **Prefetch Count:** 1 (process one message at a time)

### Message Format

```json
{
  "job_id": "987fcdeb-51a2-43d7-b123-456789abcdef",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "industry": "SaaS",
  "geography": "Sydney, Australia",
  "keywords": ["B2B", "enterprise", "cloud"],
  "source_types": ["google", "linkedin"],
  "search_query": "saas companies sydney",
  "filters": {"company_size": "50-200"}
}
```

### Publisher

**Code Location:** `app/mq/publisher.py`

**Class:** `RabbitMQPublisher`

**Key Methods:**
- `connect()` - Establish connection to RabbitMQ
- `publish_message(queue_name, message)` - Publish message to queue
- `close()` - Close connection

**Usage:**
```python
from app.mq.publisher import publish_scrape_job

await publish_scrape_job({
    "job_id": str(job_id),
    "user_id": str(user_id),
    "industry": "SaaS",
    ...
})
```

### Consumer

**Code Location:** `workers/scraper_worker.py`

**Class:** `ScrapeWorker`

**Key Methods:**
- `connect()` - Connect to RabbitMQ
- `process_message(message)` - Handle incoming message
- `process_scrape_job(payload)` - Process the scrape job
- `run_scraper(payload)` - Execute scraping logic
- `start()` - Start listening for messages
- `stop()` - Gracefully shutdown

---

## Worker Process

### Worker Lifecycle

```
1. START
   ↓
2. Connect to RabbitMQ
   ↓
3. Declare queue (scrape_jobs)
   ↓
4. Start consuming messages
   ↓
5. WAIT for messages (blocking)
   ↓
6. MESSAGE ARRIVES
   ↓
7. Process message:
   - Update job status to "running"
   - Execute scraping logic
   - Save results to database
   - Update job status to "completed"
   ↓
8. Acknowledge message (remove from queue)
   ↓
9. Go back to step 5 (wait for next message)
```

### Starting the Worker

```bash
cd backend
.\start_worker.ps1
```

Or manually:
```bash
$env:PYTHONPATH="D:\Coding\Live\LeadEngine\backend"
.\venv\Scripts\python.exe workers\scraper_worker.py
```

### Worker Output

```
============================================================
SCRAPE JOB WORKER
============================================================
Event-Driven RabbitMQ Consumer
Point-to-Point Pattern
============================================================

🔌 Connecting to RabbitMQ...
✓ Connected to RabbitMQ successfully!

🎧 WORKER STARTED - LISTENING FOR MESSAGES
⏳ Waiting for messages... (Press Ctrl+C to stop)
============================================================

📨 NEW MESSAGE RECEIVED
Job ID: 987fcdeb-51a2-43d7-b123-456789abcdef
Industry: SaaS
Geography: Sydney, Australia
...

🏃 Starting job processing...
✓ Job status updated to: RUNNING

🔍 Running scraper...
✓ Scraper completed. Found 3 results

💾 Saving raw leads to database...
✓ Saved 3 new leads

✅ JOB COMPLETED SUCCESSFULLY
Duration: 2.15 seconds
============================================================
```

### Scaling Workers

Run multiple workers for parallel processing:

```bash
# Terminal 1
.\start_worker.ps1

# Terminal 2
.\start_worker.ps1

# Terminal 3
.\start_worker.ps1
```

Messages are automatically distributed across all workers (load balancing).

---

## Data Flow

### Complete Flow Diagram

```
1. USER creates job via Swagger
   ↓
2. API validates request
   ↓
3. API creates job in database
   INSERT INTO scrape_jobs (status='queued', ...)
   ↓
4. API publishes message to RabbitMQ
   PUBLISH to queue: scrape_jobs
   ↓
5. API returns response to user
   HTTP 201 Created
   ↓
6. Worker receives message (event-driven)
   CONSUME from queue: scrape_jobs
   ↓
7. Worker updates job status
   UPDATE scrape_jobs SET status='running', started_at=NOW()
   ↓
8. Worker executes scraping logic
   - Fetch data from sources
   - Parse and extract information
   - Apply filters and keywords
   ↓
9. Worker saves results
   INSERT INTO raw_leads (raw_payload, data_hash, ...)
   ↓
10. Worker updates job status
    UPDATE scrape_jobs SET status='completed', 
           total_found=X, total_processed=Y, completed_at=NOW()
    ↓
11. Worker acknowledges message
    ACK message (removes from queue)
    ↓
12. Worker continues listening
    WAIT for next message...
```

### Status Transitions

```
queued → running → completed
                 ↘ failed
```

**Transitions:**
- `queued → running`: Worker starts processing
- `running → completed`: Job finishes successfully
- `running → failed`: Error occurs during processing

---

## Code Examples

### Creating a Job (API)

```python
# app/api/v1/endpoints/scrape_jobs.py

@router.post("/scrape", response_model=ScrapeJobResponse, status_code=201)
async def create_scrape_job(
    job_request: ScrapeJobCreate,
    db: Session = Depends(get_db)
):
    # Generate job ID
    job_id = uuid4()
    
    # Create job in database
    scrape_job = ScrapeJob(
        id=job_id,
        user_id=job_request.user_id,
        status="queued",
        industry=job_request.industry,
        geography=job_request.geography,
        keywords=job_request.keywords,
        source_types=job_request.source_types,
        search_query=job_request.search_query,
        filters=job_request.filters,
        total_found=0,
        total_processed=0,
        created_at=datetime.utcnow()
    )
    
    db.add(scrape_job)
    db.commit()
    db.refresh(scrape_job)
    
    # Prepare message payload
    message_payload = {
        "job_id": str(job_id),
        "user_id": str(job_request.user_id),
        "industry": job_request.industry,
        "geography": job_request.geography,
        "keywords": job_request.keywords or [],
        "source_types": job_request.source_types or [],
        "search_query": job_request.search_query,
        "filters": job_request.filters or {}
    }
    
    # Publish to RabbitMQ
    await publish_scrape_job(message_payload)
    
    return ScrapeJobResponse(...)
```

### Publishing to RabbitMQ

```python
# app/mq/publisher.py

async def publish_scrape_job(job_data: Dict[str, Any]):
    """Publish a scrape job to the scrape_jobs queue"""
    publisher = await get_publisher()
    await publisher.publish_message("scrape_jobs", job_data)
```

### Processing a Job (Worker)

```python
# workers/scraper_worker.py

async def process_scrape_job(self, payload: dict):
    job_id = payload["job_id"]
    user_id = payload["user_id"]
    
    db = SessionLocal()
    
    try:
        # Get job from database
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        
        # Update status to RUNNING
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Run the scraper
        results = await self.run_scraper(payload)
        
        # Save raw leads
        for item in results:
            hash_value = hashlib.sha256(
                json.dumps(item, sort_keys=True).encode()
            ).hexdigest()
            
            raw = RawLead(
                scrape_job_id=job_id,
                user_id=user_id,
                raw_payload=item,
                data_hash=hash_value,
                source_url=item.get("source_url", "")
            )
            
            db.add(raw)
        
        # Update job status to COMPLETED
        job.total_found = len(results)
        job.total_processed = len(results)
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        job.status = "failed"
        job.completed_at = datetime.utcnow()
        db.commit()
        raise e
    finally:
        db.close()
```

---

## Summary

The Scrape Job System provides:
- ✅ **Asynchronous Processing**: Jobs processed in background
- ✅ **Event-Driven**: Real-time message processing
- ✅ **Scalable**: Add more workers for higher throughput
- ✅ **Reliable**: Persistent messages and durable queues
- ✅ **Traceable**: Complete status tracking and logging
- ✅ **Flexible**: Support for multiple sources and criteria

For more information, see:
- `WORKER_GUIDE.md` - Worker setup and usage
- `API_SCRAPE_JOBS.md` - API documentation
- `DATABASE_SCHEMA.md` - Database structure
