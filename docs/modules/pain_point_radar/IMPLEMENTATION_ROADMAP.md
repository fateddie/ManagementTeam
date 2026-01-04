# 🚀 Pain Point Radar - Implementation Roadmap

**Project:** Private Clinic Pain Point Monitoring System
**Version:** 1.0
**Author:** System Architect (Claude)
**Date:** 2025-01-03
**Status:** Design Phase - Awaiting Approval

---

## TABLE OF CONTENTS

1. [Overview](#overview)
2. [Phase 1: MVP (4-6 weeks)](#phase-1-mvp-4-6-weeks)
3. [Phase 2: Expansion (4-6 weeks)](#phase-2-expansion-4-6-weeks)
4. [Phase 3: Automation & Active Research (2-4 weeks)](#phase-3-automation--active-research-2-4-weeks)
5. [Dependencies & Prerequisites](#dependencies--prerequisites)
6. [Risk Mitigation](#risk-mitigation)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Plan](#deployment-plan)
9. [Success Metrics](#success-metrics)

---

## 1. OVERVIEW

### 1.1 Implementation Philosophy

**Incremental Value Delivery:** Each phase delivers working, valuable functionality
**Risk Reduction:** Validate assumptions early (scraper stability, data quality, proxy costs)
**Human-in-the-Loop:** Rob reviews and approves before each phase

### 1.2 Timeline Summary

```
┌──────────────┬──────────────┬────────────┐
│   Phase 1    │   Phase 2    │  Phase 3   │
│   (MVP)      │ (Expansion)  │ (Automation)│
│  4-6 weeks   │  4-6 weeks   │  2-4 weeks │
└──────────────┴──────────────┴────────────┘
   Jan-Feb         Mar-Apr        May-Jun
```

**Total Duration:** 10-16 weeks (2.5-4 months)

### 1.3 Resource Requirements

**Team:**
- Rob (Founder): Decision-maker, reviewer (2-4 hours/week)
- Claude (System Architect): Implementation (full-time equivalent)

**Infrastructure:**
- AWS EC2 t3.medium ($30/month)
- AWS RDS Postgres db.t3.micro ($15/month)
- Bright Data proxies ($50/month)
- **Total:** ~$95/month

---

## 2. PHASE 1: MVP (4-6 WEEKS)

### 2.1 Goals

**Primary:** Prove the concept works with ONE clinic type (physiotherapy, UK only)

**Success Criteria:**
- 50 clinics in database
- 500+ reviews scraped
- 100+ job ads scraped
- <5% scraping error rate
- CSV export functional

**Deliverables:**
1. Postgres database (core tables)
2. Google Reviews scraper (Playwright)
3. Indeed scraper (Scrapy)
4. Physio First directory scraper
5. Basic Prefect orchestration
6. CSV export functionality
7. Manual validation completed

### 2.2 Task Breakdown

#### Week 1: Infrastructure & Database Setup

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **1.1** Provision AWS EC2 (t3.medium) | 2h | Rob/Claude | AWS account | Running EC2 instance |
| **1.2** Provision AWS RDS Postgres | 2h | Rob/Claude | AWS account | Postgres database |
| **1.3** Configure security groups & VPC | 1h | Rob/Claude | EC2, RDS created | Network connectivity |
| **1.4** Install Python 3.11, dependencies | 1h | Claude | EC2 running | Python environment |
| **1.5** Create database schema | 2h | Claude | RDS ready | Tables created |
| **1.6** Write sample data insert scripts | 2h | Claude | Schema created | Test data available |
| **1.7** Test database connectivity | 1h | Claude | All above | Connection verified |

**Total:** 11 hours
**Deliverable:** Operational database with schema

---

#### Week 2: Directory Scraper (Clinic Discovery)

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **2.1** Research Physio First website structure | 2h | Claude | - | Scraping plan |
| **2.2** Implement Scrapy spider | 4h | Claude | Python env | Working scraper |
| **2.3** Add robots.txt compliance check | 1h | Claude | Scraper coded | Respectful scraping |
| **2.4** Implement deduplication logic | 2h | Claude | Scraper coded | No duplicate clinics |
| **2.5** Write clinic data to database | 2h | Claude | DB ready | Clinics in DB |
| **2.6** Manual validation (check 10 clinics) | 1h | Rob | Data scraped | Quality verified |
| **2.7** Run full scrape (target: 100 clinics) | 1h | Claude | Validation passed | 100 clinics in DB |

**Total:** 13 hours
**Deliverable:** 100 UK physiotherapy clinics in database

---

#### Week 3: Google Reviews Scraper

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **3.1** Setup Bright Data proxy account | 1h | Rob | Credit card | Proxy credentials |
| **3.2** Research Google Maps review structure | 3h | Claude | - | Scraping plan |
| **3.3** Implement Playwright scraper | 8h | Claude | Proxy ready | Working scraper |
| **3.4** Add rate limiting (6 sec delay) | 1h | Claude | Scraper coded | Respectful scraping |
| **3.5** Implement scroll-to-load logic | 2h | Claude | Scraper coded | Load all reviews |
| **3.6** Write review data to database | 2h | Claude | DB ready | Reviews in DB |
| **3.7** Test with 5 clinics manually | 2h | Claude | Scraper ready | Debugged |
| **3.8** Run scrape for 50 clinics | 3h | Claude | Tests passed | 500+ reviews |
| **3.9** Manual validation (check 20 reviews) | 1h | Rob | Data scraped | Quality verified |

**Total:** 23 hours
**Deliverable:** 500+ reviews from 50 clinics

---

#### Week 4: Indeed Job Scraper

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **4.1** Research Indeed UK structure | 2h | Claude | - | Scraping plan |
| **4.2** Implement Scrapy spider | 6h | Claude | Python env | Working scraper |
| **4.3** Add keyword logic (physiotherapist, receptionist) | 2h | Claude | Scraper coded | Targeted scraping |
| **4.4** Add location filtering (London, Manchester, etc.) | 1h | Claude | Keywords done | Geographic targeting |
| **4.5** Write job ad data to database | 2h | Claude | DB ready | Jobs in DB |
| **4.6** Test with manual search | 1h | Claude | Scraper ready | Debugged |
| **4.7** Run full scrape (target: 100+ ads) | 2h | Claude | Tests passed | 100+ job ads |
| **4.8** Manual validation (check 10 job ads) | 1h | Rob | Data scraped | Quality verified |

**Total:** 17 hours
**Deliverable:** 100+ job ads in database

---

#### Week 5: Orchestration & CSV Export

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **5.1** Install Prefect 2.x | 1h | Claude | EC2 ready | Prefect installed |
| **5.2** Create directory scrape flow | 3h | Claude | Scrapers ready | Weekly flow |
| **5.3** Create reviews scrape flow | 3h | Claude | Reviews scraper | Weekly flow |
| **5.4** Create jobs scrape flow | 3h | Claude | Jobs scraper | Daily flow |
| **5.5** Add error handling & retries | 2h | Claude | Flows coded | Robust flows |
| **5.6** Schedule flows (cron) | 1h | Claude | Flows tested | Automated |
| **5.7** Implement CSV export function | 3h | Claude | DB populated | CSV export working |
| **5.8** Test export with 500 rows | 1h | Claude | Export coded | Validated |
| **5.9** Document how to run manually | 1h | Claude | All tested | Documentation |

**Total:** 18 hours
**Deliverable:** Automated scraping + CSV export

---

#### Week 6: Testing & Validation

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **6.1** End-to-end test (full workflow) | 4h | Claude | All components | System tested |
| **6.2** Manual review of data quality | 3h | Rob | Data collected | Quality assessed |
| **6.3** Fix identified issues | 4h | Claude | Issues found | Bugs fixed |
| **6.4** Document known limitations | 2h | Claude | Testing complete | Honest assessment |
| **6.5** Rob review & approval meeting | 1h | Rob | Documentation ready | Go/No-go decision |

**Total:** 14 hours
**Deliverable:** Working MVP + approval for Phase 2

---

### 2.3 Phase 1 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Google blocks scraper | HIGH | HIGH | Use residential proxies, rate limiting, retry logic |
| Low data quality | MEDIUM | HIGH | Manual validation at each step, adjust scrapers |
| Scraper maintenance burden | MEDIUM | MEDIUM | Use proven templates, document thoroughly |
| Proxy costs higher than expected | LOW | MEDIUM | Monitor usage, set budget alerts |

---

## 3. PHASE 2: EXPANSION (4-6 WEEKS)

### 3.1 Goals

**Primary:** Scale to all clinic types + Ireland + add analysis

**Success Criteria:**
- 800+ clinics (all 4 types)
- 3000+ reviews
- 500+ job ads
- Deduplication <5% duplicates
- Pain point analysis working
- Perplexity export functional

**Deliverables:**
1. Counselling & chiropody scrapers
2. Ireland data sources (IrishJobs, Irish directories)
3. Reed job board scraper
4. Deduplication pipeline
5. Pain point analysis algorithm
6. Perplexity export
7. ManagementTeam API integration

### 3.2 Task Breakdown

#### Week 7-8: New Clinic Types & Directories

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **7.1** Add BACP directory scraper (counselling) | 6h | Claude | Phase 1 complete | Counselling clinics |
| **7.2** Add College of Podiatry scraper | 6h | Claude | Phase 1 complete | Chiropody clinics |
| **7.3** Add Irish directories (ISCP) | 6h | Claude | Phase 1 complete | Ireland clinics |
| **7.4** Run discovery scrapes (target: 800 clinics) | 3h | Claude | Scrapers ready | 800+ clinics |
| **7.5** Manual validation (sample 30 clinics) | 2h | Rob | Data scraped | Quality verified |
| **7.6** Update Google Reviews scraper for all types | 3h | Claude | New clinics added | Reviews for all |
| **7.7** Run review scraping (target: 3000 reviews) | 8h | Claude | Scraper updated | 3000+ reviews |

**Total:** 34 hours (2 weeks)
**Deliverable:** 800 clinics, 3000 reviews across all types

---

#### Week 9: Additional Job Boards

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **9.1** Implement Reed scraper (UK) | 6h | Claude | Indeed working | Reed scraper |
| **9.2** Implement IrishJobs scraper | 6h | Claude | Indeed working | IrishJobs scraper |
| **9.3** Add keywords for counselling/chiropody | 2h | Claude | Scrapers ready | Targeted keywords |
| **9.4** Run job scrapes (target: 500+ ads) | 3h | Claude | All tested | 500+ job ads |
| **9.5** Manual validation (sample 20 ads) | 1h | Rob | Data scraped | Quality verified |

**Total:** 18 hours
**Deliverable:** 500+ job ads from 3 job boards

---

#### Week 10: Deduplication & Data Quality

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **10.1** Implement content hash generation | 3h | Claude | DB ready | Hash function |
| **10.2** Add hash column to raw_items table | 1h | Claude | Migration ready | Schema updated |
| **10.3** Backfill hashes for existing data | 2h | Claude | Function ready | All hashed |
| **10.4** Implement fuzzy matching (RapidFuzz) | 4h | Claude | Hashing done | Fuzzy dedup |
| **10.5** Create deduplication flow (Prefect) | 3h | Claude | Logic ready | Daily dedup job |
| **10.6** Run dedup on full dataset | 1h | Claude | Flow tested | Duplicates marked |
| **10.7** Measure duplicate rate | 1h | Claude | Dedup complete | <5% verified |

**Total:** 15 hours
**Deliverable:** Deduplication pipeline with <5% duplicate rate

---

#### Week 11: Pain Point Analysis

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **11.1** Design pain point detection algorithm | 3h | Claude | Data available | Algorithm spec |
| **11.2** Implement keyword extraction (KeyBERT) | 4h | Claude | Algorithm designed | Keyword extraction |
| **11.3** Implement urgency detection (regex + sentiment) | 4h | Claude | Keywords working | Urgency scoring |
| **11.4** Write aggregation logic (top pain points) | 4h | Claude | Detection ready | Aggregation |
| **11.5** Store in derived_metadata table | 2h | Claude | DB ready | Insights saved |
| **11.6** Create pain point analysis flow (Prefect) | 3h | Claude | Logic coded | Weekly analysis |
| **11.7** Run analysis on all clinics | 2h | Claude | Flow tested | Pain points identified |
| **11.8** Manual review of top 10 pain points | 2h | Rob | Analysis complete | Quality verified |

**Total:** 24 hours
**Deliverable:** Automated pain point detection

---

#### Week 12: Exports & Integration

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **12.1** Design Perplexity export format | 2h | Claude | Pain points ready | Export spec |
| **12.2** Implement Perplexity Markdown export | 4h | Claude | Spec ready | Export function |
| **12.3** Test export with 10 clinics | 1h | Claude | Function coded | Validated |
| **12.4** Design ManagementTeam API endpoints | 2h | Claude | Both systems understood | API spec |
| **12.5** Implement FastAPI endpoints | 4h | Claude | Spec approved | API working |
| **12.6** Test integration with ManagementTeam | 2h | Claude | API deployed | Integration tested |
| **12.7** Document API usage | 2h | Claude | Testing complete | Documentation |
| **12.8** Rob review & approval | 1h | Rob | All tested | Go/No-go for Phase 3 |

**Total:** 18 hours
**Deliverable:** Perplexity export + ManagementTeam integration

---

### 3.3 Phase 2 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data volume overwhelms system | MEDIUM | MEDIUM | Implement partitioning, monitor performance |
| Pain point algorithm low quality | HIGH | HIGH | Manual validation, iterative refinement |
| API integration breaks existing system | LOW | HIGH | Thorough testing, staging environment |

---

## 4. PHASE 3: AUTOMATION & ACTIVE RESEARCH (2-4 WEEKS)

### 4.1 Goals

**Primary:** Full autopilot + active research capabilities

**Success Criteria:**
- 99% scheduled job success rate
- Keyword hit rate >80%
- Active research playbook documented
- Monitoring dashboard operational
- 100% uptime for 1 week

**Deliverables:**
1. Clinic website scraping
2. Keyword automation (KeyBERT weekly updates)
3. Active research templates
4. Monitoring dashboard
5. Automated alerts
6. Complete documentation

### 4.2 Task Breakdown

#### Week 13: Website Scraping

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **13.1** Research website scraping patterns | 3h | Claude | Clinic URLs available | Scraping plan |
| **13.2** Implement Playwright website crawler | 8h | Claude | Plan ready | Website scraper |
| **13.3** Add robots.txt compliance | 1h | Claude | Scraper coded | Respectful scraping |
| **13.4** Extract services, pricing, team size | 4h | Claude | Crawler working | Data extraction |
| **13.5** Detect booking systems (Cliniko, etc.) | 3h | Claude | Extraction working | Technology detection |
| **13.6** Test with 20 clinic websites | 2h | Claude | All coded | Debugged |
| **13.7** Run full scrape (800 websites) | 4h | Claude | Tests passed | Website data |
| **13.8** Manual validation (sample 10 sites) | 1h | Rob | Data scraped | Quality verified |

**Total:** 26 hours
**Deliverable:** Technology stack data for 800 clinics

---

#### Week 14: Keyword Automation

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **14.1** Implement KeyBERT keyword expansion | 4h | Claude | Existing keywords | Expansion function |
| **14.2** Create weekly keyword review report | 3h | Claude | Expansion working | Markdown report |
| **14.3** Add keyword approval workflow | 2h | Claude | Report generated | Human-in-loop |
| **14.4** Test with 1 week of data | 2h | Claude | All coded | Validated |
| **14.5** Schedule weekly keyword job | 1h | Claude | Tests passed | Automated |
| **14.6** Rob reviews first keyword report | 1h | Rob | Report generated | Feedback provided |

**Total:** 13 hours
**Deliverable:** Automated keyword expansion with human approval

---

#### Week 15: Active Research

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **15.1** Design LinkedIn post template | 2h | Claude | Pain points identified | Template |
| **15.2** Design survey template (TypeForm) | 2h | Claude | Pain points identified | Survey |
| **15.3** Create active research database table | 1h | Claude | DB ready | Schema extended |
| **15.4** Document LinkedIn campaign process | 3h | Claude | Template ready | Playbook |
| **15.5** Document survey campaign process | 3h | Claude | Survey ready | Playbook |
| **15.6** Rob reviews playbooks | 1h | Rob | Docs complete | Approved |

**Total:** 12 hours
**Deliverable:** Active research playbooks (manual execution)

---

#### Week 16: Monitoring & Documentation

| Task | Effort | Owner | Dependencies | Deliverable |
|------|--------|-------|--------------|-------------|
| **16.1** Setup Sentry error tracking | 2h | Claude | Sentry account | Errors monitored |
| **16.2** Add logging to all scrapers | 3h | Claude | Sentry ready | Comprehensive logs |
| **16.3** Create monitoring dashboard (queries) | 4h | Claude | Logs available | Dashboard |
| **16.4** Setup email alerts for failures | 2h | Claude | Sentry configured | Alerts working |
| **16.5** Write operator documentation | 4h | Claude | System stable | Ops docs |
| **16.6** Write developer documentation | 4h | Claude | System stable | Dev docs |
| **16.7** Create troubleshooting guide | 3h | Claude | Common issues known | Troubleshooting guide |
| **16.8** Final Rob review & handoff | 2h | Rob | All docs ready | Project complete |

**Total:** 24 hours
**Deliverable:** Production-ready system with full documentation

---

### 4.3 Phase 3 Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Website scraping unreliable | HIGH | MEDIUM | Make website data optional, focus on reviews/jobs |
| Active research low response rate | MEDIUM | LOW | Set expectations, iterate on templates |
| Documentation insufficient | LOW | HIGH | Ongoing documentation throughout project |

---

## 5. DEPENDENCIES & PREREQUISITES

### 5.1 External Dependencies

| Dependency | Phase | Critical? | Alternative |
|------------|-------|-----------|-------------|
| AWS Account | 1 | YES | Local Postgres (slower, not production-ready) |
| Bright Data Proxies | 1 | YES | ScraperAPI, Oxylabs (similar cost) |
| Prefect Cloud (optional) | 1 | NO | Self-hosted Prefect (free) |
| Sentry Account | 3 | NO | CloudWatch Logs (AWS-native) |

### 5.2 Internal Dependencies (ManagementTeam)

| Dependency | Phase | Required For | Status |
|------------|-------|--------------|--------|
| Supabase Integration | 2 | Shared memory | ✅ Already implemented |
| FastAPI Orchestrator | 2 | API endpoints | ✅ Already running |
| Transparency Config | 2 | Unified settings | ✅ Already exists |

---

## 6. RISK MITIGATION

### 6.1 Technical Risks

**Risk 1: Google Blocks Scrapers**

- **Mitigation:** Residential proxies, user-agent rotation, rate limiting
- **Fallback:** Switch to Trustpilot reviews (less data, but accessible)
- **Early Detection:** Monitor error rate in Week 3

**Risk 2: Data Quality Issues**

- **Mitigation:** Manual validation at each step, iterative refinement
- **Fallback:** Reduce scope (fewer clinics, focus on quality)
- **Early Detection:** Rob's manual review in Week 6

**Risk 3: Maintenance Burden**

- **Mitigation:** Use proven templates, thorough documentation
- **Fallback:** Reduce scraping frequency (weekly → monthly)
- **Early Detection:** Track time spent on scraper fixes

### 6.2 Business Risks

**Risk 1: Insufficient Pain Point Signal**

- **Mitigation:** Start with high-volume clinic type (physiotherapy)
- **Fallback:** Add more data sources (Trustpilot, clinic forums)
- **Early Detection:** Analyze Phase 1 data quality

**Risk 2: Cost Overruns**

- **Mitigation:** Set AWS budget alerts ($150/month), monitor proxy usage
- **Fallback:** Reduce scraping frequency, optimize proxy usage
- **Early Detection:** Weekly cost review

---

## 7. TESTING STRATEGY

### 7.1 Unit Tests

**Coverage:** All scraper functions, database queries, analysis algorithms

**Tools:** pytest

**Example:**
```python
# tests/test_google_reviews_scraper.py

def test_extract_review():
    """Test review extraction from HTML element."""
    scraper = GoogleReviewsScraper()
    mock_element = create_mock_review_element()
    result = scraper._extract_review(mock_element)

    assert result['content']['rating'] == 4
    assert 'phone' in result['keywords']
```

**Schedule:** Run before each deployment

---

### 7.2 Integration Tests

**Coverage:** End-to-end workflows (scrape → store → analyze → export)

**Tools:** pytest + Docker Compose (local Postgres)

**Example:**
```python
# tests/integration/test_full_workflow.py

def test_reviews_scraping_workflow(db):
    """Test complete reviews workflow."""
    # Setup
    clinic = db.create_test_clinic()

    # Scrape
    scraper = GoogleReviewsScraper()
    reviews = scraper.scrape(clinic.name, clinic.google_maps_url)

    # Verify storage
    stored = db.get_reviews(clinic.id)
    assert len(stored) > 0

    # Verify analysis
    pain_points = analyze_pain_points(clinic.id)
    assert len(pain_points) > 0
```

**Schedule:** Run weekly during development

---

### 7.3 Manual Validation

**Coverage:** Data quality, pain point relevance, export formatting

**Process:**
1. Sample 10-30 records per data source
2. Rob manually reviews for accuracy
3. Flag issues for refinement
4. Re-test after fixes

**Schedule:** End of each week during Phase 1-2

---

## 8. DEPLOYMENT PLAN

### 8.1 Phase 1 Deployment

**Environment:** AWS EC2 + RDS (production from day 1)

**Steps:**
1. Provision infrastructure (Week 1)
2. Deploy database schema (Week 1)
3. Deploy scrapers as systemd services (Week 5)
4. Deploy Prefect flows (Week 5)
5. Schedule cron jobs (Week 5)

**Rollback:** Restore from daily backup

---

### 8.2 Phase 2 Deployment

**Environment:** Same as Phase 1

**Steps:**
1. Run schema migrations (Week 10)
2. Deploy new scrapers (Weeks 7-9)
3. Deploy analysis pipeline (Week 11)
4. Deploy API endpoints (Week 12)

**Rollback:** Database migration rollback + code revert

---

### 8.3 Phase 3 Deployment

**Environment:** Same as Phase 1-2

**Steps:**
1. Deploy website scraper (Week 13)
2. Deploy keyword automation (Week 14)
3. Deploy monitoring (Week 16)

**Rollback:** Disable new scrapers, revert to Phase 2

---

## 9. SUCCESS METRICS

### 9.1 Phase 1 Metrics

| Metric | Target | Measured |
|--------|--------|----------|
| Clinics in database | 50+ | TBD |
| Reviews collected | 500+ | TBD |
| Job ads collected | 100+ | TBD |
| Scraping error rate | <5% | TBD |
| Data validation pass rate | >95% | TBD |

---

### 9.2 Phase 2 Metrics

| Metric | Target | Measured |
|--------|--------|----------|
| Clinics (all types) | 800+ | TBD |
| Reviews collected | 3000+ | TBD |
| Job ads collected | 500+ | TBD |
| Duplicate rate | <5% | TBD |
| Pain point quality (manual review) | >80% relevant | TBD |

---

### 9.3 Phase 3 Metrics

| Metric | Target | Measured |
|--------|--------|----------|
| Scheduled job success rate | 99%+ | TBD |
| Keyword hit rate | >80% | TBD |
| Uptime (1 week continuous) | 100% | TBD |
| Documentation completeness | 100% (all sections) | TBD |

---

## APPENDICES

### A. Effort Summary

| Phase | Total Hours | Duration | FTE |
|-------|-------------|----------|-----|
| Phase 1 | 96 hours | 4-6 weeks | 0.6 FTE |
| Phase 2 | 109 hours | 4-6 weeks | 0.7 FTE |
| Phase 3 | 75 hours | 2-4 weeks | 0.9 FTE |
| **Total** | **280 hours** | **10-16 weeks** | **0.7 FTE avg** |

**Note:** FTE based on 40-hour work week

---

### B. Weekly Schedule Example

**Phase 1, Week 3 (Google Reviews Scraper):**

| Day | Task | Hours |
|-----|------|-------|
| Monday | Setup Bright Data proxies | 1h |
| Monday | Research Google Maps structure | 3h |
| Tuesday | Implement Playwright scraper (part 1) | 4h |
| Wednesday | Implement Playwright scraper (part 2) | 4h |
| Thursday | Add rate limiting & scroll logic | 3h |
| Friday | Write to database + testing | 4h |
| Weekend | Run 50-clinic scrape + manual validation | 4h |

**Total:** 23 hours

---

### C. Checklist: Ready for Phase 2?

Before starting Phase 2, verify:

- [ ] 50+ clinics in database (physiotherapy, UK)
- [ ] 500+ reviews scraped with <5% error rate
- [ ] 100+ job ads scraped with <5% error rate
- [ ] CSV export tested and functional
- [ ] Prefect flows running on schedule
- [ ] Manual validation passed (Rob approved)
- [ ] No critical bugs identified
- [ ] Infrastructure costs within budget ($95/month)
- [ ] Documentation up-to-date

---

### D. Glossary

- **FTE:** Full-Time Equivalent (40 hours/week)
- **MVP:** Minimum Viable Product
- **DDL:** Data Definition Language (SQL schema)
- **Scraper:** Automated tool to extract data from websites

---

**Document Version:** 1.0
**Status:** Awaiting Founder Approval
**Next:** Create INTEGRATION_GUIDE.md
