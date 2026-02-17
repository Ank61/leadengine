# RabbitMQ Consumer Worker - Point-to-Point Pattern

## 🎯 How It Works

### **It's a LISTENER, NOT a Scheduler!**

The worker uses an **event-driven, point-to-point pattern**:

```
✅ Event-Driven Listener (What we use)
   - Worker continuously listens to the queue
   - Processes messages IMMEDIATELY when they arrive
   - No polling, no cron jobs, no 10-minute intervals
   - Real-time processing

❌ Job Scheduler (What we DON'T use)
   - Runs every X minutes
   - Checks for new jobs
   - Slow, inefficient
   - Not real-time
```

---

## 📊 Message Flow

```
1. API receives request
   ↓
2. API creates job in DB (status: queued)
   ↓
3. API sends message to RabbitMQ queue
   ↓
4. Worker IMMEDIATELY receives message (listening 24/7)
   ↓
5. Worker updates job status to "running"
   ↓
6. Worker processes the scrape
   ↓
7. Worker saves results to raw_leads table
   ↓
8. Worker updates job status to "completed"
   ↓
9. Worker continues listening for next message
```

---

## 🚀 Starting the Worker

### **Option 1: Run Directly**
```bash
cd backend
.\venv\Scripts\python.exe workers/scraper_worker.py
```

### **Option 2: Run in Background (Windows)**
```powershell
# Start in new window
Start-Process powershell -ArgumentList "cd backend; .\venv\Scripts\python.exe workers/scraper_worker.py"
```

### **Option 3: Run as Service (Production)**
Use a process manager like:
- **Windows:** NSSM (Non-Sucking Service Manager)
- **Linux:** systemd, supervisor
- **Docker:** Run as container

---

## 🎧 What You'll See When Worker Starts

```
============================================================
SCRAPE JOB WORKER
============================================================
Event-Driven RabbitMQ Consumer
Point-to-Point Pattern
============================================================

🔌 Connecting to RabbitMQ...
   Host: localhost:5672
   VHost: /
✓ Connected to RabbitMQ successfully!

============================================================
🎧 WORKER STARTED - LISTENING FOR MESSAGES
============================================================
Queue: scrape_jobs
Prefetch: 1 message(s) at a time
Pattern: Point-to-Point (Event-Driven Listener)

💡 This worker will process messages IMMEDIATELY as they arrive.
   No polling or cron jobs needed!

⏳ Waiting for messages... (Press Ctrl+C to stop)
============================================================
```

---

## 📨 When a Message Arrives

```
============================================================
📨 NEW MESSAGE RECEIVED
============================================================
Job ID: 987fcdeb-51a2-43d7-b123-456789abcdef
User ID: 123e4567-e89b-12d3-a456-426614174000
Industry: SaaS
Geography: Sydney, Australia
Keywords: ['B2B', 'enterprise', 'cloud']
Source Types: ['google', 'linkedin']
Search Query: saas companies sydney
============================================================

🏃 Starting job processing...
✓ Job status updated to: RUNNING

🔍 Running scraper...
✓ Scraper completed. Found 3 results

💾 Saving raw leads to database...
✓ Saved 3 new leads

============================================================
✅ JOB COMPLETED SUCCESSFULLY
============================================================
Job ID: 987fcdeb-51a2-43d7-b123-456789abcdef
Status: completed
Total Found: 3
Total Processed: 3
Duration: 2.15 seconds
============================================================
```

---

## 🔄 Point-to-Point Pattern Explained

### **What is Point-to-Point?**

- **One Queue** → `scrape_jobs`
- **Multiple Producers** → API endpoints (can have many)
- **Multiple Consumers** → Workers (can scale horizontally)
- **One Message → One Consumer** → Each message processed by exactly ONE worker

### **Benefits:**

1. **Load Balancing** - Multiple workers share the load
2. **Fault Tolerance** - If one worker dies, others continue
3. **Scalability** - Add more workers to process faster
4. **Guaranteed Processing** - Each message processed exactly once

