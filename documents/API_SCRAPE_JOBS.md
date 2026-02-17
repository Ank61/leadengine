# Updated Scrape Job API - With Industry, Geography, Keywords & Source Types

## 🎯 Overview
The Scrape Job API now supports detailed scraping criteria including:
- **Industry** - Target industry (e.g., "SaaS", "Healthcare", "Finance")
- **Geography** - Target location (e.g., "Sydney", "Australia", "North America")
- **Keywords** - List of keywords to search for
- **Source Types** - Multiple sources to scrape (e.g., ["google", "linkedin"])

## 📊 Database Schema Updates

### scrape_jobs Table
New columns added:
- `industry` VARCHAR(255) - Target industry
- `geography` VARCHAR(255) - Target geography/location
- `keywords` JSONB - Array of keywords
- `source_types` JSONB - Array of source types (replaces single `source_type`)

**Note:** The old `source_type` column has been replaced with `source_types` (JSONB array)

---

## 🚀 API Endpoint

### Create Scrape Job
**Endpoint:** `POST /api/v1/jobs/scrape`

**New Request Body:**
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

**Field Descriptions:**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `user_id` | UUID | ✅ Yes | User creating the job | `"123e4567-e89b-12d3-a456-426614174000"` |
| `industry` | String | ❌ No | Target industry | `"SaaS"`, `"Healthcare"`, `"Finance"` |
| `geography` | String | ❌ No | Target location | `"Sydney"`, `"Australia"`, `"North America"` |
| `keywords` | Array[String] | ❌ No | Keywords to search | `["B2B", "enterprise", "cloud"]` |
| `source_types` | Array[String] | ❌ No | Sources to scrape | `["google", "linkedin", "crunchbase"]` |
| `search_query` | String | ✅ Yes | Main search query | `"saas companies sydney"` |
| `filters` | Object | ❌ No | Additional filters | `{"company_size": "50-200"}` |

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
  "filters": {
    "company_size": "50-200",
    "revenue": ">1M"
  },
  "total_found": 0,
  "total_processed": 0,
  "created_at": "2026-02-15T13:04:35.123456",
  "started_at": null,
  "completed_at": null
}
```

---

## 📝 Status Flow

### Job Status Lifecycle

```
1. QUEUED (Initial)
   ↓
   Job created in database
   Message sent to RabbitMQ
   ↓
2. RUNNING (Worker Processing)
   ↓
   Worker picks up message
   Updates status to "running"
   Sets started_at timestamp
   ↓
3. COMPLETED (Success)
   ↓
   Scraping finished
   Results saved to raw_leads
   Updates total_found & total_processed
   Sets completed_at timestamp
   
   OR
   
3. FAILED (Error)
   ↓
   Error occurred during scraping
   Status set to "failed"
```

### Status Values
- `queued` - Job created, waiting for worker
- `running` - Worker is actively processing
- `completed` - Successfully finished with results
- `failed` - Encountered an error

---

## 🧪 Testing Examples

### Example 1: SaaS Companies in Sydney
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

### Example 2: Healthcare Startups in USA
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "industry": "Healthcare",
  "geography": "United States",
  "keywords": ["telemedicine", "digital health", "AI"],
  "source_types": ["google", "crunchbase"],
  "search_query": "healthcare startups USA",
  "filters": {
    "funding_stage": "Series A",
    "founded_year": ">2020"
  }
}
```

### Example 3: Fintech in Europe
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "industry": "Fintech",
  "geography": "Europe",
  "keywords": ["payments", "blockchain", "neobank"],
  "source_types": ["google", "linkedin", "crunchbase"],
  "search_query": "fintech companies europe",
  "filters": {
    "company_size": "100-500",
    "has_api": true
  }
}
```

### Example 4: Minimal Request (Only Required Fields)
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "search_query": "tech companies"
}
```

---

## 🔄 Message Queue Payload

**Queue Name:** `scrape_jobs`

**Message Format:**
```json
{
  "job_id": "987fcdeb-51a2-43d7-b123-456789abcdef",
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

The worker receives this complete payload and can use all fields to customize the scraping logic.

---

## 🎯 Use Cases

### 1. **Industry-Specific Lead Generation**
Target specific industries for focused lead generation:
```json
{
  "industry": "SaaS",
  "keywords": ["B2B", "enterprise"],
  "search_query": "B2B SaaS companies"
}
```

### 2. **Geographic Targeting**
Find companies in specific regions:
```json
{
  "geography": "Sydney, Australia",
  "search_query": "companies in sydney"
}
```

### 3. **Multi-Source Scraping**
Scrape from multiple sources for comprehensive results:
```json
{
  "source_types": ["google", "linkedin", "crunchbase"],
  "search_query": "startup companies"
}
```

### 4. **Keyword-Based Filtering**
Use keywords to refine search results:
```json
{
  "keywords": ["AI", "machine learning", "automation"],
  "search_query": "AI companies"
}
```

---

## 🛠️ Implementation Notes

### For Frontend Developers
1. All fields except `user_id` and `search_query` are optional
2. `keywords` and `source_types` should be arrays (can be empty `[]`)
3. `filters` is a flexible object for any additional criteria
4. Status will always start as `queued`

### For Worker Developers
1. Access all criteria from the message payload
2. Use `source_types` array to determine which sources to scrape
3. Use `keywords` to refine search queries
4. Use `industry` and `geography` to filter results
5. Update status to `running` when starting
6. Update status to `completed` when done
7. Set `started_at` and `completed_at` timestamps

---

## 📚 Testing in Swagger

1. **Start the server** (already running):
   ```
   http://localhost:8000/docs
   ```

2. **Navigate to** `POST /api/v1/jobs/scrape`

3. **Click** "Try it out"

4. **Use this test payload:**
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

5. **Click** "Execute"

6. **Check the response** - You should see status `queued` with all your criteria

---

## ✅ Migration Summary

### What Changed:
- ✅ Added `industry` field (String)
- ✅ Added `geography` field (String)
- ✅ Added `keywords` field (JSONB array)
- ✅ Changed `source_type` → `source_types` (JSONB array)
- ✅ Updated schemas to support new fields
- ✅ Updated API endpoint to handle new fields
- ✅ Updated message queue payload
- ✅ Database tables updated

### Backward Compatibility:
- ⚠️ **Breaking Change:** `source_type` (single string) replaced with `source_types` (array)
- Old requests using `source_type` will fail validation
- Update all API calls to use the new format

---

## 🎊 Ready to Use!

Your API now supports comprehensive scraping criteria. Test it in Swagger and start creating detailed scrape jobs!

**Swagger URL:** http://localhost:8000/docs
