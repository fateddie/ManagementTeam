# 📊 Pain Point Radar - Database Schema

**Project:** Private Clinic Pain Point Monitoring System
**Version:** 1.0
**Author:** System Architect (Claude)
**Date:** 2025-01-03
**Status:** Design Phase - Awaiting Approval

---

## TABLE OF CONTENTS

1. [Schema Overview](#schema-overview)
2. [Complete DDL Scripts](#complete-ddl-scripts)
3. [Table Specifications](#table-specifications)
4. [Indexes & Performance](#indexes--performance)
5. [Sample Data](#sample-data)
6. [Migration Scripts](#migration-scripts)
7. [Query Cookbook](#query-cookbook)
8. [Backup & Maintenance](#backup--maintenance)

---

## 1. SCHEMA OVERVIEW

### 1.1 Entity-Relationship Diagram

```
┌─────────────────┐
│    clinics      │
│  (Master List)  │
└────────┬────────┘
         │
         │ 1:N
         │
┌────────▼────────┐         ┌──────────────┐
│   raw_items     │────────▶│   sources    │
│ (Reviews, Jobs) │   N:1   │ (Audit Trail)│
└────────┬────────┘         └──────────────┘
         │
         │ 1:N
         │
┌────────▼────────────┐
│ derived_metadata    │
│  (Pain Points,      │
│   Aggregations)     │
└─────────────────────┘
```

### 1.2 Design Principles

1. **Normalization:** Separate concerns (clinics vs. data sources vs. raw items)
2. **Flexibility:** JSONB for heterogeneous data (reviews vs job ads)
3. **Auditability:** Every record traceable to source + timestamp
4. **Performance:** Indexes on common query patterns (clinic_id, scraped_at, item_type)
5. **Scalability:** Partitioning strategy for raw_items (by date)

### 1.3 Table Summary

| Table | Purpose | Estimated Rows (1 year) |
|-------|---------|------------------------|
| `clinics` | Master clinic list | 1,000 |
| `sources` | Scraping audit trail | 50,000 |
| `raw_items` | Reviews, job ads, website data | 500,000 |
| `derived_metadata` | Analyzed insights | 10,000 |

**Total Database Size (1 year):** ~2-5 GB

---

## 2. COMPLETE DDL SCRIPTS

### 2.1 Core Tables

```sql
-- ============================================================
-- TABLE: clinics
-- PURPOSE: Master list of all clinics being monitored
-- ============================================================

CREATE TABLE IF NOT EXISTS clinics (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Core Identifiers
    name VARCHAR(255) NOT NULL,
    clinic_type VARCHAR(50) NOT NULL
        CHECK (clinic_type IN ('physiotherapy', 'counselling', 'chiropody', 'multi_practitioner')),

    -- Location
    country VARCHAR(50) NOT NULL
        CHECK (country IN ('UK', 'Ireland')),
    region VARCHAR(100),  -- e.g., "London", "Dublin", "Manchester"
    address TEXT,
    postcode VARCHAR(20),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Contact Information
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(500),
    google_maps_url VARCHAR(500),

    -- Status Tracking
    status VARCHAR(20) DEFAULT 'active'
        CHECK (status IN ('active', 'closed', 'merged', 'monitoring_paused')),

    -- Timestamps
    first_discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Flexible Storage
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Prevent Duplicates
    CONSTRAINT unique_clinic_name_postcode UNIQUE(name, postcode)
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_clinics_type ON clinics(clinic_type);
CREATE INDEX IF NOT EXISTS idx_clinics_country ON clinics(country);
CREATE INDEX IF NOT EXISTS idx_clinics_region ON clinics(region);
CREATE INDEX IF NOT EXISTS idx_clinics_status ON clinics(status);
CREATE INDEX IF NOT EXISTS idx_clinics_metadata ON clinics USING gin(metadata);

-- Trigger: Auto-update last_updated_at
CREATE OR REPLACE FUNCTION update_last_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER clinics_update_timestamp
    BEFORE UPDATE ON clinics
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated_at();

-- Comments for Documentation
COMMENT ON TABLE clinics IS 'Master list of all private clinics being monitored for pain points';
COMMENT ON COLUMN clinics.metadata IS 'JSONB field for flexible data: team_size, services, booking_system, etc.';


-- ============================================================
-- TABLE: sources
-- PURPOSE: Audit trail for all scraping operations
-- ============================================================

CREATE TABLE IF NOT EXISTS sources (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Source Metadata
    source_type VARCHAR(50) NOT NULL
        CHECK (source_type IN ('google_review', 'job_ad', 'website_content', 'directory_listing', 'manual_entry')),
    source_name VARCHAR(100) NOT NULL,  -- e.g., "Indeed", "Google Reviews"
    source_url TEXT,

    -- Scraping Details
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scraper_version VARCHAR(20),  -- e.g., "v1.2.3"
    scrape_success BOOLEAN DEFAULT TRUE,
    error_message TEXT,

    -- Flexible Storage
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type);
CREATE INDEX IF NOT EXISTS idx_sources_scraped_at ON sources(scraped_at);
CREATE INDEX IF NOT EXISTS idx_sources_success ON sources(scrape_success);

-- Comments
COMMENT ON TABLE sources IS 'Audit trail for every scraping operation (transparency requirement)';
COMMENT ON COLUMN sources.metadata IS 'Scraping stats: reviews_collected, rate_limit_hit, proxy_used, etc.';


-- ============================================================
-- TABLE: raw_items
-- PURPOSE: Store all scraped data (reviews, jobs, website content)
-- ============================================================

CREATE TABLE IF NOT EXISTS raw_items (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Foreign Keys
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,

    -- Item Classification
    item_type VARCHAR(50) NOT NULL
        CHECK (item_type IN ('review', 'job_ad', 'website_snapshot', 'directory_entry')),

    -- Content (Flexible Structure)
    content JSONB NOT NULL,  -- Varies by item_type (see examples below)
    text_excerpt TEXT,       -- For full-text search
    content_hash VARCHAR(64),  -- SHA256 for deduplication

    -- Analyzed Fields
    sentiment_score DECIMAL(3, 2)
        CHECK (sentiment_score BETWEEN -1.0 AND 1.0),
    urgency_detected VARCHAR(20)
        CHECK (urgency_detected IN ('critical', 'high', 'medium', 'low')),
    keywords TEXT[],  -- Array of detected keywords

    -- Deduplication
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of INTEGER REFERENCES raw_items(id),

    -- Timestamps
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,  -- When analysis was run

    -- Flexible Storage
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Prevent Exact Duplicates (will be handled by hash)
    CONSTRAINT unique_content_hash UNIQUE(content_hash)
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_raw_items_clinic ON raw_items(clinic_id);
CREATE INDEX IF NOT EXISTS idx_raw_items_type ON raw_items(item_type);
CREATE INDEX IF NOT EXISTS idx_raw_items_scraped_at ON raw_items(scraped_at);
CREATE INDEX IF NOT EXISTS idx_raw_items_urgency ON raw_items(urgency_detected);
CREATE INDEX IF NOT EXISTS idx_raw_items_keywords ON raw_items USING gin(keywords);
CREATE INDEX IF NOT EXISTS idx_raw_items_content ON raw_items USING gin(content);

-- Full-Text Search Index
CREATE INDEX IF NOT EXISTS idx_raw_items_text_search
    ON raw_items USING gin(to_tsvector('english', COALESCE(text_excerpt, '')));

-- Comments
COMMENT ON TABLE raw_items IS 'All scraped data: reviews, job ads, website snapshots';
COMMENT ON COLUMN raw_items.content IS 'JSONB structure varies by item_type (see schema examples)';
COMMENT ON COLUMN raw_items.content_hash IS 'SHA256 hash for exact duplicate detection';


-- ============================================================
-- TABLE: derived_metadata
-- PURPOSE: Store analyzed insights and aggregations
-- ============================================================

CREATE TABLE IF NOT EXISTS derived_metadata (
    -- Primary Key
    id SERIAL PRIMARY KEY,

    -- Foreign Key
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,

    -- Metric Details
    metric_type VARCHAR(100) NOT NULL,  -- e.g., "avg_rating", "top_pain_points", "hiring_frequency"
    metric_value JSONB NOT NULL,
    confidence_level VARCHAR(20)
        CHECK (confidence_level IN ('high', 'medium', 'low', 'insufficient')),

    -- Evidence Trail
    based_on_item_ids INTEGER[],  -- References to raw_items.id

    -- Calculation Details
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculation_version VARCHAR(20),  -- e.g., "v1.0"

    -- Flexible Storage
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_derived_clinic ON derived_metadata(clinic_id);
CREATE INDEX IF NOT EXISTS idx_derived_type ON derived_metadata(metric_type);
CREATE INDEX IF NOT EXISTS idx_derived_calculated_at ON derived_metadata(calculated_at);
CREATE INDEX IF NOT EXISTS idx_derived_confidence ON derived_metadata(confidence_level);

-- Comments
COMMENT ON TABLE derived_metadata IS 'Analyzed insights: pain points, ratings, hiring patterns';
COMMENT ON COLUMN derived_metadata.based_on_item_ids IS 'Array of raw_items.id used to calculate this metric (auditability)';
```

### 2.2 Phase 2 Tables (Future)

```sql
-- ============================================================
-- TABLE: active_research
-- PURPOSE: Store active research data (LinkedIn, surveys, interviews)
-- ============================================================

CREATE TABLE IF NOT EXISTS active_research (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,

    research_type VARCHAR(50) NOT NULL
        CHECK (research_type IN ('linkedin_post', 'survey_response', 'interview', 'email_outreach')),

    content JSONB NOT NULL,
    response_received BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,

    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_active_research_clinic ON active_research(clinic_id);
CREATE INDEX IF NOT EXISTS idx_active_research_type ON active_research(research_type);

COMMENT ON TABLE active_research IS 'Active research campaigns (Phase 3)';


-- ============================================================
-- TABLE: competitors
-- PURPOSE: Competitive intelligence (mentioned in reviews/jobs)
-- ============================================================

CREATE TABLE IF NOT EXISTS competitors (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,

    competitor_name VARCHAR(255) NOT NULL,
    competitor_type VARCHAR(100),  -- e.g., "AI receptionist", "booking software", "competing clinic"

    evidence_source INTEGER REFERENCES raw_items(id),

    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_competitors_clinic ON competitors(clinic_id);
CREATE INDEX IF NOT EXISTS idx_competitors_type ON competitors(competitor_type);

COMMENT ON TABLE competitors IS 'Competitors mentioned in reviews or job ads';
```

---

## 3. TABLE SPECIFICATIONS

### 3.1 `clinics` Table

**Purpose:** Master directory of all clinics being monitored

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| `name` | VARCHAR(255) | NOT NULL | Clinic name |
| `clinic_type` | VARCHAR(50) | NOT NULL, CHECK | Type: physiotherapy, counselling, chiropody, multi_practitioner |
| `country` | VARCHAR(50) | NOT NULL, CHECK | UK or Ireland |
| `region` | VARCHAR(100) | NULL | City/region (e.g., "London", "Dublin") |
| `address` | TEXT | NULL | Full street address |
| `postcode` | VARCHAR(20) | NULL | UK/Ireland postcode |
| `latitude` | DECIMAL(10,8) | NULL | GPS coordinate |
| `longitude` | DECIMAL(11,8) | NULL | GPS coordinate |
| `phone` | VARCHAR(50) | NULL | Contact phone |
| `email` | VARCHAR(255) | NULL | Contact email |
| `website` | VARCHAR(500) | NULL | Clinic website URL |
| `google_maps_url` | VARCHAR(500) | NULL | Google Maps URL for reviews |
| `status` | VARCHAR(20) | DEFAULT 'active', CHECK | active, closed, merged, monitoring_paused |
| `first_discovered_at` | TIMESTAMP | DEFAULT NOW() | When clinic was first added |
| `last_updated_at` | TIMESTAMP | DEFAULT NOW() | Last update timestamp (auto-updated) |
| `metadata` | JSONB | DEFAULT '{}' | Flexible storage for additional fields |

**metadata JSONB Structure:**

```json
{
  "team_size": 5,
  "services": ["sports physio", "massage", "acupuncture"],
  "booking_system": "Cliniko",
  "discovered_via": "Physio First directory",
  "notes": "High-volume clinic, multiple locations"
}
```

**Common Queries:**

```sql
-- Find all active physiotherapy clinics in London
SELECT * FROM clinics
WHERE clinic_type = 'physiotherapy'
  AND country = 'UK'
  AND region = 'London'
  AND status = 'active';

-- Find clinics using Cliniko booking system
SELECT * FROM clinics
WHERE metadata->>'booking_system' = 'Cliniko';
```

---

### 3.2 `sources` Table

**Purpose:** Audit trail for every scraping operation

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| `source_type` | VARCHAR(50) | NOT NULL, CHECK | google_review, job_ad, website_content, directory_listing, manual_entry |
| `source_name` | VARCHAR(100) | NOT NULL | Platform name (e.g., "Indeed", "Google Reviews") |
| `source_url` | TEXT | NULL | URL scraped from |
| `scraped_at` | TIMESTAMP | DEFAULT NOW() | When scrape occurred |
| `scraper_version` | VARCHAR(20) | NULL | Scraper version for reproducibility (e.g., "v1.2.3") |
| `scrape_success` | BOOLEAN | DEFAULT TRUE | Whether scrape succeeded |
| `error_message` | TEXT | NULL | Error details if failed |
| `metadata` | JSONB | DEFAULT '{}' | Scraping stats |

**metadata JSONB Structure:**

```json
{
  "reviews_collected": 15,
  "rate_limit_hit": false,
  "proxy_used": "144.56.78.90",
  "user_agent": "Mozilla/5.0...",
  "scrape_duration_sec": 12.5
}
```

**Common Queries:**

```sql
-- Find all failed scrapes in last 7 days
SELECT * FROM sources
WHERE scrape_success = FALSE
  AND scraped_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY scraped_at DESC;

-- Success rate by source type
SELECT
    source_type,
    COUNT(*) AS total_scrapes,
    SUM(CASE WHEN scrape_success THEN 1 ELSE 0 END) AS successful,
    ROUND(100.0 * SUM(CASE WHEN scrape_success THEN 1 ELSE 0 END) / COUNT(*), 2) AS success_rate
FROM sources
WHERE scraped_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY source_type;
```

---

### 3.3 `raw_items` Table

**Purpose:** Store all scraped content (reviews, job ads, website data)

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| `clinic_id` | INTEGER | FK → clinics(id), ON DELETE CASCADE | Clinic this item belongs to |
| `source_id` | INTEGER | FK → sources(id), ON DELETE CASCADE | Scraping source (audit trail) |
| `item_type` | VARCHAR(50) | NOT NULL, CHECK | review, job_ad, website_snapshot, directory_entry |
| `content` | JSONB | NOT NULL | Flexible structure (varies by item_type) |
| `text_excerpt` | TEXT | NULL | Plaintext for full-text search |
| `content_hash` | VARCHAR(64) | UNIQUE | SHA256 hash for deduplication |
| `sentiment_score` | DECIMAL(3,2) | CHECK (-1.0 to 1.0) | Sentiment analysis result |
| `urgency_detected` | VARCHAR(20) | CHECK | critical, high, medium, low |
| `keywords` | TEXT[] | NULL | Array of detected keywords |
| `is_duplicate` | BOOLEAN | DEFAULT FALSE | Marked as duplicate? |
| `duplicate_of` | INTEGER | FK → raw_items(id) | Original item if duplicate |
| `scraped_at` | TIMESTAMP | DEFAULT NOW() | When item was scraped |
| `processed_at` | TIMESTAMP | NULL | When analysis was run |
| `metadata` | JSONB | DEFAULT '{}' | Additional context |

**content JSONB Structure by item_type:**

**Google Review:**
```json
{
  "rating": 2,
  "text": "Phone system is terrible. Always goes to voicemail.",
  "reviewer_name": "Sarah M.",
  "review_date": "2024-12-15",
  "clinic_response": null,
  "upvotes": 12,
  "verified_patient": true
}
```

**Job Ad:**
```json
{
  "job_title": "Receptionist - Physiotherapy Clinic",
  "description": "Busy clinic seeks receptionist to manage phones, bookings...",
  "posted_date": "2025-01-01",
  "salary": "£22,000 - £25,000",
  "job_board": "Indeed",
  "job_url": "https://indeed.co.uk/...",
  "location": "London",
  "applications_count": 45
}
```

**Website Snapshot:**
```json
{
  "services_offered": ["sports physio", "massage", "acupuncture"],
  "pricing_visible": false,
  "team_size": 5,
  "booking_system_detected": "Cliniko",
  "contact_methods": ["phone", "email", "contact_form"],
  "mobile_friendly": true
}
```

**Common Queries:**

```sql
-- Find critical reviews mentioning "phone" for a clinic
SELECT
    text_excerpt,
    content->>'rating' AS rating,
    content->>'review_date' AS review_date,
    urgency_detected
FROM raw_items
WHERE clinic_id = 1
  AND item_type = 'review'
  AND urgency_detected = 'critical'
  AND 'phone' = ANY(keywords)
ORDER BY scraped_at DESC;

-- Full-text search for "booking system"
SELECT
    c.name AS clinic_name,
    r.text_excerpt,
    r.item_type
FROM raw_items r
JOIN clinics c ON r.clinic_id = c.id
WHERE to_tsvector('english', r.text_excerpt) @@ to_tsquery('english', 'booking & system')
LIMIT 20;
```

---

### 3.4 `derived_metadata` Table

**Purpose:** Store analyzed insights and aggregations

**Columns:**

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | SERIAL | PRIMARY KEY | Auto-incrementing ID |
| `clinic_id` | INTEGER | FK → clinics(id), ON DELETE CASCADE | Clinic this metric belongs to |
| `metric_type` | VARCHAR(100) | NOT NULL | Type of metric (e.g., "top_pain_points", "avg_rating") |
| `metric_value` | JSONB | NOT NULL | The calculated metric |
| `confidence_level` | VARCHAR(20) | CHECK | high, medium, low, insufficient |
| `based_on_item_ids` | INTEGER[] | NULL | Array of raw_items.id used for calculation |
| `calculated_at` | TIMESTAMP | DEFAULT NOW() | When metric was calculated |
| `calculation_version` | VARCHAR(20) | NULL | Algorithm version (e.g., "v1.0") |
| `metadata` | JSONB | DEFAULT '{}' | Additional context |

**metric_value JSONB Examples:**

**Top Pain Points:**
```json
{
  "pain_points": [
    {
      "pain_point": "Phone system / missed calls",
      "mentions": 8,
      "severity": "critical",
      "evidence_count": 8,
      "example_quotes": [
        "Phone system is terrible. Always goes to voicemail.",
        "Can never get through on the phone."
      ]
    },
    {
      "pain_point": "Booking complexity",
      "mentions": 5,
      "severity": "high",
      "evidence_count": 5,
      "example_quotes": [
        "Online booking is confusing."
      ]
    }
  ]
}
```

**Average Rating:**
```json
{
  "avg_rating": 3.2,
  "total_reviews": 35,
  "rating_distribution": {
    "5": 5,
    "4": 8,
    "3": 7,
    "2": 10,
    "1": 5
  }
}
```

**Hiring Frequency:**
```json
{
  "job_ads_last_30_days": 3,
  "job_ads_last_90_days": 7,
  "avg_days_between_ads": 12.5,
  "most_common_role": "receptionist",
  "interpretation": "High turnover (7 ads in 90 days)"
}
```

**Common Queries:**

```sql
-- Get latest pain points for all clinics
SELECT
    c.name AS clinic_name,
    c.clinic_type,
    d.metric_value->'pain_points'->0->>'pain_point' AS top_pain_point,
    d.confidence_level,
    d.calculated_at
FROM derived_metadata d
JOIN clinics c ON d.clinic_id = c.id
WHERE d.metric_type = 'top_pain_points'
  AND d.calculated_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY d.calculated_at DESC;
```

---

## 4. INDEXES & PERFORMANCE

### 4.1 Index Strategy

**Primary Indexes:**
- Primary keys (auto-indexed)
- Foreign keys
- Status/type filters (clinic_type, source_type, item_type)
- Temporal queries (scraped_at, calculated_at)

**GIN Indexes (for JSONB and Arrays):**
- `metadata` columns (all tables)
- `keywords` array
- `content` JSONB
- Full-text search on `text_excerpt`

**Performance Targets:**
- Clinic lookup by ID: <1ms
- Reviews for clinic (100 items): <10ms
- Full-text search (1000 items): <50ms
- Pain point aggregation (1 clinic): <100ms

### 4.2 Partitioning Strategy (Future)

**When to Partition:**
When `raw_items` exceeds 1M rows (expected after ~2 years)

**Partition by:** `scraped_at` (monthly partitions)

```sql
-- Convert raw_items to partitioned table
CREATE TABLE raw_items_partitioned (LIKE raw_items INCLUDING ALL)
PARTITION BY RANGE (scraped_at);

-- Create monthly partitions
CREATE TABLE raw_items_2025_01 PARTITION OF raw_items_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE raw_items_2025_02 PARTITION OF raw_items_partitioned
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- ... etc.
```

**Benefits:**
- Faster queries on recent data
- Easier archival (drop old partitions)
- Better index performance

---

## 5. SAMPLE DATA

### 5.1 Sample Clinics

```sql
INSERT INTO clinics (name, clinic_type, country, region, address, postcode, phone, email, website, google_maps_url, metadata) VALUES
('Central London Physiotherapy Clinic', 'physiotherapy', 'UK', 'London', '123 High Street, London', 'SW1A 1AA', '+44 20 1234 5678', 'info@clphysio.co.uk', 'https://clphysio.co.uk', 'https://maps.google.com/clphysio', '{"team_size": 5, "services": ["sports physio", "massage"], "booking_system": "Cliniko"}'::jsonb),
('Dublin Mind Therapy', 'counselling', 'Ireland', 'Dublin', '45 O''Connell Street, Dublin', 'D01 F5P2', '+353 1 234 5678', 'hello@dublinmind.ie', 'https://dublinmind.ie', 'https://maps.google.com/dublinmind', '{"team_size": 3, "services": ["CBT", "EMDR"], "booking_system": "SimplePractice"}'::jsonb),
('Manchester Foot Clinic', 'chiropody', 'UK', 'Manchester', '78 Market Street, Manchester', 'M1 1PT', '+44 161 234 5678', 'contact@manchesterfoot.com', 'https://manchesterfoot.com', NULL, '{"team_size": 2, "services": ["diabetic foot care", "nail surgery"]}'::jsonb);
```

### 5.2 Sample Sources

```sql
INSERT INTO sources (source_type, source_name, source_url, scraper_version, scrape_success, metadata) VALUES
('google_review', 'Google Maps Reviews', 'https://maps.google.com/clphysio', 'v1.0.0', TRUE, '{"reviews_collected": 15, "rate_limit_hit": false}'::jsonb),
('job_ad', 'Indeed UK', 'https://indeed.co.uk/jobs?q=receptionist+physiotherapy&l=London', 'v1.0.0', TRUE, '{"jobs_collected": 8, "scrape_duration_sec": 5.2}'::jsonb),
('directory_listing', 'Physio First Directory', 'https://www.physio-first.org.uk/find-a-physio', 'v1.0.0', TRUE, '{"clinics_discovered": 120}'::jsonb);
```

### 5.3 Sample Raw Items

**Google Review:**
```sql
INSERT INTO raw_items (clinic_id, source_id, item_type, content, text_excerpt, content_hash, sentiment_score, urgency_detected, keywords, scraped_at, metadata) VALUES
(1, 1, 'review',
 '{"rating": 2, "text": "Phone system is terrible. Always goes to voicemail. Lost 3 appointments because I couldn''t get through.", "reviewer_name": "Sarah M.", "review_date": "2024-12-15", "clinic_response": null, "upvotes": 12, "verified_patient": true}'::jsonb,
 'Phone system is terrible. Always goes to voicemail. Lost 3 appointments because I couldn''t get through.',
 'abc123def456...', -0.75, 'critical',
 ARRAY['phone', 'voicemail', 'appointments', 'communication'],
 '2025-01-03 10:15:00',
 '{"source": "google_maps"}'::jsonb
);
```

**Job Ad:**
```sql
INSERT INTO raw_items (clinic_id, source_id, item_type, content, text_excerpt, content_hash, urgency_detected, keywords, scraped_at, metadata) VALUES
(1, 2, 'job_ad',
 '{"job_title": "Receptionist - Physiotherapy Clinic", "description": "Busy clinic seeks receptionist to manage phones, bookings, and patient queries. Must be comfortable with high call volume.", "posted_date": "2025-01-01", "salary": "£22,000 - £25,000", "job_board": "Indeed", "job_url": "https://indeed.co.uk/job123"}'::jsonb,
 'Busy clinic seeks receptionist to manage phones, bookings, and patient queries. Must be comfortable with high call volume.',
 'def789ghi012...', 'high',
 ARRAY['receptionist', 'phones', 'bookings', 'high_call_volume'],
 '2025-01-03 11:00:00',
 '{"applications_count": 45}'::jsonb
);
```

### 5.4 Sample Derived Metadata

```sql
INSERT INTO derived_metadata (clinic_id, metric_type, metric_value, confidence_level, based_on_item_ids, calculation_version, metadata) VALUES
(1, 'top_pain_points',
 '{"pain_points": [{"pain_point": "Phone system / missed calls", "mentions": 8, "severity": "critical", "evidence_count": 8, "example_quotes": ["Phone system is terrible. Always goes to voicemail.", "Can never get through on the phone."]}]}'::jsonb,
 'high',
 ARRAY[1, 5, 7, 12, 15, 20, 25, 30],
 'v1.0',
 '{"total_reviews_analyzed": 35, "date_range": "2024-01-01 to 2025-01-03"}'::jsonb
);
```

---

## 6. MIGRATION SCRIPTS

### 6.1 Initial Setup

```bash
#!/bin/bash
# setup_database.sh

# Create database
psql -U postgres -c "CREATE DATABASE pain_point_radar;"

# Run DDL scripts
psql -U postgres -d pain_point_radar -f ddl/01_create_tables.sql
psql -U postgres -d pain_point_radar -f ddl/02_create_indexes.sql
psql -U postgres -d pain_point_radar -f ddl/03_create_triggers.sql

# Insert sample data (optional)
psql -U postgres -d pain_point_radar -f sample_data/clinics.sql
```

### 6.2 Version Migrations

**Migration 1: Add content_hash column (v1.0 → v1.1)**

```sql
-- migrations/001_add_content_hash.sql

BEGIN;

-- Add column
ALTER TABLE raw_items ADD COLUMN IF NOT EXISTS content_hash VARCHAR(64);

-- Backfill existing data
UPDATE raw_items
SET content_hash = md5(content::text)
WHERE content_hash IS NULL;

-- Add unique constraint
ALTER TABLE raw_items ADD CONSTRAINT unique_content_hash UNIQUE(content_hash);

-- Update version
INSERT INTO schema_versions (version, applied_at, description) VALUES
('v1.1', CURRENT_TIMESTAMP, 'Added content_hash for deduplication');

COMMIT;
```

**Migration 2: Add active_research table (v1.1 → v2.0)**

```sql
-- migrations/002_add_active_research.sql

BEGIN;

CREATE TABLE IF NOT EXISTS active_research (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,
    research_type VARCHAR(50) NOT NULL CHECK (research_type IN ('linkedin_post', 'survey_response', 'interview', 'email_outreach')),
    content JSONB NOT NULL,
    response_received BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_active_research_clinic ON active_research(clinic_id);

INSERT INTO schema_versions (version, applied_at, description) VALUES
('v2.0', CURRENT_TIMESTAMP, 'Added active_research table for Phase 3');

COMMIT;
```

### 6.3 Schema Version Tracking

```sql
-- Create version tracking table
CREATE TABLE IF NOT EXISTS schema_versions (
    id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Record initial version
INSERT INTO schema_versions (version, description) VALUES
('v1.0', 'Initial schema with clinics, sources, raw_items, derived_metadata');
```

---

## 7. QUERY COOKBOOK

### 7.1 Common Queries

**Query 1: Top Pain Points Across All Clinics**

```sql
SELECT
    unnest(keywords) AS keyword,
    COUNT(*) AS mentions,
    AVG(sentiment_score) AS avg_sentiment,
    STRING_AGG(DISTINCT text_excerpt, ' | ' ORDER BY text_excerpt) AS examples
FROM raw_items
WHERE item_type = 'review'
  AND urgency_detected IN ('critical', 'high')
  AND scraped_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY keyword
HAVING COUNT(*) >= 3
ORDER BY mentions DESC
LIMIT 10;
```

**Query 2: Clinics with Highest Hiring Frequency**

```sql
SELECT
    c.name,
    c.clinic_type,
    COUNT(r.id) AS job_ads_count,
    MAX(r.scraped_at) AS most_recent_ad,
    ROUND(AVG(EXTRACT(EPOCH FROM (CURRENT_DATE - (r.content->>'posted_date')::DATE)) / 86400)) AS avg_days_old
FROM clinics c
JOIN raw_items r ON c.id = r.clinic_id
WHERE r.item_type = 'job_ad'
  AND r.scraped_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY c.id, c.name, c.clinic_type
HAVING COUNT(r.id) >= 2
ORDER BY job_ads_count DESC;
```

**Query 3: Average Rating by Region**

```sql
SELECT
    c.region,
    c.clinic_type,
    COUNT(DISTINCT c.id) AS clinics_count,
    ROUND(AVG((r.content->>'rating')::DECIMAL), 2) AS avg_rating,
    COUNT(r.id) AS total_reviews
FROM clinics c
JOIN raw_items r ON c.id = r.clinic_id
WHERE r.item_type = 'review'
  AND r.content->>'rating' IS NOT NULL
GROUP BY c.region, c.clinic_type
HAVING COUNT(r.id) >= 10
ORDER BY avg_rating ASC;
```

**Query 4: Recent Negative Reviews**

```sql
SELECT
    c.name AS clinic_name,
    r.text_excerpt,
    r.content->>'rating' AS rating,
    r.content->>'review_date' AS review_date,
    r.sentiment_score,
    r.urgency_detected
FROM raw_items r
JOIN clinics c ON r.clinic_id = c.id
WHERE r.item_type = 'review'
  AND (r.content->>'rating')::INTEGER <= 2
  AND r.scraped_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY r.scraped_at DESC
LIMIT 20;
```

**Query 5: Technology Stack Distribution**

```sql
SELECT
    c.metadata->>'booking_system' AS booking_system,
    COUNT(*) AS clinics_using,
    ARRAY_AGG(c.name) AS clinic_names
FROM clinics c
WHERE c.metadata->>'booking_system' IS NOT NULL
GROUP BY booking_system
ORDER BY clinics_using DESC;
```

### 7.2 Analytics Queries

**Query 6: Pain Point Trends Over Time**

```sql
SELECT
    DATE_TRUNC('month', r.scraped_at) AS month,
    unnest(r.keywords) AS keyword,
    COUNT(*) AS mentions
FROM raw_items r
WHERE r.item_type = 'review'
  AND r.urgency_detected IN ('critical', 'high')
  AND r.scraped_at >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY month, keyword
HAVING COUNT(*) >= 5
ORDER BY month DESC, mentions DESC;
```

**Query 7: Sentiment Analysis by Clinic Type**

```sql
SELECT
    c.clinic_type,
    ROUND(AVG(r.sentiment_score), 3) AS avg_sentiment,
    COUNT(*) AS review_count,
    SUM(CASE WHEN r.sentiment_score >= 0.5 THEN 1 ELSE 0 END) AS positive_reviews,
    SUM(CASE WHEN r.sentiment_score <= -0.5 THEN 1 ELSE 0 END) AS negative_reviews
FROM raw_items r
JOIN clinics c ON r.clinic_id = c.id
WHERE r.item_type = 'review'
  AND r.sentiment_score IS NOT NULL
GROUP BY c.clinic_type
ORDER BY avg_sentiment ASC;
```

---

## 8. BACKUP & MAINTENANCE

### 8.1 Backup Strategy

**Daily Backups:**
```bash
#!/bin/bash
# backup_daily.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/pain_point_radar"

# Full database dump
pg_dump -U postgres pain_point_radar | gzip > "$BACKUP_DIR/full_backup_$DATE.sql.gz"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR/full_backup_$DATE.sql.gz" s3://my-backups/pain_point_radar/

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "full_backup_*.sql.gz" -mtime +30 -delete
```

**Schedule with cron:**
```bash
# Run daily at 3 AM
0 3 * * * /scripts/backup_daily.sh
```

### 8.2 Maintenance Tasks

**Weekly Vacuum:**
```sql
-- Reclaim storage and update statistics
VACUUM ANALYZE raw_items;
VACUUM ANALYZE clinics;
VACUUM ANALYZE derived_metadata;
```

**Monthly Cleanup:**
```sql
-- Delete old raw_items (older than 12 months)
DELETE FROM raw_items
WHERE scraped_at < CURRENT_DATE - INTERVAL '12 months';

-- Delete failed scrape logs (older than 90 days)
DELETE FROM sources
WHERE scrape_success = FALSE
  AND scraped_at < CURRENT_DATE - INTERVAL '90 days';
```

**Index Maintenance:**
```sql
-- Rebuild indexes if fragmented
REINDEX TABLE raw_items;
REINDEX TABLE clinics;
```

### 8.3 Monitoring Queries

**Database Size:**
```sql
SELECT
    pg_size_pretty(pg_database_size('pain_point_radar')) AS database_size;
```

**Table Sizes:**
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Row Counts:**
```sql
SELECT
    'clinics' AS table_name,
    COUNT(*) AS row_count
FROM clinics
UNION ALL
SELECT 'raw_items', COUNT(*) FROM raw_items
UNION ALL
SELECT 'sources', COUNT(*) FROM sources
UNION ALL
SELECT 'derived_metadata', COUNT(*) FROM derived_metadata;
```

---

## APPENDICES

### A. Data Retention Policy

| Table | Retention Period | Rationale |
|-------|-----------------|-----------|
| `clinics` | Indefinite | Master data |
| `sources` (success) | 90 days | Audit trail, archived after |
| `sources` (failure) | 30 days | Debugging only |
| `raw_items` | 12 months | Analysis on recent data |
| `derived_metadata` | 24 months | Historical insights |

### B. Performance Benchmarks

**Target Performance (t3.medium EC2, 1000 clinics, 100K items):**

| Query Type | Target | Measured |
|------------|--------|----------|
| Clinic lookup by ID | <1ms | TBD |
| Reviews for clinic (100 items) | <10ms | TBD |
| Full-text search (1000 items) | <50ms | TBD |
| Pain point aggregation | <100ms | TBD |
| CSV export (10K rows) | <2s | TBD |

### C. Glossary

- **JSONB:** PostgreSQL's binary JSON format (indexed, queryable)
- **GIN Index:** Generalized Inverted Index (for JSONB and arrays)
- **Partitioning:** Splitting large tables into smaller chunks
- **VACUUM:** PostgreSQL maintenance command to reclaim storage

---

**Document Version:** 1.0
**Status:** Awaiting Founder Approval
**Next:** Create IMPLEMENTATION_ROADMAP.md
