# LeadEngine - Quick Start Guide

## 🚀 Starting the Application

### **Prerequisites:**
1. ✅ PostgreSQL running
2. ✅ RabbitMQ running
3. ✅ Virtual environment activated
4. ✅ Database tables created
5. ✅ Seed data loaded

---

## **Option 1: Using PowerShell Scripts (Recommended)**

### **Terminal 1 - Start API Server:**
```powershell
cd backend
.\start_api.ps1
```

### **Terminal 2 - Start Worker:**
```powershell
cd backend
.\start_worker.ps1
```

---

## **Option 2: Manual Commands**

### **Terminal 1 - Start API Server:**
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Terminal 2 - Start Worker:**
```powershell
cd backend
$env:PYTHONPATH="D:\Coding\Live\LeadEngine\backend"
.\venv\Scripts\python.exe workers\scraper_worker.py
```

---

## **🧪 Testing the Full Flow**

### **1. Start Both Services**
- Terminal 1: API Server running
- Terminal 2: Worker running and listening

### **2. Create a Scrape Job**
Go to: http://localhost:8000/docs

Use this payload:
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "industry": "SaaS",
  "geography": "Sydney, Australia",
  "keywords": ["B2B", "enterprise", "cloud"],
  "source_types": ["google", "linkedin"],
  "search_query": "saas companies sydney",
  "filters": {
    "company_size": "50-200"
  }
}
```

### **3. Watch the Worker Terminal**
You should see:
```
============================================================
📨 NEW MESSAGE RECEIVED
============================================================
Job ID: xxx
Industry: SaaS
Geography: Sydney, Australia
...
✅ JOB COMPLETED SUCCESSFULLY
============================================================
```

### **4. Check Job Status**
Use the `GET /api/v1/jobs/scrape/{job_id}` endpoint to check status

---

## **📊 What's Happening**

```
API Request (Swagger)
    ↓
Job created in DB (status: queued)
    ↓
Message sent to RabbitMQ
    ↓
Worker receives message IMMEDIATELY
    ↓
Worker updates status to "running"
    ↓
Worker processes scrape
    ↓
Worker saves results to raw_leads
    ↓
Worker updates status to "completed"
    ↓
Worker continues listening...
```

---

## **🔍 Monitoring**

### **Check RabbitMQ:**
- URL: http://localhost:15672
- Username: guest
- Password: guest
- Queue: `scrape_jobs`

### **Check Database:**
```sql
-- Check jobs
SELECT id, status, industry, geography, total_found, total_processed 
FROM scrape_jobs 
ORDER BY created_at DESC 
LIMIT 5;

-- Check raw leads
SELECT id, scrape_job_id, raw_payload->>'company_name' as company
FROM raw_leads 
ORDER BY scraped_at DESC 
LIMIT 5;
```

---

## **🛑 Stopping Services**

### **Stop API Server:**
Press `Ctrl+C` in Terminal 1

### **Stop Worker:**
Press `Ctrl+C` in Terminal 2

Both will shut down gracefully.

---

## **⚡ Quick Commands**

```powershell
# Seed database
.\venv\Scripts\python.exe seeds\seed_all.py

# Migrate database
.\venv\Scripts\python.exe migrate_scrape_jobs.py

# Verify table structure
.\venv\Scripts\python.exe verify_table.py

# Create tables
.\venv\Scripts\python.exe create_tables.py
```

---

## **🎯 URLs**

- **API:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **RabbitMQ Management:** http://localhost:15672

---

## **✅ Checklist**

Before testing, make sure:
- [ ] PostgreSQL is running
- [ ] RabbitMQ is running
- [ ] API server is running (Terminal 1)
- [ ] Worker is running (Terminal 2)
- [ ] Seed data is loaded
- [ ] Database tables exist

---

## **🐛 Troubleshooting**

### **Worker: "No module named 'app'"**
**Solution:** Use `start_worker.ps1` or set PYTHONPATH:
```powershell
$env:PYTHONPATH="D:\Coding\Live\LeadEngine\backend"
```

### **API: "Database connection failed"**
**Solution:** Check PostgreSQL is running and .env is configured

### **Worker: "Connection refused to RabbitMQ"**
**Solution:** Check RabbitMQ is running on port 5672

### **Messages not being consumed**
**Solution:** Make sure worker is running! Check Terminal 2

---

## **🎊 You're Ready!**

Start both services and test the full flow! 🚀
