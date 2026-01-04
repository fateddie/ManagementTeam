# 🧠 Pain Point Radar - Claude Instructions

**Module:** Pain Point Radar (Clinic Pain Point Monitoring)
**Version:** 1.0
**Author:** System Architect (Claude) + Rob (Founder)
**Date:** 2025-01-03
**Status:** Design Phase - Awaiting Approval

---

## 📚 INHERITANCE

**This file EXTENDS the main ManagementTeam Claude instructions.**

**Primary Reference:** `/docs/CLAUDE.md` (1,022 lines)
**Secondary Reference:** `/docs/system/claude.md` (102 lines)

**READ THOSE FIRST.** This file adds Pain Point Radar-specific rules.

---

## 🎯 MODULE-SPECIFIC ROLE

You are implementing a **web scraping and data monitoring system** that:
- Collects data from public websites (reviews, job ads, directories)
- Stores in structured database (Postgres)
- Analyzes for pain point patterns
- Exports for external consumption (Perplexity, BI tools, ManagementTeam)

**Key Difference from Main System:**
- **ManagementTeam:** One-time analysis, human-in-loop at every step
- **Pain Point Radar:** Continuous monitoring, automated pipelines, human reviews periodically

**Your responsibilities:**
1. Implement scrapers that are **respectful and compliant** (robots.txt, rate limits)
2. Store data with **full transparency** (source URLs, timestamps, versions)
3. Design **maintainable pipelines** (proven templates, not custom hacks)
4. Enable **human oversight** (manual validation, keyword approval, alerts)

---

## 🚨 MANDATORY RULES (NEVER VIOLATE)

### 1. ETHICAL SCRAPING

```python
# ❌ BAD - Aggressive scraping
def scrape_all_reviews(clinic_url):
    while True:  # No rate limiting!
        reviews = fetch_page(clinic_url)
        # ...

# ✅ GOOD - Respectful scraping
def scrape_reviews(clinic_url):
    # Check robots.txt FIRST
    if not is_allowed_by_robots_txt(clinic_url):
        logger.warning(f"Scraping not allowed: {clinic_url}")
        return []

    reviews = []
    for page in range(max_pages):
        # Rate limiting: 6 sec delay + random jitter
        time.sleep(6 + random.uniform(0, 2))

        try:
            page_reviews = fetch_page(clinic_url, page)
            reviews.extend(page_reviews)
        except RateLimitError:
            # Exponential backoff
            time.sleep(60)
            continue

    return reviews
```

**Rules:**
- ALWAYS check `robots.txt` before scraping
- ALWAYS implement rate limiting (minimum 5-10 sec between requests)
- ALWAYS use proxies for high-volume scraping
- NEVER scrape personal data (PII) - only public business info
- NEVER bypass authentication or paywalls

---

### 2. SOURCE TRACKING (TRANSPARENCY)

```python
# ❌ BAD - No audit trail
def save_review(review_text, rating):
    db.insert("INSERT INTO reviews VALUES (%s, %s)", (review_text, rating))

# ✅ GOOD - Full audit trail
def save_review(review_data, source_url, scraper_version):
    # Create source record
    source_record = {
        "source_type": "google_review",
        "source_name": "Google Maps Reviews",
        "source_url": source_url,
        "scraped_at": datetime.utcnow().isoformat(),
        "scraper_version": scraper_version,
        "scrape_success": True,
        "metadata": {
            "reviews_collected": 1,
            "rate_limit_hit": False
        }
    }
    source_id = db.insert_source(source_record)

    # Create raw_item record
    raw_item = {
        "clinic_id": review_data['clinic_id'],
        "source_id": source_id,
        "item_type": "review",
        "content": review_data,
        "text_excerpt": review_data['text'],
        "scraped_at": datetime.utcnow().isoformat(),
        "metadata": {}
    }
    db.insert_raw_item(raw_item)
```

**Every scraped item MUST include:**
- `source_url`: Where it came from
- `scraped_at`: When it was collected
- `scraper_version`: Which version of scraper was used
- `source_id`: Link to sources table (audit trail)

**Why:** Rob must be able to trace any data point back to its source 6 months later.

---

### 3. GRACEFUL DEGRADATION

