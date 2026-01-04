# 🎯 Pain Point Radar - Technical Design Document

**Project:** Private Clinic Pain Point Monitoring System
**Version:** 1.0
**Author:** System Architect (Claude) + Rob (Founder)
**Date:** 2025-01-03
**Status:** Design Phase - Awaiting Approval

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Database Schema Design](#database-schema-design)
4. [Data Source Strategy](#data-source-strategy)
5. [Scraping Implementation](#scraping-implementation)
6. [Orchestration & Scheduling](#orchestration--scheduling)
7. [Export & Analysis Integration](#export--analysis-integration)
8. [Keyword Automation Logic](#keyword-automation-logic)
9. [Integration with ManagementTeam](#integration-with-managementteam)
10. [Risk Assessment & Hardening](#risk-assessment--hardening)
11. [Technology Recommendations](#technology-recommendations)
12. [Implementation Phases](#implementation-phases)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Purpose

The **Pain Point Radar** is a continuous monitoring system that scrapes, stores, and analyzes data about private clinics in the UK & Ireland to identify pain points, operational challenges, and business opportunities.

Unlike the existing ManagementTeam system (which performs one-time analysis on demand), this module:
- **Runs continuously** on autopilot
- **Monitors multiple data sources** (reviews, job ads, websites, directories)
- **Builds a structured database** for longitudinal analysis
- **Exports to Perplexity** for AI-powered insight generation
- **Supports both passive AND active research** (future phase)

### 1.2 Target Market

**Geographic Scope:** UK & Ireland
**Clinic Types:**
1. Physiotherapy clinics
2. Counselling/therapy practices
3. Chiropody/podiatry clinics
4. Multi-practitioner clinics (combined services)

### 1.3 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Postgres Database** | Relational structure needed for analytics, BI tools compatibility, robust querying |
| **Proven Scrapers** | Use Scrapy/Playwright templates (NOT custom scrapers) for reliability and maintenance |
| **Scheduled Orchestration** | Prefect preferred over Airflow (lighter, Python-native, better for small-medium scale) |
| **Modular Architecture** | Each data source = separate scraper module for maintainability |
| **Export-First Design** | Structured exports for Perplexity, Excel, CSV ensure data accessibility |
| **Transparency by Default** | All scraped data includes source URL, timestamp, confidence metadata |

### 1.4 Success Metrics

- **Coverage:** 200+ clinics per type (800+ total) within 3 months
- **Data Freshness:** Reviews updated weekly, job ads updated daily, websites monthly
- **Quality:** <5% duplicate rate, >95% valid contact data
- **Uptime:** 99% scheduled job success rate
- **Export Speed:** <30 seconds to generate Perplexity export for 1000 records

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PAIN POINT RADAR SYSTEM                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐        ┌─────▼─────┐
   │ SCRAPERS │          │ POSTGRES  │        │  EXPORT   │
   │  LAYER   │─────────▶│  DATABASE │───────▶│   LAYER   │
   └──────────┘          └───────────┘        └───────────┘
        │                     │                     │
        │                     │                     │
   ┌────▼────────────────┐   │              ┌──────▼────────┐
   │ Data Sources:       │   │              │ Consumers:    │
   │ - Google Reviews    │   │              │ - Perplexity  │
   │ - Indeed Jobs       │   │              │ - Excel/CSV   │
   │ - Reed Jobs         │   │              │ - BI Tools    │
   │ - IrishJobs         │   │              │ - Management  │
   │ - Clinic Websites   │   │              │   Team System │
   │ - Directories       │   │              └───────────────┘
   └─────────────────────┘   │
                             │
                       ┌─────▼──────┐
                       │ ORCHESTRATOR│
                       │  (Prefect)  │
                       └─────────────┘
                             │
                    ┌────────┼────────┐
              ┌─────▼────┐ ┌▼────────▼────┐
              │ SCHEDULER│ │ MONITORING &  │
              │  (Cron)  │ │ ALERTS (Logs) │
              └──────────┘ └───────────────┘
```

### 2.2 Component Breakdown

#### Layer 1: Data Collection (Scrapers)

**Purpose:** Extract raw data from multiple sources
**Technology:** Scrapy (for APIs/structured data) + Playwright (for JavaScript-heavy sites)
**Output:** Raw JSON/CSV → Postgres staging tables

**Scraper Modules:**

1. **`google_reviews_scraper/`**
   - Scrapes Google Maps reviews for clinics
   - Extracts: rating, text, date, reviewer_name, response (if any)
   - Rate limit: 10 requests/minute (conservative)

2. **`job_boards_scraper/`**
   - Sub-modules: `indeed_scraper.py`, `reed_scraper.py`, `irishjobs_scraper.py`
   - Extracts: job_title, description, posted_date, salary (if available), company
   - Keywords: "physiotherapist", "counsellor", "chiropodist", "receptionist", "practice manager"

3. **`clinic_websites_scraper/`**
   - Crawls clinic websites (from directory listings)
   - Extracts: services_offered, pricing (if visible), team_size, technology_used (booking systems)
   - Respects robots.txt

4. **`directories_scraper/`**
   - Sources: Physio First, BACP (counselling), College of Podiatry directories
   - Extracts: clinic_name, address, phone, email, website, services

#### Layer 2: Database (Postgres)

**Purpose:** Structured storage for analysis and querying
**Schema:** See [Section 3](#database-schema-design)
**Tables:** `clinics`, `sources`, `raw_items`, `derived_metadata`

#### Layer 3: Orchestration (Prefect)

**Purpose:** Schedule, coordinate, and monitor scraping jobs
**Features:**
- DAG-based workflows (dependencies between scrapers)
- Retry logic with exponential backoff
- Logging and monitoring
- Parameterized flows (e.g., scrape UK vs Ireland separately)

**Example Flow:**
```
1. Scrape Directories (weekly) → Update clinics table
2. For each clinic:
   a. Scrape Google Reviews (weekly)
   b. Scrape Website (monthly)
3. Scrape Job Boards (daily)
4. Run deduplication job (daily)
5. Generate exports (on demand or weekly)
```

#### Layer 4: Export & Analysis

**Purpose:** Make data accessible to external tools and humans
**Formats:**
- **Perplexity Export:** Structured text summaries for AI analysis
- **CSV/Excel:** For manual review and BI tools
- **JSON API:** For ManagementTeam integration (future)

### 2.3 Data Flow Diagram

```
[Google Reviews] ──┐
[Indeed Jobs]    ──┤
[Reed Jobs]      ──┤
[IrishJobs]      ──├──▶ [Scrapers] ──▶ [Raw Data] ──▶ [Validation] ──▶ [Postgres]
[Clinic Sites]   ──┤                                                        │
[Directories]    ──┘                                                        │
                                                                            │
                                    ┌───────────────────────────────────────┘
                                    │
                              [Deduplication]
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              [Perplexity      [CSV/Excel     [Management
               Export]          Export]        Team API]
```

---

## 3. DATABASE SCHEMA DESIGN

### 3.1 Schema Philosophy

**Design Principles:**
1. **Normalization:** Separate clinics, sources, and raw items to avoid duplication
2. **Source Tracking:** Every piece of data includes source_id for audit trails
3. **Flexibility:** `raw_items` table stores heterogeneous data (reviews, jobs, website content)
4. **Metadata:** Derived insights stored separately from raw data
5. **Temporal:** All records include `scraped_at` and `last_updated_at` timestamps

### 3.2 Core Tables

#### Table 1: `clinics`

**Purpose:** Master list of all clinics being monitored

```sql
CREATE TABLE clinics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    clinic_type VARCHAR(50) NOT NULL CHECK (clinic_type IN ('physiotherapy', 'counselling', 'chiropody', 'multi_practitioner')),
    country VARCHAR(50) NOT NULL CHECK (country IN ('UK', 'Ireland')),
    region VARCHAR(100),  -- e.g., "London", "Dublin", "Manchester"
    address TEXT,
    postcode VARCHAR(20),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(500),
    google_maps_url VARCHAR(500),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'closed', 'merged', 'monitoring_paused')),
    first_discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,  -- Flexible storage for additional fields
    UNIQUE(name, postcode)  -- Prevent duplicates
);

CREATE INDEX idx_clinics_type ON clinics(clinic_type);
CREATE INDEX idx_clinics_country ON clinics(country);
CREATE INDEX idx_clinics_region ON clinics(region);
CREATE INDEX idx_clinics_status ON clinics(status);
```

**Sample Record:**
```json
{
  "id": 1,
  "name": "Central London Physiotherapy Clinic",
  "clinic_type": "physiotherapy",
  "country": "UK",
  "region": "London",
  "address": "123 High Street, London",
  "postcode": "SW1A 1AA",
  "phone": "+44 20 1234 5678",
  "email": "info@clphysio.co.uk",
  "website": "https://clphysio.co.uk",
  "google_maps_url": "https://maps.google.com/...",
  "latitude": 51.5074,
  "longitude": -0.1278,
  "status": "active",
  "first_discovered_at": "2025-01-03T10:00:00Z",
  "last_updated_at": "2025-01-03T10:00:00Z",
  "metadata": {
    "team_size": 5,
    "services": ["sports physio", "massage", "acupuncture"],
    "booking_system": "Cliniko"
  }
}
```

#### Table 2: `sources`

**Purpose:** Track all data sources for transparency and audit trails

```sql
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('google_review', 'job_ad', 'website_content', 'directory_listing', 'manual_entry')),
    source_name VARCHAR(100) NOT NULL,  -- e.g., "Indeed", "Google Reviews", "Physio First Directory"
    source_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    scraper_version VARCHAR(20),  -- e.g., "v1.2.3" for reproducibility
    scrape_success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    metadata JSONB
);

CREATE INDEX idx_sources_type ON sources(source_type);
CREATE INDEX idx_sources_scraped_at ON sources(scraped_at);
```

**Sample Record:**
```json
{
  "id": 1001,
  "source_type": "google_review",
  "source_name": "Google Maps Reviews",
  "source_url": "https://maps.google.com/...",
  "scraped_at": "2025-01-03T10:15:00Z",
  "scraper_version": "v1.0.0",
  "scrape_success": true,
  "error_message": null,
  "metadata": {
    "reviews_collected": 15,
    "rate_limit_hit": false
  }
}
```

#### Table 3: `raw_items`

**Purpose:** Store all scraped data in flexible format (heterogeneous data types)

```sql
CREATE TABLE raw_items (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('review', 'job_ad', 'website_snapshot', 'directory_entry')),
    content JSONB NOT NULL,  -- Flexible structure per item_type
    text_excerpt TEXT,  -- For full-text search
    sentiment_score DECIMAL(3, 2),  -- -1.0 to 1.0 (if analyzed)
    urgency_detected VARCHAR(20) CHECK (urgency_detected IN ('critical', 'high', 'medium', 'low')),
    keywords TEXT[],  -- Array of detected keywords
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_duplicate BOOLEAN DEFAULT FALSE,
    duplicate_of INTEGER REFERENCES raw_items(id),
    metadata JSONB,
    UNIQUE(clinic_id, item_type, content)  -- Prevent exact duplicates
);

CREATE INDEX idx_raw_items_clinic ON raw_items(clinic_id);
CREATE INDEX idx_raw_items_type ON raw_items(item_type);
CREATE INDEX idx_raw_items_scraped_at ON raw_items(scraped_at);
CREATE INDEX idx_raw_items_text_search ON raw_items USING gin(to_tsvector('english', text_excerpt));
CREATE INDEX idx_raw_items_keywords ON raw_items USING gin(keywords);
```

**Sample Records:**

**Google Review:**
```json
{
  "id": 5001,
  "clinic_id": 1,
  "source_id": 1001,
  "item_type": "review",
  "content": {
    "rating": 2,
    "text": "Phone system is terrible. Always goes to voicemail. Lost 3 appointments because I couldn't get through.",
    "reviewer_name": "Sarah M.",
    "review_date": "2024-12-15",
    "clinic_response": null
  },
  "text_excerpt": "Phone system is terrible. Always goes to voicemail. Lost 3 appointments because I couldn't get through.",
  "sentiment_score": -0.75,
  "urgency_detected": "critical",
  "keywords": ["phone", "voicemail", "appointments", "communication"],
  "scraped_at": "2025-01-03T10:15:00Z",
  "is_duplicate": false,
  "duplicate_of": null,
  "metadata": {
    "upvotes": 12,
    "verified_patient": true
  }
}
```

**Job Ad:**
```json
{
  "id": 5002,
  "clinic_id": 1,
  "source_id": 1002,
  "item_type": "job_ad",
  "content": {
    "job_title": "Receptionist - Physiotherapy Clinic",
    "description": "Busy clinic seeks receptionist to manage phones, bookings, and patient queries. Must be comfortable with high call volume.",
    "posted_date": "2025-01-01",
    "salary": "£22,000 - £25,000",
    "job_board": "Indeed",
    "job_url": "https://indeed.co.uk/..."
  },
  "text_excerpt": "Busy clinic seeks receptionist to manage phones, bookings, and patient queries. Must be comfortable with high call volume.",
  "sentiment_score": null,
  "urgency_detected": "high",
  "keywords": ["receptionist", "phones", "bookings", "high_call_volume"],
  "scraped_at": "2025-01-03T11:00:00Z",
  "is_duplicate": false,
  "duplicate_of": null,
  "metadata": {
    "applications_count": 45,
    "days_since_posted": 2
  }
}
```

#### Table 4: `derived_metadata`

**Purpose:** Store analyzed insights and aggregated metrics (separate from raw data)

```sql
CREATE TABLE derived_metadata (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES clinics(id) ON DELETE CASCADE,
    metric_type VARCHAR(100) NOT NULL,  -- e.g., "avg_rating", "top_pain_points", "hiring_frequency"
    metric_value JSONB NOT NULL,
    confidence_level VARCHAR(20) CHECK (confidence_level IN ('high', 'medium', 'low', 'insufficient')),
    based_on_item_ids INTEGER[],  -- References to raw_items
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    calculation_version VARCHAR(20),  -- e.g., "v1.0" for reproducibility
    metadata JSONB
);

CREATE INDEX idx_derived_clinic ON derived_metadata(clinic_id);
CREATE INDEX idx_derived_type ON derived_metadata(metric_type);
CREATE INDEX idx_derived_calculated_at ON derived_metadata(calculated_at);
```

**Sample Record:**
```json
{
  "id": 8001,
  "clinic_id": 1,
  "metric_type": "top_pain_points",
  "metric_value": {
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
        "pain_point": "Booking system complexity",
        "mentions": 5,
        "severity": "high",
        "evidence_count": 5,
        "example_quotes": [
          "Online booking is confusing.",
          "Had to call 3 times to reschedule."
        ]
      }
    ]
  },
  "confidence_level": "high",
  "based_on_item_ids": [5001, 5003, 5007, 5012, 5015, 5020, 5025, 5030],
  "calculated_at": "2025-01-03T12:00:00Z",
  "calculation_version": "v1.0",
  "metadata": {
    "total_reviews_analyzed": 35,
    "date_range": "2024-01-01 to 2025-01-03"
  }
}
```

### 3.3 Additional Tables (Future Phases)

**Phase 2 Additions:**

```sql
-- Active research data (LinkedIn posts, surveys)
CREATE TABLE active_research (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES clinics(id),
    research_type VARCHAR(50) CHECK (research_type IN ('linkedin_post', 'survey_response', 'interview', 'email_outreach')),
    content JSONB,
    response_received BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Competitive intelligence
CREATE TABLE competitors (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES clinics(id),
    competitor_name VARCHAR(255),
    competitor_type VARCHAR(100),  -- e.g., "AI receptionist", "booking software"
    evidence_source INTEGER REFERENCES raw_items(id),
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
```

---

## 4. DATA SOURCE STRATEGY

### 4.1 Data Source Prioritization

**Phase 1 (MVP - 4-6 weeks):**

| Source | Priority | Rationale | Update Frequency | Estimated Yield |
|--------|----------|-----------|------------------|-----------------|
| **Google Reviews** | HIGH | Direct patient feedback, rich pain point data | Weekly | 500-1000 reviews/week |
| **Job Boards (Indeed, Reed)** | HIGH | Reveals operational challenges (hiring needs) | Daily | 50-100 ads/week |
| **Professional Directories** | HIGH | Builds clinic master list (foundation) | Weekly (initial), Monthly (ongoing) | 800-1200 clinics |

**Phase 2 (Expansion - 4-6 weeks):**

| Source | Priority | Rationale | Update Frequency | Estimated Yield |
|--------|----------|-----------|------------------|-----------------|
| **Clinic Websites** | MEDIUM | Technology stack, services, pricing | Monthly | 500-800 sites |
| **Trustpilot Reviews** | MEDIUM | Additional review data, potentially less filtered | Weekly | 200-400 reviews/week |
| **IrishJobs** | MEDIUM | Ireland-specific job market insights | Daily | 10-20 ads/week |

**Phase 3 (Active Research - 2-4 weeks):**

| Source | Priority | Rationale | Update Frequency | Estimated Yield |
|--------|----------|-----------|------------------|-----------------|
| **LinkedIn Posts** | LOW (manual) | Active engagement, lead generation | Manual campaigns | 20-50 responses/campaign |
| **Surveys (TypeForm)** | LOW (manual) | Targeted questions, high-quality data | Manual campaigns | 10-30 responses/survey |

### 4.2 Data Source Details

#### Source 1: Google Reviews

**URL Pattern:**
`https://www.google.com/maps/place/[CLINIC_NAME]/[PLACE_ID]`

**Extraction Method:**
Playwright (JavaScript rendering required)

**Boilerplate:**
`playwright-scraper-template` + `google-maps-reviews-scraper` (open-source)

**Rate Limits:**
10 requests/minute (conservative to avoid blocks)

**Data Extracted:**
- `rating` (1-5 stars)
- `text` (review content)
- `reviewer_name`
- `review_date`
- `clinic_response` (if owner replied)
- `upvotes` (helpful count)

**Challenges:**
- Google aggressively blocks scrapers → Use residential proxies + rotation
- Reviews paginated → Scroll simulation required
- Rate limiting → Implement exponential backoff

**Deduplication:**
Hash of `(clinic_id, reviewer_name, review_date, text[:50])`

---

#### Source 2: Job Boards

**Indeed (UK):**
`https://www.indeed.co.uk/jobs?q=[KEYWORD]&l=[LOCATION]`

**Reed (UK):**
`https://www.reed.co.uk/jobs/[KEYWORD]-jobs-in-[LOCATION]`

**IrishJobs (Ireland):**
`https://www.irishjobs.ie/Jobs/[KEYWORD]`

**Extraction Method:**
Scrapy (HTML parsing, no JavaScript needed)

**Boilerplate:**
`scrapy-job-board-spider` (custom template)

**Keywords:**
- Primary: "physiotherapist", "counsellor", "chiropodist", "podiatrist"
- Secondary: "receptionist physiotherapy", "practice manager clinic", "admin healthcare"

**Rate Limits:**
20 requests/minute (Indeed), 30 requests/minute (Reed)

**Data Extracted:**
- `job_title`
- `description` (full text)
- `posted_date`
- `salary` (if available)
- `company_name`
- `location`
- `job_url`

**Pain Point Signals:**
- Recurring job ads for same clinic → High turnover
- Urgent language ("ASAP", "immediate start") → Operational strain
- Admin/receptionist roles → Phone/booking challenges

**Deduplication:**
Hash of `(job_url)` (unique per job board)

---

#### Source 3: Professional Directories

**Physio First (UK Physiotherapy):**
`https://www.physio-first.org.uk/find-a-physio`

**BACP (UK Counselling):**
`https://www.bacp.co.uk/search/Therapists`

**College of Podiatry (UK Chiropody):**
`https://www.scpod.org/find-a-podiatrist/`

**Irish Society of Chartered Physiotherapists:**
`https://www.iscp.ie/find-a-chartered-physiotherapist`

**Extraction Method:**
Scrapy (most directories are HTML-based)

**Rate Limits:**
10 requests/minute (respectful, public directories)

**Data Extracted:**
- `clinic_name`
- `address`
- `phone`
- `email`
- `website`
- `services_offered`
- `qualifications` (therapist credentials)

**Purpose:**
Build initial `clinics` table, discover new clinics to monitor

**Deduplication:**
Match on `(name, postcode)` with fuzzy matching (Levenshtein distance)

---

#### Source 4: Clinic Websites (Phase 2)

**Discovery:**
From directory listings (use `website` field)

**Extraction Method:**
Playwright (many use booking widgets = JavaScript)

**Boilerplate:**
`playwright-website-crawler`

**Rate Limits:**
5 requests/minute (respectful of small clinic servers)

**Data Extracted:**
- `services_offered` (parse service pages)
- `pricing` (if publicly visible)
- `team_size` (count staff on "Meet the Team" pages)
- `technology_used` (detect booking systems: Cliniko, Acuity, SimplePractice)
- `contact_methods` (phone, email, contact form, live chat)

**Pain Point Signals:**
- No online booking → Potential need for automation
- Complex navigation → UX issues
- No mobile-friendly design → Technology gap

**Robots.txt Compliance:**
MANDATORY - Check `robots.txt` before crawling, respect `Crawl-delay`

---

### 4.3 Keyword Automation Logic

**Problem:**
Manually defining keywords for each clinic type is not scalable.

**Solution:**
Automated keyword generation + refinement loop.

#### Step 1: Seed Keywords (Manual)

**Physiotherapy:**
```python
PHYSIO_SEEDS = [
    "physiotherapist", "physio", "physical therapy",
    "sports injury", "massage therapist", "osteopath"
]
```

**Counselling:**
```python
COUNSELLING_SEEDS = [
    "counsellor", "therapist", "psychotherapist", "psychologist",
    "mental health", "CBT", "EMDR"
]
```

**Chiropody:**
```python
CHIROPODY_SEEDS = [
    "chiropodist", "podiatrist", "foot care", "foot clinic"
]
```

#### Step 2: Automated Expansion (HuggingFace)

**Tool:** KeyBERT or BERT-based synonym expansion

```python
from keybert import KeyBERT

def expand_keywords(seed_keywords: List[str], corpus: List[str]) -> List[str]:
    """
    Expand seed keywords using KeyBERT on existing corpus.

    Args:
        seed_keywords: Initial manual keywords
        corpus: Existing reviews/job ads text

    Returns:
        Expanded keyword list (top 50)
    """
    kw_model = KeyBERT(model='all-MiniLM-L6-v2')

    # Extract keywords from corpus
    combined_text = " ".join(corpus)
    keywords = kw_model.extract_keywords(
        combined_text,
        keyphrase_ngram_range=(1, 3),
        stop_words='english',
        use_mmr=True,
        diversity=0.7,
        top_n=50
    )

    # Combine with seeds
    expanded = seed_keywords + [kw[0] for kw in keywords]

    return list(set(expanded))  # Remove duplicates
```

**Frequency:** Run weekly on new data, auto-update keyword lists

#### Step 3: Manual Review (Human-in-the-Loop)

**Output:**
Generate `keywords_review_YYYY_MM_DD.md` with proposed additions

**Review Checklist:**
- [ ] Are new keywords relevant to pain points?
- [ ] Any false positives (irrelevant terms)?
- [ ] Missing synonyms or regional terms (UK vs Ireland)?

**Approval:** Rob reviews and approves/rejects suggested keywords

#### Step 4: Feedback Loop

**Metrics:**
- Keyword hit rate (% of scraped items matched)
- False positive rate (manual sampling)
- Coverage gaps (items with no keywords detected)

**Adjustment:** Refine keyword weights, add negatives (e.g., "-hiring -job" for review scraping)

---

## 5. SCRAPING IMPLEMENTATION

### 5.1 Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Static HTML Scraping** | Scrapy | Battle-tested, fast, built-in rate limiting |
| **JavaScript-Heavy Sites** | Playwright | Headless browser, handles dynamic content |
| **Proxy Management** | Bright Data or ScraperAPI | Residential proxies, auto-rotation |
| **Storage** | Postgres | Relational queries, JSONB for flexibility |
| **Orchestration** | Prefect | Python-native, easier than Airflow for small-medium scale |

### 5.2 Scraper Architecture (Modular Design)

**Directory Structure:**
```
src/scrapers/
├── __init__.py
├── base_scraper.py           # Abstract base class
├── google_reviews/
│   ├── __init__.py
│   ├── scraper.py            # Playwright-based scraper
│   ├── config.yaml           # Rate limits, selectors
│   └── tests/
├── job_boards/
│   ├── __init__.py
│   ├── indeed_scraper.py     # Scrapy spider
│   ├── reed_scraper.py       # Scrapy spider
│   ├── irishjobs_scraper.py  # Scrapy spider
│   └── tests/
├── directories/
│   ├── __init__.py
│   ├── physio_first.py       # Scrapy spider
│   ├── bacp.py               # Scrapy spider
│   └── tests/
└── utils/
    ├── deduplication.py
    ├── proxy_manager.py
    └── rate_limiter.py
```

### 5.3 Base Scraper Template

```python
# src/scrapers/base_scraper.py

from abc import ABC, abstractmethod
from typing import List, Dict
import logging
from datetime import datetime

class BaseScraper(ABC):
    """
    Abstract base class for all scrapers.
    Enforces transparency and audit trail requirements.
    """

    def __init__(self, scraper_name: str, version: str):
        self.scraper_name = scraper_name
        self.version = version
        self.logger = logging.getLogger(scraper_name)

    @abstractmethod
    def scrape(self, **kwargs) -> List[Dict]:
        """
        Main scraping method. Must be implemented by subclasses.

        Returns:
            List of dicts with standardized structure:
            {
                "content": {...},        # Raw scraped data
                "source_url": "...",     # URL scraped from
                "scraped_at": "...",     # ISO timestamp
                "scraper_version": "...", # For reproducibility
                "metadata": {...}        # Additional context
            }
        """
        pass

    def _create_audit_trail(self, source_url: str, success: bool, error: str = None) -> Dict:
        """Create standardized audit trail."""
        return {
            "source_url": source_url,
            "scraped_at": datetime.utcnow().isoformat(),
            "scraper_name": self.scraper_name,
            "scraper_version": self.version,
            "scrape_success": success,
            "error_message": error
        }

    def _save_to_db(self, items: List[Dict], db_connection):
        """
        Save scraped items to database with full transparency.
        """
        for item in items:
            # Insert into sources table
            source_record = self._create_audit_trail(
                item['source_url'],
                success=True
            )
            source_id = db_connection.insert_source(source_record)

            # Insert into raw_items table
            raw_item = {
                "clinic_id": item.get('clinic_id'),
                "source_id": source_id,
                "item_type": item['item_type'],
                "content": item['content'],
                "text_excerpt": item.get('text_excerpt'),
                "scraped_at": item['scraped_at'],
                "metadata": item.get('metadata', {})
            }
            db_connection.insert_raw_item(raw_item)

        self.logger.info(f"Saved {len(items)} items to database")
```

### 5.4 Example: Google Reviews Scraper

```python
# src/scrapers/google_reviews/scraper.py

from playwright.sync_api import sync_playwright
from ..base_scraper import BaseScraper
import time
import random

class GoogleReviewsScraper(BaseScraper):
    """
    Scrapes Google Maps reviews for clinics using Playwright.
    """

    def __init__(self):
        super().__init__(scraper_name="google_reviews", version="v1.0.0")
        self.rate_limit_delay = 6  # 10 requests/minute = 6 sec delay

    def scrape(self, clinic_name: str, google_maps_url: str, max_reviews: int = 50) -> List[Dict]:
        """
        Scrape reviews for a specific clinic.

        Args:
            clinic_name: Name of clinic (for logging)
            google_maps_url: Google Maps URL
            max_reviews: Max number of reviews to scrape

        Returns:
            List of review dicts
        """
        self.logger.info(f"Scraping reviews for {clinic_name}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # Navigate to Google Maps
                page.goto(google_maps_url, wait_until='networkidle')

                # Click "Reviews" tab
                page.click('button:has-text("Reviews")')
                time.sleep(2)

                # Scroll to load reviews
                reviews_container = page.locator('[role="feed"]')
                self._scroll_reviews(page, reviews_container, max_reviews)

                # Extract reviews
                review_elements = page.locator('.jftiEf').all()
                reviews = []

                for idx, review_el in enumerate(review_elements[:max_reviews]):
                    try:
                        review_data = self._extract_review(review_el)
                        review_data['source_url'] = google_maps_url
                        review_data['scraped_at'] = datetime.utcnow().isoformat()
                        review_data['scraper_version'] = self.version
                        reviews.append(review_data)
                    except Exception as e:
                        self.logger.warning(f"Failed to extract review {idx}: {e}")

                browser.close()

                # Rate limiting
                time.sleep(self.rate_limit_delay + random.uniform(0, 2))

                return reviews

            except Exception as e:
                self.logger.error(f"Scraping failed for {clinic_name}: {e}")
                browser.close()
                return []

    def _scroll_reviews(self, page, container, target_count):
        """Scroll to load more reviews."""
        for _ in range(target_count // 10):  # ~10 reviews per scroll
            container.evaluate('el => el.scrollTop = el.scrollHeight')
            time.sleep(1)

    def _extract_review(self, review_element) -> Dict:
        """Extract data from a single review element."""
        rating_el = review_element.locator('[role="img"]').get_attribute('aria-label')
        rating = int(rating_el.split()[0]) if rating_el else None

        text = review_element.locator('.wiI7pd').inner_text() if review_element.locator('.wiI7pd').count() > 0 else ""

        reviewer = review_element.locator('.d4r55').inner_text() if review_element.locator('.d4r55').count() > 0 else ""

        date_text = review_element.locator('.rsqaWe').inner_text() if review_element.locator('.rsqaWe').count() > 0 else ""

        return {
            "item_type": "review",
            "content": {
                "rating": rating,
                "text": text,
                "reviewer_name": reviewer,
                "review_date": date_text,
                "clinic_response": None  # TODO: Extract if present
            },
            "text_excerpt": text,
            "metadata": {}
        }
```

**Key Features:**
- Extends `BaseScraper` for consistency
- Handles rate limiting (6 sec delay + random jitter)
- Scroll simulation to load reviews
- Error handling per review (doesn't fail entire scrape if one review fails)
- Audit trail automatically included

### 5.5 Deduplication Strategy

**Problem:** Same review/job ad scraped multiple times

**Solution:** Multi-layer deduplication

#### Layer 1: Database Constraints

```sql
-- Prevent exact duplicates at insert time
UNIQUE(clinic_id, item_type, content)
```

#### Layer 2: Hash-Based Detection

```python
# src/scrapers/utils/deduplication.py

import hashlib
import json

def generate_content_hash(item: Dict) -> str:
    """
    Generate hash for deduplication.

    Args:
        item: Raw item dict

    Returns:
        SHA256 hash of content
    """
    # Normalize content (sort keys, remove timestamps)
    normalized = {
        "clinic_id": item.get('clinic_id'),
        "item_type": item['item_type'],
        "content": item['content']
    }

    # Generate hash
    content_str = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()

def is_duplicate(item: Dict, db_connection) -> bool:
    """
    Check if item already exists in database.

    Args:
        item: Item to check
        db_connection: Database connection

    Returns:
        True if duplicate exists
    """
    content_hash = generate_content_hash(item)

    # Query database for matching hash
    existing = db_connection.query(
        "SELECT id FROM raw_items WHERE content_hash = %s",
        (content_hash,)
    )

    return len(existing) > 0
```

#### Layer 3: Fuzzy Matching (for text variations)

**Use Case:** Same review with slight text differences (typos fixed, punctuation changed)

**Tool:** RapidFuzz (Levenshtein distance)

```python
from rapidfuzz import fuzz

def is_fuzzy_duplicate(new_text: str, existing_texts: List[str], threshold: int = 90) -> bool:
    """
    Check if text is fuzzy duplicate of existing items.

    Args:
        new_text: New review/job ad text
        existing_texts: List of existing texts to compare against
        threshold: Similarity threshold (0-100, default 90%)

    Returns:
        True if fuzzy duplicate found
    """
    for existing in existing_texts:
        similarity = fuzz.ratio(new_text, existing)
        if similarity >= threshold:
            return True
    return False
```

**Trade-off:** Fuzzy matching is expensive → Only run on items that pass hash check

---

## 6. ORCHESTRATION & SCHEDULING

### 6.1 Why Prefect Over Airflow

| Criterion | Prefect | Airflow | Decision |
|-----------|---------|---------|----------|
| **Setup Complexity** | Minimal (pip install) | High (Docker + configs) | ✅ Prefect |
| **Python-Native** | Yes (Pythonic API) | Yes but DSL-heavy | ✅ Prefect |
| **Scaling** | Good for small-medium | Excellent for large | ✅ Prefect (our scale) |
| **UI** | Modern, intuitive | Functional but dated | ✅ Prefect |
| **Cost** | Free (self-hosted) or Cloud ($) | Free (self-hosted) | Tie |
| **Learning Curve** | Low | Medium-High | ✅ Prefect |

**Recommendation:** Use Prefect for Phase 1-2, re-evaluate if scaling beyond 10K+ daily scrapes.

### 6.2 Prefect Flow Architecture

**Flow Structure:**

```
Main Flow: "pain_point_radar_daily"
│
├── Subflow 1: "update_clinic_master_list" (Weekly)
│   ├── Task: Scrape Physio First Directory
│   ├── Task: Scrape BACP Directory
│   ├── Task: Scrape College of Podiatry
│   └── Task: Merge + Deduplicate Clinics
│
├── Subflow 2: "scrape_reviews" (Weekly)
│   ├── Task: Get Active Clinics (from DB)
│   ├── Task: Scrape Google Reviews (parallel, 10 at a time)
│   └── Task: Save Reviews to DB
│
├── Subflow 3: "scrape_job_boards" (Daily)
│   ├── Task: Scrape Indeed UK
│   ├── Task: Scrape Reed UK
│   ├── Task: Scrape IrishJobs
│   └── Task: Save Job Ads to DB
│
└── Subflow 4: "deduplication_and_analysis" (Daily)
    ├── Task: Run Deduplication
    ├── Task: Calculate Derived Metadata
    └── Task: Generate Exports
```

### 6.3 Example Prefect Flow

```python
# src/orchestration/flows/daily_scraping_flow.py

from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
from datetime import timedelta
import logging

from src.scrapers.google_reviews.scraper import GoogleReviewsScraper
from src.scrapers.job_boards.indeed_scraper import IndeedScraper
from src.database.postgres_client import PostgresClient

logger = logging.getLogger(__name__)

@task(retries=3, retry_delay_seconds=60)
def scrape_clinic_reviews(clinic_id: int, clinic_name: str, google_maps_url: str):
    """
    Scrape reviews for a single clinic.

    Retries: 3 times with 60-second delay (handles transient errors)
    """
    scraper = GoogleReviewsScraper()
    reviews = scraper.scrape(clinic_name, google_maps_url, max_reviews=50)

    # Save to database
    db = PostgresClient()
    for review in reviews:
        review['clinic_id'] = clinic_id
        db.insert_raw_item(review)

    return len(reviews)

@task(retries=2, retry_delay_seconds=30)
def scrape_indeed_jobs(keywords: List[str], location: str):
    """
    Scrape Indeed job board.
    """
    scraper = IndeedScraper()
    jobs = scraper.scrape(keywords=keywords, location=location, max_pages=5)

    # Save to database
    db = PostgresClient()
    for job in jobs:
        db.insert_raw_item(job)

    return len(jobs)

@flow(name="scrape_reviews_weekly", log_prints=True)
def scrape_reviews_flow():
    """
    Weekly flow to scrape Google reviews for all active clinics.
    """
    db = PostgresClient()
    active_clinics = db.query("SELECT id, name, google_maps_url FROM clinics WHERE status = 'active' AND google_maps_url IS NOT NULL")

    logger.info(f"Scraping reviews for {len(active_clinics)} clinics")

    # Scrape in parallel (10 concurrent tasks)
    results = []
    for clinic in active_clinics:
        result = scrape_clinic_reviews.submit(
            clinic_id=clinic['id'],
            clinic_name=clinic['name'],
            google_maps_url=clinic['google_maps_url']
        )
        results.append(result)

    # Wait for all tasks to complete
    total_reviews = sum([r.result() for r in results])
    logger.info(f"Scraped {total_reviews} reviews total")

    return total_reviews

@flow(name="scrape_job_boards_daily", log_prints=True)
def scrape_jobs_flow():
    """
    Daily flow to scrape job boards.
    """
    keywords = ["physiotherapist", "counsellor", "chiropodist", "receptionist physiotherapy"]
    locations = ["London", "Manchester", "Birmingham", "Dublin", "Cork"]

    total_jobs = 0
    for location in locations:
        jobs_count = scrape_indeed_jobs(keywords, location)
        total_jobs += jobs_count

    logger.info(f"Scraped {total_jobs} job ads")
    return total_jobs

@flow(name="pain_point_radar_main", task_runner=ConcurrentTaskRunner())
def main_flow():
    """
    Main orchestration flow (runs daily).
    """
    logger.info("Starting Pain Point Radar main flow")

    # Run job scraping daily
    scrape_jobs_flow()

    # Run review scraping weekly (check if today is Monday)
    from datetime import datetime
    if datetime.now().weekday() == 0:  # Monday
        scrape_reviews_flow()

    logger.info("Pain Point Radar main flow complete")

# Schedule the flow
if __name__ == "__main__":
    # Run immediately (for testing)
    main_flow()

    # OR: Deploy with schedule
    # main_flow.serve(
    #     name="pain-point-radar-daily",
    #     cron="0 2 * * *"  # Run at 2 AM daily
    # )
```

### 6.4 Scheduling Strategy

| Flow | Schedule | Rationale |
|------|----------|-----------|
| **Job Board Scraping** | Daily at 2 AM | Fresh job ads, low competition for API/scraper resources |
| **Google Reviews** | Weekly (Monday 3 AM) | Reviews change slowly, weekly sufficient |
| **Directory Updates** | Monthly (1st of month, 4 AM) | Directories rarely change |
| **Website Scraping** | Monthly (15th of month, 5 AM) | Clinic websites stable |
| **Deduplication** | Daily at 6 AM (after scraping) | Clean data before exports |

**Cron Expressions:**
```python
# Daily job scraping at 2 AM
"0 2 * * *"

# Weekly reviews (Monday at 3 AM)
"0 3 * * 1"

# Monthly directory updates (1st of month, 4 AM)
"0 4 1 * *"
```

### 6.5 Error Handling & Monitoring

**Strategy:** Graceful degradation + alerts

```python
@task(retries=3, retry_delay_seconds=60, on_failure=[send_alert])
def scrape_with_monitoring(clinic_id: int):
    """
    Scrape with error monitoring.
    """
    try:
        # Scraping logic
        result = scraper.scrape(...)
        return result
    except Exception as e:
        logger.error(f"Scraping failed for clinic {clinic_id}: {e}")
        # Log to monitoring system (e.g., Sentry, CloudWatch)
        log_error_to_monitoring(clinic_id, str(e))
        raise  # Re-raise for Prefect retry logic

def send_alert(task, state):
    """
    Send alert on task failure (after all retries exhausted).
    """
    # Email alert to Rob
    send_email(
        to="rob@example.com",
        subject=f"Pain Point Radar: {task.name} Failed",
        body=f"Task {task.name} failed after 3 retries. State: {state}"
    )
```

**Monitoring Metrics:**
- Task success rate (% of tasks completed without retries)
- Average task duration
- Items scraped per day
- Error rate by scraper type
- Database growth rate

---

## 7. EXPORT & ANALYSIS INTEGRATION

### 7.1 Export Formats

#### Format 1: Perplexity Export (Structured Text Summary)

**Purpose:** Feed to Perplexity AI for insight generation

**Structure:**
```markdown
# Pain Point Analysis Export
**Clinic:** Central London Physiotherapy Clinic
**Generated:** 2025-01-03
**Data Period:** 2024-01-01 to 2025-01-03

## Reviews Summary (35 reviews)
**Average Rating:** 3.2/5
**Sentiment:** Mixed (60% negative)

### Top Pain Points:
1. **Phone System / Missed Calls** (8 mentions, critical)
   - "Phone system is terrible. Always goes to voicemail."
   - "Can never get through on the phone."
   - Evidence: Review IDs [5001, 5003, 5007...]

2. **Booking Complexity** (5 mentions, high)
   - "Online booking is confusing."
   - Evidence: Review IDs [5010, 5015...]

## Job Ads Summary (3 ads in last 30 days)
**Hiring Frequency:** High (3 ads/month suggests turnover)
**Roles:**
- Receptionist (2 ads) - "Must handle high call volume"
- Practice Manager (1 ad) - "Improve operational efficiency"

**Urgency Signals:**
- "ASAP start" (1 ad)
- "Immediate start preferred" (1 ad)

## Technology Stack (from website)
- Booking System: Cliniko
- Phone: Traditional landline (no VoIP)
- Website: WordPress (outdated design)

## Competitive Intelligence
**Competitors Mentioned:**
- "Switched to [Competitor Clinic] because they have online booking"

---

**Recommended Questions for Perplexity:**
1. What are the root causes of phone system issues in small clinics?
2. How do AI receptionists address high call volume challenges?
3. What booking systems integrate best with Cliniko?
```

**Implementation:**
```python
def generate_perplexity_export(clinic_id: int, output_path: str):
    """
    Generate Perplexity-friendly export for a clinic.
    """
    db = PostgresClient()

    # Get clinic data
    clinic = db.get_clinic(clinic_id)
    reviews = db.get_reviews(clinic_id, limit=100)
    jobs = db.get_job_ads(clinic_id, days=30)
    metadata = db.get_derived_metadata(clinic_id)

    # Generate markdown
    export_md = f"""
# Pain Point Analysis Export
**Clinic:** {clinic['name']}
**Generated:** {datetime.now().strftime('%Y-%m-%d')}

## Reviews Summary ({len(reviews)} reviews)
{_summarize_reviews(reviews)}

## Job Ads Summary ({len(jobs)} ads)
{_summarize_jobs(jobs)}

## Top Pain Points
{_format_pain_points(metadata['top_pain_points'])}
"""

    # Save to file
    with open(output_path, 'w') as f:
        f.write(export_md)

    return output_path
```

#### Format 2: CSV Export (for Excel / BI Tools)

**Structure:**
```csv
clinic_id,clinic_name,item_type,text_excerpt,sentiment_score,urgency,scraped_date,source_url
1,"Central London Physio","review","Phone system terrible",-0.75,"critical","2025-01-03","https://maps.google.com/..."
1,"Central London Physio","job_ad","Receptionist needed ASAP",null,"high","2025-01-02","https://indeed.co.uk/..."
```

**Implementation:**
```python
def generate_csv_export(clinic_id: int = None, output_path: str = "export.csv"):
    """
    Generate CSV export for all clinics or specific clinic.
    """
    db = PostgresClient()

    query = """
        SELECT
            c.id AS clinic_id,
            c.name AS clinic_name,
            r.item_type,
            r.text_excerpt,
            r.sentiment_score,
            r.urgency_detected,
            r.scraped_at,
            s.source_url
        FROM raw_items r
        JOIN clinics c ON r.clinic_id = c.id
        JOIN sources s ON r.source_id = s.id
    """

    if clinic_id:
        query += f" WHERE c.id = {clinic_id}"

    query += " ORDER BY r.scraped_at DESC"

    # Execute and export
    df = pd.read_sql(query, db.connection)
    df.to_csv(output_path, index=False)

    return output_path
```

#### Format 3: JSON API (for ManagementTeam Integration)

**Endpoint:** `/api/pain-points/{clinic_id}`

**Response:**
```json
{
  "clinic": {
    "id": 1,
    "name": "Central London Physiotherapy Clinic",
    "type": "physiotherapy",
    "location": "London, UK"
  },
  "pain_points": [
    {
      "pain_point": "Phone system / missed calls",
      "severity": "critical",
      "mentions": 8,
      "confidence": "high",
      "evidence": [
        {
          "id": 5001,
          "type": "review",
          "text": "Phone system is terrible. Always goes to voicemail.",
          "date": "2024-12-15",
          "source_url": "https://maps.google.com/..."
        }
      ]
    }
  ],
  "summary_stats": {
    "total_reviews": 35,
    "avg_rating": 3.2,
    "total_job_ads": 3,
    "data_period": "2024-01-01 to 2025-01-03"
  },
  "_audit_trail": {
    "generated_at": "2025-01-03T12:00:00Z",
    "data_sources": ["google_reviews", "indeed", "reed"],
    "confidence_level": "high"
  }
}
```

### 7.2 Integration with ManagementTeam

**Use Case:** Feed Pain Point Radar data into ManagementTeam's Demand Validation step

**Integration Pattern:**

```
Pain Point Radar DB
       │
       ├──▶ Export API (/api/pain-points)
       │
       └──▶ ManagementTeam Demand Validator
              │
              ├── Existing: Reddit/Twitter data
              ├── NEW: Pain Point Radar data
              └── Hybrid Analysis (passive + active)
```

**Code Integration:**

```python
# In ManagementTeam: src/analysis/demand_validator.py

class DemandValidator:
    def __init__(self):
        self.pain_radar_client = PainPointRadarClient()

    def validate_demand(self, idea_context: Dict) -> Dict:
        """
        Validate demand using BOTH social media AND Pain Point Radar.
        """
        # Existing: Social media scraping
        social_data = self._scrape_social_media(idea_context)

        # NEW: Query Pain Point Radar
        clinic_type = self._detect_clinic_type(idea_context)
        pain_radar_data = self.pain_radar_client.get_pain_points(
            clinic_type=clinic_type,
            country="UK",
            min_confidence="medium"
        )

        # Merge insights
        combined_insights = self._merge_insights(social_data, pain_radar_data)

        return {
            "validation_score": combined_insights['score'],
            "pain_points": combined_insights['pain_points'],
            "data_sources": {
                "social_media": social_data['_audit_trail'],
                "pain_point_radar": pain_radar_data['_audit_trail']
            },
            "_audit_trail": {
                "hybrid_approach": True,
                "data_freshness": "Pain Radar updated weekly"
            }
        }
```

---

## 8. KEYWORD AUTOMATION LOGIC

**See Section 4.3** for full details. Summary:

1. **Seed Keywords** (manual) → Initial set per clinic type
2. **Automated Expansion** (KeyBERT) → Extract from existing corpus
3. **Human Review** (Rob) → Approve/reject new keywords
4. **Feedback Loop** → Track hit rates, adjust weights

**Frequency:** Weekly keyword expansion, monthly review

---

## 9. INTEGRATION WITH MANAGEMENTTEAM

### 9.1 Integration Points

| Integration | Purpose | Implementation |
|-------------|---------|----------------|
| **Shared Database** | Unified data storage | Use Supabase (already integrated) |
| **API Endpoint** | Query pain points | FastAPI endpoint in orchestrator |
| **Checkpoint System** | Save radar state | Extend existing checkpoint system |
| **Transparency Config** | Unified settings | Add radar settings to `transparency_config.json` |

### 9.2 Shared Supabase Tables

**Extend existing Supabase schema:**

```sql
-- Add to Supabase (ManagementTeam already uses it)

CREATE TABLE pain_radar_clinics (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    clinic_type VARCHAR(50),
    country VARCHAR(50),
    -- ... (same as Postgres schema)
);

CREATE TABLE pain_radar_items (
    id SERIAL PRIMARY KEY,
    clinic_id INTEGER REFERENCES pain_radar_clinics(id),
    -- ... (same as Postgres schema)
);
```

**Alternative:** Keep Postgres separate, sync summaries to Supabase nightly

### 9.3 API Integration (FastAPI)

**Extend ManagementTeam orchestrator:**

```python
# In ManagementTeam: src/orchestrator/api.py

from fastapi import FastAPI, Query
from src.pain_radar.database import PainRadarDB

app = FastAPI()

@app.get("/pain-radar/clinics")
def get_clinics(
    clinic_type: str = Query(None),
    country: str = Query("UK"),
    limit: int = 100
):
    """
    Get list of clinics from Pain Point Radar.
    """
    db = PainRadarDB()
    clinics = db.get_clinics(
        clinic_type=clinic_type,
        country=country,
        limit=limit
    )

    return {
        "clinics": clinics,
        "count": len(clinics),
        "_audit_trail": {
            "query_params": {
                "clinic_type": clinic_type,
                "country": country
            }
        }
    }

@app.get("/pain-radar/pain-points/{clinic_id}")
def get_pain_points(clinic_id: int):
    """
    Get pain points for a specific clinic.
    """
    db = PainRadarDB()

    reviews = db.get_reviews(clinic_id)
    jobs = db.get_job_ads(clinic_id)
    metadata = db.get_derived_metadata(clinic_id, metric_type="top_pain_points")

    return {
        "clinic_id": clinic_id,
        "pain_points": metadata['metric_value']['pain_points'],
        "evidence": {
            "reviews_count": len(reviews),
            "job_ads_count": len(jobs)
        },
        "_audit_trail": metadata['_audit_trail']
    }
```

---

## 10. RISK ASSESSMENT & HARDENING

### 10.1 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Scraper Blocking** | HIGH | HIGH | Residential proxies, rate limiting, user-agent rotation |
| **API Rate Limits** | MEDIUM | MEDIUM | Exponential backoff, queue-based scraping |
| **Data Quality Issues** | MEDIUM | HIGH | Validation rules, deduplication, manual sampling |
| **Database Scaling** | LOW | MEDIUM | Start with Postgres, migrate to TimescaleDB if needed |
| **Maintenance Burden** | MEDIUM | MEDIUM | Use proven templates, avoid custom scrapers |

### 10.2 Legal/Compliance Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **robots.txt Violations** | LOW | HIGH | Mandatory robots.txt checks before scraping |
| **GDPR (Personal Data)** | MEDIUM | HIGH | Don't scrape PII (emails, phone), only public business data |
| **Terms of Service** | MEDIUM | MEDIUM | Review ToS for Google, Indeed, etc. Use official APIs where available |

### 10.3 Hardening Checklist

- [ ] **Proxy Rotation:** Implement residential proxy pool (Bright Data or ScraperAPI)
- [ ] **Rate Limiting:** Enforce delays (6-10 sec between requests)
- [ ] **User-Agent Rotation:** Randomize browser fingerprints
- [ ] **Error Handling:** Graceful degradation, retry logic (max 3 retries)
- [ ] **Monitoring:** Sentry or CloudWatch for error tracking
- [ ] **Backup Strategy:** Daily Postgres backups to S3
- [ ] **Data Retention:** Delete raw_items older than 12 months (GDPR compliance)
- [ ] **Access Control:** Database credentials in environment variables only

---

## 11. TECHNOLOGY RECOMMENDATIONS

### 11.1 Final Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **Database** | PostgreSQL 15+ | Relational queries, JSONB for flexibility, mature ecosystem |
| **Scraping (Static)** | Scrapy 2.11+ | Battle-tested, fast, extensive middleware |
| **Scraping (JavaScript)** | Playwright | Headless browser, better than Selenium for modern sites |
| **Orchestration** | Prefect 2.x | Python-native, easier than Airflow for our scale |
| **Proxies** | Bright Data or ScraperAPI | Residential proxies, auto-rotation, 99.9% uptime |
| **Language** | Python 3.11+ | Consistency with ManagementTeam, rich ecosystem |
| **Hosting** | AWS EC2 (t3.medium) | Cost-effective, scalable, Postgres RDS integration |
| **Monitoring** | Sentry (errors) + CloudWatch (metrics) | Free tier sufficient for MVP |

### 11.2 Cost Estimate (Monthly)

| Item | Cost (USD) |
|------|-----------|
| AWS EC2 (t3.medium, 24/7) | $30 |
| AWS RDS Postgres (db.t3.micro) | $15 |
| Bright Data Proxies (10 GB) | $50 |
| Sentry (free tier) | $0 |
| Total | **$95/month** |

**Phase 2:** Add $20/month for larger EC2 instance if scraping increases

---

## 12. IMPLEMENTATION PHASES

### Phase 1: MVP (4-6 weeks)

**Goal:** Prove concept with single clinic type (physiotherapy, UK only)

**Deliverables:**
1. Postgres database (clinics, sources, raw_items tables)
2. Google Reviews scraper (Playwright)
3. Indeed scraper (Scrapy)
4. Physio First directory scraper
5. Basic Prefect flow (daily job scraping, weekly reviews)
6. CSV export
7. Manual testing with 50 clinics

**Success Criteria:**
- 50 clinics in database
- 500+ reviews scraped
- 100+ job ads scraped
- <5% error rate

### Phase 2: Expansion (4-6 weeks)

**Goal:** Scale to all clinic types + Ireland

**Deliverables:**
1. Add counselling, chiropody scrapers
2. Add BACP, College of Podiatry directories
3. Add Reed, IrishJobs scrapers
4. Implement deduplication
5. Add `derived_metadata` table + pain point analysis
6. Perplexity export
7. ManagementTeam API integration

**Success Criteria:**
- 800+ clinics across all types
- 3000+ reviews
- 500+ job ads
- Perplexity exports generated weekly

### Phase 3: Automation & Active Research (2-4 weeks)

**Goal:** Full autopilot + active research capabilities

**Deliverables:**
1. Clinic website scraping
2. Keyword automation (KeyBERT)
3. Active research templates (LinkedIn posts, surveys)
4. Monitoring dashboard
5. Automated alerts (Slack/email)
6. Documentation

**Success Criteria:**
- 100% uptime for scheduled jobs
- Keyword hit rate >80%
- Active research playbook documented

---

## APPENDICES

### A. Sample Queries

**Query 1: Top Pain Points Across All Clinics**
```sql
SELECT
    r.keywords,
    COUNT(*) AS mentions,
    AVG(r.sentiment_score) AS avg_sentiment,
    STRING_AGG(DISTINCT r.text_excerpt, ' | ') AS examples
FROM raw_items r
WHERE r.item_type = 'review'
  AND r.urgency_detected IN ('critical', 'high')
GROUP BY r.keywords
ORDER BY mentions DESC
LIMIT 10;
```

**Query 2: Clinics with Highest Hiring Frequency**
```sql
SELECT
    c.name,
    c.clinic_type,
    COUNT(r.id) AS job_ads_count,
    AVG(EXTRACT(EPOCH FROM (CURRENT_DATE - r.scraped_at::DATE)) / 86400) AS avg_days_since_posting
FROM clinics c
JOIN raw_items r ON c.id = r.clinic_id
WHERE r.item_type = 'job_ad'
  AND r.scraped_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY c.id, c.name, c.clinic_type
HAVING COUNT(r.id) >= 3
ORDER BY job_ads_count DESC;
```

### B. Glossary

- **ICP:** Ideal Customer Profile
- **DAG:** Directed Acyclic Graph (workflow structure)
- **ETL:** Extract, Transform, Load
- **JSONB:** PostgreSQL's JSON binary format
- **Playwright:** Headless browser automation tool
- **Scrapy:** Python web scraping framework
- **Prefect:** Workflow orchestration platform

---

## NEXT STEPS

1. **Rob Reviews This Document** → Approve/request changes
2. **Create DATABASE_SCHEMA.md** → Full SQL DDL + migration scripts
3. **Create IMPLEMENTATION_ROADMAP.md** → Detailed task breakdown with effort estimates
4. **Create INTEGRATION_GUIDE.md** → Developer documentation for extending system
5. **Create project-specific CLAUDE.md** → AI assistant guidelines for this module
6. **Begin Phase 1 Implementation** → After all docs approved

---

**Document Version:** 1.0
**Status:** Awaiting Founder Approval
**Next Review:** After Rob's feedback
