# 🔌 Pain Point Radar - Integration Guide

**Project:** Private Clinic Pain Point Monitoring System
**Version:** 1.0
**Author:** System Architect (Claude)
**Date:** 2025-01-03
**Status:** Design Phase - Awaiting Approval

---

## TABLE OF CONTENTS

1. [Integration Overview](#integration-overview)
2. [ManagementTeam Integration](#managementteam-integration)
3. [API Reference](#api-reference)
4. [Adding New Data Sources](#adding-new-data-sources)
5. [Extending the Schema](#extending-the-schema)
6. [Custom Analysis Algorithms](#custom-analysis-algorithms)
7. [Export Formats](#export-formats)
8. [Troubleshooting](#troubleshooting)

---

## 1. INTEGRATION OVERVIEW

### 1.1 Integration Architecture

```
┌──────────────────────────────────────────────────────┐
│         MANAGEMENT TEAM SYSTEM                       │
│  (Decision Support for Business Idea Validation)     │
└────────────────┬─────────────────────────────────────┘
                 │
                 │ REST API
                 │
┌────────────────▼─────────────────────────────────────┐
│         PAIN POINT RADAR MODULE                      │
│  (Continuous Monitoring of Clinic Pain Points)       │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Scrapers   │  │   Postgres   │  │  Exports   │ │
│  │   (Passive   │─▶│   Database   │─▶│ (Perplexity│ │
│  │    Research) │  │              │  │  CSV, JSON) │ │
│  └──────────────┘  └──────────────┘  └────────────┘ │
└──────────────────────────────────────────────────────┘
                 │
                 │ Future: Shared Supabase Memory
                 │
┌────────────────▼─────────────────────────────────────┐
│              SUPABASE (LONG-TERM MEMORY)             │
│  - Business ideas                                    │
│  - Pain point insights                               │
│  - User decisions                                    │
└──────────────────────────────────────────────────────┘
```

### 1.2 Integration Points

| Integration | Type | Direction | Purpose |
|-------------|------|-----------|---------|
| **REST API** | Synchronous | ManagementTeam → Radar | Query pain points for validation |
| **Supabase Sync** | Asynchronous | Radar → Supabase | Share insights across systems |
| **Checkpoint System** | File-based | Bidirectional | State persistence |
| **Transparency Config** | Shared Config | Bidirectional | Unified settings |

---

## 2. MANAGEMENTTEAM INTEGRATION

### 2.1 Use Case: Enhance Demand Validation

**Current Workflow (ManagementTeam):**
1. User provides business idea
2. System scrapes Reddit/Twitter for pain points (one-time)
3. Validates demand based on social media signals
4. Provides go/no-go recommendation

**Enhanced Workflow (with Pain Point Radar):**
1. User provides business idea (e.g., "AI receptionist for physiotherapists")
2. System queries Pain Point Radar for relevant clinics + data
3. Combines social media data + Pain Point Radar data
4. Provides stronger validation with real-world evidence
5. Shows example clinics with pain points

### 2.2 Integration Code Example

**In ManagementTeam: `src/analysis/demand_validator.py`**

```python
# src/analysis/demand_validator.py

import requests
from typing import Dict, List

class DemandValidator:
    """
    Validates business idea demand using multiple data sources.

    Now includes Pain Point Radar integration for real-world clinic data.
    """

    def __init__(self):
        self.pain_radar_api_url = "http://localhost:8000/pain-radar"
        self.use_pain_radar = self._check_pain_radar_available()

    def _check_pain_radar_available(self) -> bool:
        """Check if Pain Point Radar API is accessible."""
        try:
            response = requests.get(f"{self.pain_radar_api_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def validate_demand(self, idea_context: Dict) -> Dict:
        """
        Validate demand using BOTH social media AND Pain Point Radar.

        Args:
            idea_context: {
                "idea_title": "AI Receptionist for Physiotherapists",
                "target_customer": "physiotherapy clinics",
                "pain_point": "phone system / missed calls"
            }

        Returns:
            Validation results with hybrid data sources
        """
        # EXISTING: Social media scraping
        social_data = self._scrape_social_media(idea_context)

        # NEW: Pain Point Radar data
        if self.use_pain_radar:
            radar_data = self._query_pain_radar(idea_context)
        else:
            radar_data = None

        # Merge insights
        combined_insights = self._merge_insights(social_data, radar_data)

        return {
            "validation_score": combined_insights['score'],
            "pain_points": combined_insights['pain_points'],
            "example_clinics": combined_insights.get('clinics', []),
            "data_sources": {
                "social_media": social_data['_audit_trail'],
                "pain_point_radar": radar_data['_audit_trail'] if radar_data else None
            },
            "_audit_trail": {
                "hybrid_approach": self.use_pain_radar,
                "data_freshness": "Pain Radar updated weekly" if self.use_pain_radar else "N/A"
            }
        }

    def _query_pain_radar(self, idea_context: Dict) -> Dict:
        """
        Query Pain Point Radar for relevant clinic data.

        Args:
            idea_context: Business idea context

        Returns:
            Pain point data from radar
        """
        # Detect clinic type from idea
        clinic_type = self._detect_clinic_type(idea_context['target_customer'])

        # Detect pain point keywords
        pain_keywords = self._extract_keywords(idea_context['pain_point'])

        # Query Pain Radar API
        response = requests.post(
            f"{self.pain_radar_api_url}/search-pain-points",
            json={
                "clinic_type": clinic_type,
                "keywords": pain_keywords,
                "country": "UK",  # or from idea_context
                "min_confidence": "medium",
                "limit": 10
            },
            timeout=30
        )

        if response.status_code != 200:
            return None

        return response.json()

    def _detect_clinic_type(self, target_customer: str) -> str:
        """
        Map target customer to clinic type.

        Args:
            target_customer: e.g., "physiotherapy clinics", "therapists"

        Returns:
            Clinic type (physiotherapy, counselling, chiropody, multi_practitioner)
        """
        target_lower = target_customer.lower()

        if any(word in target_lower for word in ["physio", "physiotherap"]):
            return "physiotherapy"
        elif any(word in target_lower for word in ["counsel", "therap", "psycholog"]):
            return "counselling"
        elif any(word in target_lower for word in ["chirop", "podiatr", "foot"]):
            return "chiropody"
        else:
            return "multi_practitioner"

    def _extract_keywords(self, pain_point_text: str) -> List[str]:
        """
        Extract keywords from pain point description.

        Args:
            pain_point_text: e.g., "phone system / missed calls"

        Returns:
            List of keywords
        """
        # Simple split on common delimiters
        keywords = pain_point_text.lower().replace("/", " ").replace(",", " ").split()
        return [kw.strip() for kw in keywords if len(kw) > 2]

    def _merge_insights(self, social_data: Dict, radar_data: Dict) -> Dict:
        """
        Merge social media and Pain Point Radar insights.

        Args:
            social_data: Reddit/Twitter data
            radar_data: Pain Point Radar data (or None)

        Returns:
            Combined insights with higher confidence
        """
        # Base score from social media
        score = social_data.get('validation_score', 0)

        # Pain points from social media
        pain_points = social_data.get('pain_points', [])

        # Example clinics (new field)
        clinics = []

        # If radar data available, boost score and add evidence
        if radar_data and radar_data.get('matches'):
            # Boost score by 10-20 points (real-world evidence)
            radar_matches = radar_data['matches']
            boost = min(20, len(radar_matches) * 2)  # Max 20 point boost
            score += boost

            # Add radar pain points
            for match in radar_matches:
                pain_points.append({
                    "pain_point": match['pain_point'],
                    "mentions": match['mentions'],
                    "source": "pain_point_radar",
                    "confidence": match['confidence'],
                    "evidence": match.get('example_quotes', [])
                })

                # Add example clinic
                clinics.append({
                    "name": match['clinic_name'],
                    "type": match['clinic_type'],
                    "location": match['location'],
                    "pain_point_severity": match['severity']
                })

        return {
            "score": min(100, score),  # Cap at 100
            "pain_points": pain_points,
            "clinics": clinics
        }
```

### 2.3 Integration Testing

**Test Case: Validate "AI Receptionist for Physiotherapists"**

```python
# tests/integration/test_pain_radar_integration.py

import pytest
from src.analysis.demand_validator import DemandValidator

def test_pain_radar_integration():
    """Test ManagementTeam + Pain Point Radar integration."""

    validator = DemandValidator()

    idea_context = {
        "idea_title": "AI Receptionist for Physiotherapists",
        "target_customer": "physiotherapy clinics",
        "pain_point": "phone system / missed calls"
    }

    result = validator.validate_demand(idea_context)

    # Verify hybrid data sources
    assert result['data_sources']['social_media'] is not None
    assert result['data_sources']['pain_point_radar'] is not None

    # Verify pain points include radar data
    radar_pain_points = [
        pp for pp in result['pain_points']
        if pp['source'] == 'pain_point_radar'
    ]
    assert len(radar_pain_points) > 0

    # Verify example clinics provided
    assert len(result['example_clinics']) > 0
    assert result['example_clinics'][0]['type'] == 'physiotherapy'

    # Verify score boosted by radar data
    assert result['validation_score'] >= 60  # Higher due to real-world evidence
```

---

## 3. API REFERENCE

### 3.1 API Endpoints

**Base URL:** `http://localhost:8000/pain-radar`

All endpoints return JSON with `_audit_trail` for transparency.

---

#### Endpoint 1: Health Check

**GET** `/pain-radar/health`

**Description:** Check if Pain Point Radar API is running

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "v1.0"
}
```

---

#### Endpoint 2: List Clinics

**GET** `/pain-radar/clinics`

**Description:** Get list of all clinics

**Query Parameters:**
- `clinic_type` (optional): physiotherapy, counselling, chiropody, multi_practitioner
- `country` (optional): UK, Ireland
- `region` (optional): London, Dublin, Manchester, etc.
- `status` (optional): active, closed, monitoring_paused
- `limit` (optional): Max results (default 100)
- `offset` (optional): Pagination offset (default 0)

**Example Request:**
```bash
GET /pain-radar/clinics?clinic_type=physiotherapy&country=UK&region=London&limit=10
```

**Response:**
```json
{
  "clinics": [
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
      "status": "active",
      "metadata": {
        "team_size": 5,
        "services": ["sports physio", "massage"],
        "booking_system": "Cliniko"
      }
    }
  ],
  "count": 10,
  "total": 87,
  "_audit_trail": {
    "query_params": {
      "clinic_type": "physiotherapy",
      "country": "UK",
      "region": "London"
    },
    "generated_at": "2025-01-03T12:00:00Z"
  }
}
```

---

#### Endpoint 3: Get Pain Points for Clinic

**GET** `/pain-radar/pain-points/{clinic_id}`

**Description:** Get analyzed pain points for a specific clinic

**Path Parameters:**
- `clinic_id`: Clinic ID (integer)

**Example Request:**
```bash
GET /pain-radar/pain-points/1
```

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
      "mentions": 8,
      "severity": "critical",
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

---

#### Endpoint 4: Search Pain Points

**POST** `/pain-radar/search-pain-points`

**Description:** Search for clinics with specific pain points

**Request Body:**
```json
{
  "clinic_type": "physiotherapy",
  "keywords": ["phone", "voicemail", "calls"],
  "country": "UK",
  "min_confidence": "medium",
  "limit": 10
}
```

**Response:**
```json
{
  "matches": [
    {
      "clinic_id": 1,
      "clinic_name": "Central London Physiotherapy Clinic",
      "clinic_type": "physiotherapy",
      "location": "London, UK",
      "pain_point": "Phone system / missed calls",
      "mentions": 8,
      "severity": "critical",
      "confidence": "high",
      "example_quotes": [
        "Phone system is terrible. Always goes to voicemail.",
        "Can never get through on the phone."
      ]
    }
  ],
  "total_matches": 12,
  "_audit_trail": {
    "search_params": {
      "clinic_type": "physiotherapy",
      "keywords": ["phone", "voicemail", "calls"],
      "country": "UK",
      "min_confidence": "medium"
    },
    "generated_at": "2025-01-03T12:00:00Z"
  }
}
```

---

#### Endpoint 5: Export to Perplexity

**GET** `/pain-radar/export/perplexity/{clinic_id}`

**Description:** Generate Perplexity-friendly markdown export for a clinic

**Path Parameters:**
- `clinic_id`: Clinic ID (integer)

**Query Parameters:**
- `format` (optional): markdown (default), text

**Example Request:**
```bash
GET /pain-radar/export/perplexity/1?format=markdown
```

**Response:**
```markdown
# Pain Point Analysis Export
**Clinic:** Central London Physiotherapy Clinic
**Generated:** 2025-01-03

## Reviews Summary (35 reviews)
**Average Rating:** 3.2/5
**Sentiment:** Mixed (60% negative)

### Top Pain Points:
1. **Phone System / Missed Calls** (8 mentions, critical)
   - "Phone system is terrible. Always goes to voicemail."
   - Evidence: Review IDs [5001, 5003, 5007...]

...
```

---

### 3.2 API Implementation

**In ManagementTeam: `src/orchestrator/api.py`**

```python
# src/orchestrator/api.py

from fastapi import FastAPI, Query, HTTPException
from typing import Optional, List
from pydantic import BaseModel

# Import Pain Radar database client
from src.pain_radar.database import PainRadarDB

app = FastAPI()

# ============================================================
# PAIN POINT RADAR API ENDPOINTS
# ============================================================

@app.get("/pain-radar/health")
def health_check():
    """Health check for Pain Point Radar API."""
    db = PainRadarDB()
    try:
        db.test_connection()
        return {
            "status": "healthy",
            "database": "connected",
            "version": "v1.0"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


@app.get("/pain-radar/clinics")
def get_clinics(
    clinic_type: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    status: str = "active",
    limit: int = 100,
    offset: int = 0
):
    """
    Get list of clinics with optional filters.
    """
    db = PainRadarDB()

    filters = {}
    if clinic_type:
        filters['clinic_type'] = clinic_type
    if country:
        filters['country'] = country
    if region:
        filters['region'] = region
    filters['status'] = status

    clinics = db.get_clinics(filters=filters, limit=limit, offset=offset)
    total = db.count_clinics(filters=filters)

    return {
        "clinics": clinics,
        "count": len(clinics),
        "total": total,
        "_audit_trail": {
            "query_params": filters,
            "generated_at": datetime.utcnow().isoformat()
        }
    }


@app.get("/pain-radar/pain-points/{clinic_id}")
def get_pain_points(clinic_id: int):
    """
    Get pain points for a specific clinic.
    """
    db = PainRadarDB()

    # Get clinic info
    clinic = db.get_clinic(clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    # Get pain point analysis
    metadata = db.get_derived_metadata(
        clinic_id=clinic_id,
        metric_type="top_pain_points"
    )

    if not metadata:
        # No analysis available yet
        return {
            "clinic": {
                "id": clinic['id'],
                "name": clinic['name'],
                "type": clinic['clinic_type'],
                "location": f"{clinic['region']}, {clinic['country']}"
            },
            "pain_points": [],
            "summary_stats": {},
            "message": "No pain point analysis available yet (data collection in progress)"
        }

    # Get summary stats
    reviews = db.get_reviews(clinic_id)
    jobs = db.get_job_ads(clinic_id)

    return {
        "clinic": {
            "id": clinic['id'],
            "name": clinic['name'],
            "type": clinic['clinic_type'],
            "location": f"{clinic['region']}, {clinic['country']}"
        },
        "pain_points": metadata['metric_value']['pain_points'],
        "summary_stats": {
            "total_reviews": len(reviews),
            "avg_rating": metadata.get('avg_rating', None),
            "total_job_ads": len(jobs),
            "data_period": metadata['metadata'].get('date_range', 'N/A')
        },
        "_audit_trail": metadata.get('_audit_trail', {})
    }


class SearchRequest(BaseModel):
    """Request model for pain point search."""
    clinic_type: str
    keywords: List[str]
    country: str = "UK"
    min_confidence: str = "medium"
    limit: int = 10


@app.post("/pain-radar/search-pain-points")
def search_pain_points(request: SearchRequest):
    """
    Search for clinics with specific pain points.
    """
    db = PainRadarDB()

    # Search raw_items for matching keywords
    matches = db.search_pain_points(
        clinic_type=request.clinic_type,
        keywords=request.keywords,
        country=request.country,
        min_confidence=request.min_confidence,
        limit=request.limit
    )

    return {
        "matches": matches,
        "total_matches": len(matches),
        "_audit_trail": {
            "search_params": request.dict(),
            "generated_at": datetime.utcnow().isoformat()
        }
    }


@app.get("/pain-radar/export/perplexity/{clinic_id}")
def export_perplexity(clinic_id: int, format: str = "markdown"):
    """
    Generate Perplexity export for a clinic.
    """
    from src.pain_radar.exports import generate_perplexity_export

    try:
        export_content = generate_perplexity_export(clinic_id, format=format)
        return {"content": export_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
```

---

## 4. ADDING NEW DATA SOURCES

### 4.1 Data Source Checklist

Before adding a new data source:

- [ ] Verify source is legal to scrape (check ToS, robots.txt)
- [ ] Determine scraper type needed (Scrapy vs Playwright)
- [ ] Design content JSONB structure
- [ ] Plan deduplication strategy
- [ ] Estimate scraping frequency
- [ ] Calculate cost impact (proxies, API fees)

### 4.2 Example: Adding Trustpilot Reviews

**Step 1: Create Scraper Module**

```bash
mkdir -p src/scrapers/trustpilot
touch src/scrapers/trustpilot/__init__.py
touch src/scrapers/trustpilot/scraper.py
touch src/scrapers/trustpilot/config.yaml
```

**Step 2: Implement Scraper**

```python
# src/scrapers/trustpilot/scraper.py

from src.scrapers.base_scraper import BaseScraper
from playwright.sync_api import sync_playwright

class TrustpilotScraper(BaseScraper):
    """
    Scrape Trustpilot reviews for clinics.
    """

    def __init__(self):
        super().__init__(scraper_name="trustpilot", version="v1.0.0")

    def scrape(self, clinic_name: str, trustpilot_url: str, max_reviews: int = 50) -> List[Dict]:
        """
        Scrape reviews from Trustpilot.

        Args:
            clinic_name: Name of clinic
            trustpilot_url: Trustpilot business page URL
            max_reviews: Max reviews to scrape

        Returns:
            List of review dicts
        """
        # Implementation similar to Google Reviews scraper
        # ...

        return reviews
```

**Step 3: Update Database**

```sql
-- Add trustpilot to source_type enum
ALTER TABLE sources DROP CONSTRAINT sources_source_type_check;
ALTER TABLE sources ADD CONSTRAINT sources_source_type_check
    CHECK (source_type IN ('google_review', 'job_ad', 'website_content', 'directory_listing', 'trustpilot_review', 'manual_entry'));
```

**Step 4: Add to Orchestration**

```python
# src/orchestration/flows/trustpilot_flow.py

from prefect import flow, task
from src.scrapers.trustpilot.scraper import TrustpilotScraper

@flow(name="scrape_trustpilot_reviews")
def scrape_trustpilot_flow():
    """Weekly flow to scrape Trustpilot reviews."""
    # Implementation
    pass
```

**Step 5: Schedule**

```python
# Schedule weekly scraping (Saturday 4 AM)
scrape_trustpilot_flow.serve(
    name="trustpilot-weekly",
    cron="0 4 * * 6"
)
```

---

## 5. EXTENDING THE SCHEMA

### 5.1 Adding New Columns

**Use Case:** Track clinic response rate to reviews

**Step 1: Create Migration**

```sql
-- migrations/003_add_response_rate.sql

BEGIN;

ALTER TABLE clinics ADD COLUMN IF NOT EXISTS review_response_rate DECIMAL(5, 2);

COMMENT ON COLUMN clinics.review_response_rate IS 'Percentage of reviews with clinic response (0-100)';

INSERT INTO schema_versions (version, applied_at, description) VALUES
('v1.2', CURRENT_TIMESTAMP, 'Added review_response_rate to clinics');

COMMIT;
```

**Step 2: Backfill Data**

```sql
-- Calculate response rate for existing clinics
UPDATE clinics c
SET review_response_rate = (
    SELECT ROUND(
        100.0 * COUNT(*) FILTER (WHERE r.content->>'clinic_response' IS NOT NULL) / COUNT(*),
        2
    )
    FROM raw_items r
    WHERE r.clinic_id = c.id
      AND r.item_type = 'review'
);
```

### 5.2 Adding New Derived Metrics

**Use Case:** Calculate hiring velocity (ads per month trend)

**Step 1: Implement Calculation**

```python
# src/analysis/hiring_velocity.py

def calculate_hiring_velocity(clinic_id: int, db_connection) -> Dict:
    """
    Calculate hiring velocity (trend over 6 months).

    Args:
        clinic_id: Clinic ID
        db_connection: Database connection

    Returns:
        Metric dict with trend analysis
    """
    # Query job ads for last 6 months
    query = """
        SELECT
            DATE_TRUNC('month', scraped_at) AS month,
            COUNT(*) AS ads_count
        FROM raw_items
        WHERE clinic_id = %s
          AND item_type = 'job_ad'
          AND scraped_at >= CURRENT_DATE - INTERVAL '6 months'
        GROUP BY month
        ORDER BY month;
    """

    result = db_connection.execute(query, (clinic_id,))
    monthly_ads = [{"month": row[0].isoformat(), "count": row[1]} for row in result]

    # Calculate trend (increasing/decreasing/stable)
    if len(monthly_ads) >= 3:
        recent_avg = sum([m['count'] for m in monthly_ads[-3:]]) / 3
        older_avg = sum([m['count'] for m in monthly_ads[:3]]) / 3

        if recent_avg > older_avg * 1.2:
            trend = "increasing"
        elif recent_avg < older_avg * 0.8:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    return {
        "metric_type": "hiring_velocity",
        "metric_value": {
            "monthly_ads": monthly_ads,
            "trend": trend,
            "avg_ads_per_month": round(sum([m['count'] for m in monthly_ads]) / len(monthly_ads), 2)
        },
        "confidence_level": "high" if len(monthly_ads) >= 6 else "medium"
    }
```

**Step 2: Store in derived_metadata**

```python
# Store result
db.insert_derived_metadata(clinic_id, metric_result)
```

---

## 6. CUSTOM ANALYSIS ALGORITHMS

### 6.1 Pain Point Detection Algorithm

**Current Algorithm:** Keyword frequency + urgency weighting

**Customization Example:** Add sentiment-weighted scoring

```python
# src/analysis/pain_point_detector.py

class PainPointDetector:
    """
    Detect and rank pain points from raw reviews and job ads.
    """

    def detect_pain_points(self, clinic_id: int) -> Dict:
        """
        Detect pain points with sentiment weighting.

        Args:
            clinic_id: Clinic ID

        Returns:
            Pain points ranked by severity
        """
        db = PostgresClient()

        # Get all reviews and job ads
        items = db.query("""
            SELECT
                text_excerpt,
                keywords,
                urgency_detected,
                sentiment_score
            FROM raw_items
            WHERE clinic_id = %s
              AND item_type IN ('review', 'job_ad')
        """, (clinic_id,))

        # Count keyword mentions with weighting
        keyword_scores = {}

        for item in items:
            urgency_weight = self._get_urgency_weight(item['urgency_detected'])
            sentiment_weight = abs(item['sentiment_score'] or 0)  # Negative = pain

            for keyword in item['keywords'] or []:
                # Score = urgency * sentiment intensity
                score = urgency_weight * (1 + sentiment_weight)

                if keyword not in keyword_scores:
                    keyword_scores[keyword] = {
                        "mentions": 0,
                        "total_score": 0,
                        "examples": []
                    }

                keyword_scores[keyword]['mentions'] += 1
                keyword_scores[keyword]['total_score'] += score
                keyword_scores[keyword]['examples'].append(item['text_excerpt'])

        # Rank by total score
        ranked = sorted(
            keyword_scores.items(),
            key=lambda x: x[1]['total_score'],
            reverse=True
        )

        # Format as pain points
        pain_points = []
        for keyword, data in ranked[:10]:  # Top 10
            pain_points.append({
                "pain_point": keyword.replace("_", " ").title(),
                "mentions": data['mentions'],
                "severity": self._calculate_severity(data['total_score']),
                "example_quotes": data['examples'][:3]
            })

        return {
            "pain_points": pain_points,
            "confidence": "high" if len(items) >= 20 else "medium"
        }

    def _get_urgency_weight(self, urgency: str) -> float:
        """Map urgency to numeric weight."""
        weights = {
            "critical": 3.0,
            "high": 2.0,
            "medium": 1.0,
            "low": 0.5
        }
        return weights.get(urgency, 1.0)

    def _calculate_severity(self, total_score: float) -> str:
        """Map total score to severity label."""
        if total_score >= 20:
            return "critical"
        elif total_score >= 10:
            return "high"
        elif total_score >= 5:
            return "medium"
        else:
            return "low"
```

---

## 7. EXPORT FORMATS

### 7.1 Custom Export Format

**Example:** Export for Tableau BI Tool

```python
# src/exports/tableau_export.py

import pandas as pd

def export_for_tableau(output_path: str = "tableau_export.csv"):
    """
    Export Pain Point Radar data in Tableau-friendly format.

    Args:
        output_path: Output CSV path

    Returns:
        Path to generated file
    """
    db = PostgresClient()

    query = """
        SELECT
            c.id AS clinic_id,
            c.name AS clinic_name,
            c.clinic_type,
            c.country,
            c.region,
            r.item_type,
            r.text_excerpt,
            r.sentiment_score,
            r.urgency_detected,
            r.scraped_at,
            d.metric_value->>'pain_points'->0->>'pain_point' AS top_pain_point
        FROM clinics c
        LEFT JOIN raw_items r ON c.id = r.clinic_id
        LEFT JOIN derived_metadata d ON c.id = d.clinic_id AND d.metric_type = 'top_pain_points'
        WHERE c.status = 'active'
    """

    df = pd.read_sql(query, db.connection)

    # Format dates
    df['scraped_date'] = pd.to_datetime(df['scraped_at']).dt.date

    # Export
    df.to_csv(output_path, index=False)

    return output_path
```

---

## 8. TROUBLESHOOTING

### 8.1 Common Issues

**Issue 1: API Returns 503 (Service Unavailable)**

**Cause:** Database connection failed

**Solution:**
```bash
# Check database status
psql -U postgres -d pain_point_radar -c "SELECT 1;"

# Restart database if needed
sudo systemctl restart postgresql
```

---

**Issue 2: No Pain Points Returned for Clinic**

**Cause:** Analysis not run yet or insufficient data

**Solution:**
```python
# Manually trigger analysis
from src.analysis.pain_point_detector import PainPointDetector

detector = PainPointDetector()
result = detector.detect_pain_points(clinic_id=1)
```

---

**Issue 3: Scraper Error Rate >10%**

**Cause:** Website structure changed or proxy issues

**Solution:**
```bash
# Check scraper logs
tail -f /var/log/pain_radar/scrapers.log

# Test scraper manually
python -m src.scrapers.google_reviews.scraper --test
```

---

### 8.2 Debugging Tools

**Database Query Tool:**
```bash
# Connect to database
psql -U postgres -d pain_point_radar

# Check recent scrapes
SELECT * FROM sources ORDER BY scraped_at DESC LIMIT 10;

# Check error rate
SELECT
    source_type,
    COUNT(*) AS total,
    SUM(CASE WHEN scrape_success THEN 0 ELSE 1 END) AS errors,
    ROUND(100.0 * SUM(CASE WHEN scrape_success THEN 0 ELSE 1 END) / COUNT(*), 2) AS error_rate
FROM sources
WHERE scraped_at >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY source_type;
```

**API Test Script:**
```python
# test_api.py

import requests

BASE_URL = "http://localhost:8000/pain-radar"

# Test health
response = requests.get(f"{BASE_URL}/health")
print("Health:", response.json())

# Test clinics list
response = requests.get(f"{BASE_URL}/clinics?limit=5")
print("Clinics:", response.json()['count'])

# Test pain points
response = requests.get(f"{BASE_URL}/pain-points/1")
print("Pain Points:", len(response.json()['pain_points']))
```

---

**Document Version:** 1.0
**Status:** Awaiting Founder Approval
**Next:** Create project-specific CLAUDE.md