```python
# ❌ BAD - Crashes entire pipeline
def scrape_all_clinics(clinics):
    for clinic in clinics:
        reviews = scrape_reviews(clinic.google_maps_url)  # Crash if one fails!
        save_reviews(reviews)

# ✅ GOOD - Continues despite failures
def scrape_all_clinics(clinics):
    success_count = 0
    error_count = 0

    for clinic in clinics:
        try:
            reviews = scrape_reviews(clinic.google_maps_url)
            save_reviews(reviews)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to scrape clinic {clinic.id}: {e}")
            error_count += 1

            # Log error to database
            log_scraping_error(clinic.id, str(e))

            # Continue with next clinic
            continue

    logger.info(f"Scraping complete: {success_count} success, {error_count} errors")

    # Alert if error rate too high
    if error_count / len(clinics) > 0.1:  # >10% error rate
        send_alert_to_rob(f"High error rate: {error_count}/{len(clinics)}")
```

**Rules:**
- ONE scraper failure should NOT stop entire pipeline
- Log all errors to database (for analysis)
- Send alerts if error rate >10%
- Implement retry logic (max 3 attempts with exponential backoff)

---

### 4. HUMAN-IN-THE-LOOP (VALIDATION)

```python
# ❌ BAD - Auto-adds keywords with no review
def update_keywords():
    new_keywords = keybert.extract_keywords(corpus, top_n=50)
    # Auto-add to production
    db.execute("INSERT INTO keywords VALUES (%s)", new_keywords)

# ✅ GOOD - Human approval required
def update_keywords():
    new_keywords = keybert.extract_keywords(corpus, top_n=50)

    # Generate review report
    report = generate_keyword_review_report(new_keywords)
    save_report("keywords_review_2025_01_03.md", report)

    # Email Rob for approval
    send_email(
        to="rob@example.com",
        subject="New Keywords Detected - Review Required",
        body=f"Found {len(new_keywords)} new keywords. Review: {report_url}"
    )

    # DO NOT auto-add to production
    # Wait for Rob's approval (manual process)
```

**Rules:**
- Keyword changes require Rob's approval
- New data sources require Rob's approval
- Algorithm changes require validation before production
- Weekly data quality reports sent to Rob

---

### 5. CONFIGURATION OVER HARD-CODING

```python
# ❌ BAD - Hard-coded
RATE_LIMIT_DELAY = 6  # seconds
MAX_REVIEWS = 50
URGENCY_WEIGHTS = {"critical": 3, "high": 2}

# ✅ GOOD - Configurable
class ScraperConfig:
    def __init__(self, config_path="config/scraper_config.json"):
        self.config = json.load(open(config_path))

    @property
    def rate_limit_delay(self):
        return self.config['scraping']['rate_limit_delay_sec']

    @property
    def max_reviews_per_clinic(self):
        return self.config['scraping']['max_reviews']

    @property
    def urgency_weights(self):
        return self.config['analysis']['urgency_weights']
```

**Config File:** `config/scraper_config.json`
```json
{
  "scraping": {
    "rate_limit_delay_sec": 6,
    "max_reviews": 50,
    "proxy_rotation": true,
    "user_agent_rotation": true
  },
  "analysis": {
    "urgency_weights": {
      "critical": 3.0,
      "high": 2.0,
      "medium": 1.0,
      "low": 0.5
    },
    "min_confidence_mentions": 5
  }
}
```

---

## 📋 IMPLEMENTATION CHECKLIST

Before marking ANY scraper as complete:

### Scraper Functionality
- [ ] robots.txt check implemented
- [ ] Rate limiting (min 5 sec delay)
- [ ] Proxy rotation configured
- [ ] Error handling (graceful degradation)
- [ ] Retry logic (max 3 attempts)
- [ ] Deduplication (hash-based)

### Transparency
- [ ] Source URL recorded for every item
- [ ] Scraper version tracked
- [ ] Timestamp in ISO format
- [ ] Metadata includes scraping stats
- [ ] Audit trail complete

### Data Quality
- [ ] Manual validation completed (sample 20+ items)
- [ ] Duplicate rate <5%
- [ ] Error rate <5%
- [ ] Data matches expected schema

### Documentation
- [ ] Scraper documented in README
- [ ] Example output provided
- [ ] Troubleshooting guide written
- [ ] Config options explained

---

## 🎨 CODE PATTERNS

### Pattern 1: Respectful Scraper

