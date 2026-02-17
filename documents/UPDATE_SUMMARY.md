# ✅ Scrape Job API - Updated Successfully!

## 🎉 What Was Changed

### 1. **Database Model Updated** (`app/models/scrape_job.py`)
   - ✅ Added `industry` (VARCHAR 255)
   - ✅ Added `geography` (VARCHAR 255)
   - ✅ Added `keywords` (JSONB array)
   - ✅ Added `source_types` (JSONB array)
   - ❌ Removed `source_type` (single string)

### 2. **Schemas Updated** (`app/schemas/scrape_job.py`)
   - ✅ `ScrapeJobCreate` - Added all new fields
   - ✅ `ScrapeJobResponse` - Added all new fields
   - ✅ Updated examples in Swagger docs

### 3. **API Endpoint Updated** (`app/api/v1/endpoints/scrape_jobs.py`)
   - ✅ Handles new fields in request
   - ✅ Saves all fields to database
   - ✅ Sends complete payload to RabbitMQ
   - ✅ Returns all fields in response

### 4. **Database Tables Updated**
   - ✅ Ran `create_tables.py` - New columns added

---

## 🚀 New API Request Format

**Before:**
```json
{
  "user_id": "123e4567",
  "source_type": "google",
  "search_query": "saas companies sydney",
  "filters": {}
}
```

**After (NEW):**
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

---

## 📊 Job Status Flow (As Requested)

```
1. API Request → POST /api/v1/jobs/scrape
   ↓
   Status: QUEUED ✅
   - Job created in database
   - Message sent to RabbitMQ
   - Job waits for worker

2. Worker Picks Up Message
   ↓
   Status: RUNNING ✅
   - Worker updates status to "running"
   - Sets started_at timestamp
   - Begins scraping

3. Scraping Complete
   ↓
   Status: COMPLETED ✅
   - Results saved to raw_leads table
   - Updates total_found & total_processed
   - Sets completed_at timestamp
```

---

## 🧪 Test in Swagger NOW!

**URL:** http://localhost:8000/docs

**Test Payload:**
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

**Steps:**
1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/jobs/scrape`
3. Click "Try it out"
4. Paste the test payload above
5. Click "Execute"
6. ✅ You should see status: "queued" with all your data!

---

## 📝 What Each Field Does

| Field | Purpose | Example |
|-------|---------|---------|
| `industry` | Target industry for scraping | "SaaS", "Healthcare", "Finance" |
| `geography` | Target location/region | "Sydney", "Australia", "North America" |
| `keywords` | Keywords to refine search | ["B2B", "enterprise", "cloud"] |
| `source_types` | Which sources to scrape | ["google", "linkedin", "crunchbase"] |
| `search_query` | Main search query | "saas companies sydney" |
| `filters` | Any additional criteria | {"company_size": "50-200"} |

---

## ✅ Status Tracking (As You Requested)

### When Job is Created:
- ✅ Status: `queued`
- ✅ `created_at` timestamp set
- ✅ Job stored in database
- ✅ Message sent to RabbitMQ

### When Worker Starts:
- ✅ Status: `running`
- ✅ `started_at` timestamp set
- ✅ Worker processing the scrape

### When Worker Finishes:
- ✅ Status: `completed`
- ✅ `completed_at` timestamp set
- ✅ `total_found` updated with count
- ✅ `total_processed` updated with count
- ✅ Results saved to `raw_leads` table

---

## 🎯 Job Definition Storage

**Where is the job definition stored?**

1. **Database Table:** `scrape_jobs`
   - All job criteria stored in database
   - Includes: industry, geography, keywords, source_types, search_query, filters
   - Persisted permanently

2. **Message Queue:** RabbitMQ `scrape_jobs` queue
   - Complete job definition sent as message
   - Worker receives full criteria
   - Message consumed when worker processes it

3. **Access Job Definition:**
   ```sql
   SELECT * FROM scrape_jobs WHERE id = 'job_id';
   ```
   
   Or via API:
   ```
   GET /api/v1/jobs/scrape/{job_id}
   ```

---

## 🔥 Quick Test Commands

### Check if server is running:
```bash
curl http://localhost:8000/db-check
```

### Create a test job (using curl):
```bash
curl -X POST "http://localhost:8000/api/v1/jobs/scrape" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "industry": "SaaS",
    "geography": "Sydney, Australia",
    "keywords": ["B2B", "cloud"],
    "source_types": ["google"],
    "search_query": "saas companies sydney",
    "filters": {}
  }'
```

---

## 📚 Documentation Files

- `API_SCRAPE_JOBS.md` - Complete API documentation with examples
- `DATABASE_SCHEMA.md` - Database schema reference
- `SETUP_COMPLETE.md` - Initial setup guide

---

## ✨ All Requirements Met!

✅ **Industry** - Added as field
✅ **Geography** - Added as field  
✅ **Keywords** - Added as array field
✅ **Source Types** - Added as array field (replaces source_type)
✅ **Job Definition Storage** - Stored in database + message queue
✅ **Status Flow** - queued → running → completed ✅
✅ **Database Updated** - New columns added
✅ **API Updated** - Accepts all new fields
✅ **Swagger Ready** - Test at http://localhost:8000/docs

---

## 🎊 Ready to Test!

Your scrape job API is fully updated and ready to use with all the new fields!

**Next:** Go to http://localhost:8000/docs and test it! 🚀