### **Example with Multiple Workers:**

```
API → [Message 1] → Queue → Worker 1 (processes)
API → [Message 2] → Queue → Worker 2 (processes)
API → [Message 3] → Queue → Worker 1 (processes)
API → [Message 4] → Queue → Worker 3 (processes)
```

---

## 🔧 Worker Features

### **1. Event-Driven Processing**
- Listens 24/7 to the queue
- Processes messages immediately
- No polling or delays

### **2. Deduplication**
- Checks for duplicate leads using hash
- Skips duplicates automatically
- Tracks duplicate count

### **3. Status Tracking**
- Updates job status in real-time
- Tracks: queued → running → completed/failed
- Records timestamps (started_at, completed_at)

### **4. Error Handling**
- Catches and logs errors
- Updates job status to "failed" on error
- Continues processing next messages

### **5. Graceful Shutdown**
- Press Ctrl+C to stop
- Closes RabbitMQ connection cleanly
- Finishes current message before stopping

### **6. Detailed Logging**
- Shows all job criteria
- Progress updates
- Success/failure summaries

---

## 🎯 Scaling Workers

### **Run Multiple Workers:**

```bash
# Terminal 1
.\venv\Scripts\python.exe workers/scraper_worker.py

# Terminal 2
.\venv\Scripts\python.exe workers/scraper_worker.py

# Terminal 3
.\venv\Scripts\python.exe workers/scraper_worker.py
```

**Result:** Messages distributed across all 3 workers automatically!

---

## 🛠️ Configuration

Edit these constants in `scraper_worker.py`:

```python
MAX_RETRIES = 3           # Max retry attempts
QUEUE_NAME = "scrape_jobs"  # Queue to listen to
PREFETCH_COUNT = 1        # Messages to process at once
```

**PREFETCH_COUNT:**
- `1` = Process one message at a time (safer)
- `5` = Process up to 5 messages concurrently (faster, more memory)

---

## 📝 Implementing Real Scraper Logic

Replace the `run_scraper()` method with your actual scraping logic:

```python
async def run_scraper(self, payload: dict):
    """Run actual scraper logic"""
    
    # Extract criteria
    industry = payload.get("industry")
    geography = payload.get("geography")
    keywords = payload.get("keywords", [])
    source_types = payload.get("source_types", [])
    search_query = payload.get("search_query")
    
    results = []
    
    # Scrape from each source type
    for source in source_types:
        if source == "google":
            results.extend(await scrape_google(search_query, industry, geography))
        elif source == "linkedin":
            results.extend(await scrape_linkedin(search_query, industry, geography))
        elif source == "crunchbase":
            results.extend(await scrape_crunchbase(search_query, industry, geography))
    
    # Filter by keywords
    if keywords:
        results = filter_by_keywords(results, keywords)
    
    return results
```

---

## ✅ Testing the Worker

### **1. Start the Worker**
```bash
.\venv\Scripts\python.exe workers/scraper_worker.py
```

### **2. Create a Job via API**
Go to http://localhost:8000/docs and create a scrape job

### **3. Watch the Worker Console**
You'll see the message arrive and get processed in real-time!

### **4. Check the Database**
```sql
-- Check job status
SELECT id, status, total_found, total_processed, created_at, completed_at 
FROM scrape_jobs 
ORDER BY created_at DESC 
LIMIT 5;

-- Check raw leads
SELECT id, scrape_job_id, raw_payload 
FROM raw_leads 
ORDER BY scraped_at DESC 
LIMIT 5;
```

---

## 🎊 Summary

✅ **Event-Driven** - Processes messages immediately
✅ **Point-to-Point** - One message → One worker
✅ **Scalable** - Run multiple workers
✅ **Real-Time** - No delays or polling
✅ **Fault Tolerant** - Handles errors gracefully
✅ **Production Ready** - Graceful shutdown, logging, deduplication

**No cron jobs or schedulers needed!** The worker listens 24/7 and processes messages as they arrive. 🚀