```python
# src/scrapers/base_scraper.py

import time
import random
import requests
from urllib.robotparser import RobotFileParser

class BaseScraper(ABC):
    """Base class for all scrapers with ethical scraping built-in."""

    def __init__(self, scraper_name: str, version: str):
        self.scraper_name = scraper_name
        self.version = version
        self.config = ScraperConfig()

    def is_allowed_by_robots_txt(self, url: str) -> bool:
        """Check if scraping is allowed by robots.txt."""
        rp = RobotFileParser()
        rp.set_url(f"{self._get_domain(url)}/robots.txt")
        try:
            rp.read()
            return rp.can_fetch(self.config.user_agent, url)
        except:
            # If robots.txt unavailable, be conservative
            self.logger.warning(f"Could not read robots.txt for {url}")
            return True  # Assume allowed if file not found

    def rate_limited_request(self, url: str, **kwargs):
        """Make HTTP request with rate limiting."""
        # Delay before request
        delay = self.config.rate_limit_delay + random.uniform(0, 2)
        time.sleep(delay)

        # Make request with timeout
        response = requests.get(url, timeout=30, **kwargs)

        # Check for rate limiting response
        if response.status_code == 429:
            # Exponential backoff
            backoff = 60 * (2 ** self.retry_count)
            self.logger.warning(f"Rate limited. Waiting {backoff} seconds...")
            time.sleep(backoff)
            raise RateLimitError("Rate limit hit")

        return response
```

---

### Pattern 2: Transparent Data Storage

```python
# src/database/postgres_client.py

class PostgresClient:
    """Database client with transparency built-in."""

    def insert_raw_item(self, item: Dict) -> int:
        """
        Insert raw item with automatic audit trail.

        Args:
            item: Item dict with required fields

        Returns:
            Inserted item ID
        """
        # Validate required fields
        required = ['clinic_id', 'source_id', 'item_type', 'content']
        for field in required:
            if field not in item:
                raise ValueError(f"Missing required field: {field}")

        # Generate content hash for deduplication
        content_hash = hashlib.sha256(
            json.dumps(item['content'], sort_keys=True).encode()
        ).hexdigest()

        # Check for duplicate
        existing = self.query(
            "SELECT id FROM raw_items WHERE content_hash = %s",
            (content_hash,)
        )
        if existing:
            self.logger.info(f"Duplicate detected, skipping insert")
            return existing[0]['id']

        # Insert with full metadata
        query = """
            INSERT INTO raw_items (
                clinic_id, source_id, item_type, content, text_excerpt,
                content_hash, scraped_at, metadata
            ) VALUES (
                %(clinic_id)s, %(source_id)s, %(item_type)s, %(content)s,
                %(text_excerpt)s, %(content_hash)s, %(scraped_at)s, %(metadata)s
            )
            RETURNING id
        """

        params = {
            **item,
            'content_hash': content_hash,
            'scraped_at': item.get('scraped_at', datetime.utcnow().isoformat()),
            'metadata': item.get('metadata', {})
        }

        result = self.execute(query, params)
        return result[0]['id']
```

---

### Pattern 3: Human-Approved Automation

```python
# src/analysis/keyword_updater.py

class KeywordUpdater:
    """Automated keyword discovery with human approval."""

    def generate_keyword_suggestions(self) -> Dict:
        """
        Generate new keyword suggestions using KeyBERT.

        Returns:
            Report dict for human review
        """
        # Get existing keywords
        existing = db.query("SELECT keyword FROM keywords")
        existing_set = set([k['keyword'] for k in existing])

        # Extract new candidates from recent data
        recent_items = db.query("""
            SELECT text_excerpt FROM raw_items
            WHERE scraped_at >= CURRENT_DATE - INTERVAL '7 days'
        """)

        corpus = " ".join([item['text_excerpt'] for item in recent_items])

        # Use KeyBERT to extract candidates
        kw_model = KeyBERT(model='all-MiniLM-L6-v2')
        candidates = kw_model.extract_keywords(
            corpus,
            keyphrase_ngram_range=(1, 3),
            top_n=50
        )

        # Filter out existing keywords
        new_keywords = [
            kw for kw, score in candidates
            if kw not in existing_set
        ]

        # Generate review report
        report = self._generate_markdown_report(new_keywords, candidates)

        # Save for Rob's review
        report_path = f"reports/keywords_review_{date.today()}.md"
        with open(report_path, 'w') as f:
            f.write(report)

        # Email Rob
        send_email(
            to="rob@example.com",
            subject=f"Weekly Keyword Review - {len(new_keywords)} New Candidates",
            body=f"Review report: {report_path}\n\nApprove/reject by editing keywords_approved.txt"
        )

        return {
            "new_keywords": new_keywords,
            "report_path": report_path,
            "approval_required": True
        }

    def _generate_markdown_report(self, new_keywords: List[str], scores: List) -> str:
        """Generate human-readable review report."""
        report = f"""# Keyword Review Report
**Date:** {date.today()}
**New Candidates:** {len(new_keywords)}

## Instructions
Review each keyword below. To approve, add to `keywords_approved.txt`.

## New Keywords

"""
        for kw, score in scores[:20]:
            if kw in new_keywords:
                report += f"- **{kw}** (relevance score: {score:.2f})\n"

        return report
```

---

## 🚫 ANTI-PATTERNS (DO NOT DO THIS)

### Anti-Pattern 1: Aggressive Scraping

```python
# ❌ BAD
def scrape_all_reviews():
    for clinic in clinics:
        for page in range(100):  # No delay!
            fetch_page(clinic.url, page)
```

**Why Bad:** Will get IP blocked, disrespectful to website owner

---

### Anti-Pattern 2: Losing Source References

```python
# ❌ BAD
def process_reviews(reviews):
    for review in reviews:
        # Process and save, but lose source URL!
        db.insert_review(review['text'], review['rating'])
```

**Why Bad:** Can't verify data later, no audit trail

---

### Anti-Pattern 3: Auto-Execution Without Validation

```python
# ❌ BAD
def update_pain_point_algorithm(new_algorithm):
    # Deploy to production immediately!
    deploy_to_production(new_algorithm)
```

**Why Bad:** No human validation, could produce low-quality insights

---

## 📚 DECISION FRAMEWORK

### When to Use Scrapy vs Playwright

| Criteria | Scrapy | Playwright |
|----------|--------|------------|
| **JavaScript Required?** | No | Yes |
| **Speed** | Fast | Slower |
| **Complexity** | Low | Medium |
| **Example Use Case** | Job boards, directories | Google Reviews, clinic websites |

**Decision Rule:**
1. Try Scrapy first (simpler, faster)
2. If content doesn't load → Use Playwright

---

### When to Alert Rob

| Scenario | Alert? | Rationale |
|----------|--------|-----------|
| Error rate >10% | YES | Something broken |
| New data source found | YES | Requires approval |
| Duplicate rate >5% | YES | Data quality issue |
| Individual scraper fails | NO | Logged, will retry |
| Keyword suggestions ready | YES | Requires review |

---

## ✅ EXAMPLE: FULL SCRAPER IMPLEMENTATION

**See:** `TECHNICAL_DESIGN.md` Section 5.4 for complete Google Reviews scraper example

**Key Features:**
- Extends `BaseScraper` for consistency
- robots.txt check
- Rate limiting (6 sec + jitter)
- Retry logic
- Source tracking
- Error logging

---

## 🎯 SUCCESS METRICS

You're following these guidelines when:

1. **Rob can trace any data point to its source**
   - Click on review ID → See source URL, scrape timestamp, scraper version

2. **System degrades gracefully**
   - One scraper fails → Others continue
   - Proxy blocked → Switches to backup proxy

3. **Rob is notified of important changes**
   - Weekly keyword suggestions email
   - Alerts for high error rates

4. **Scrapers are maintainable**
   - New developer can understand code in <30 minutes
   - Config changes don't require code changes

---

## 📞 WHEN UNCERTAIN

If you're unsure about a scraping decision, ask:

1. **Is this respectful?** (robots.txt, rate limits)
2. **Can Rob verify this later?** (source tracking)
3. **Will this scale?** (proven templates, not hacks)
4. **Is Rob in the loop?** (approvals, alerts)

**If any answer is unclear, err on the side of MORE caution and transparency.**

---

## 🔗 RELATED DOCUMENTATION

- **Main Claude Instructions:** `/docs/CLAUDE.md`
- **Technical Design:** `TECHNICAL_DESIGN.md` (this directory)
- **Database Schema:** `DATABASE_SCHEMA.md` (this directory)
- **Implementation Roadmap:** `IMPLEMENTATION_ROADMAP.md` (this directory)
- **Integration Guide:** `INTEGRATION_GUIDE.md` (this directory)

---

## 📜 VERSION HISTORY

| Version | Date | Author | Notes |
|----------|------|---------|-------|
| 1.0 | 2025-01-03 | System Architect (Claude) | Initial Pain Point Radar Claude instructions |

---

**Remember: You scrape ethically. You track transparently. Rob approves major changes.**
