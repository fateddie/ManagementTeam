# 🗺️ Trading Copilot — Comprehensive Project Roadmap

**Project:** Swing FX Trading Assistant (Trading Copilot)
**Author:** Rob Freyne
**Date:** 2025-10-11
**Date Updated:** 2025-10-11
**Version:** 2.1.0-alpha
**Status:** Planning Complete — Ready for M1

---

## 🎯 Project Vision

Build a professional-grade AI Trading Copilot that provides deep market insight, performance analytics, and structured top-down analysis for discretionary swing trading. The system uses modular agents with persistent memory, structured workflows, and human-in-the-loop decision support.

**Key Innovation:** Risk Sentiment Engine (RSE) provides cross-asset risk regime scoring (-100 to +100) as foundational layer for all analysis agents.

**Two-Phase Approach:**
- **Phase 1 (MVP v2.1):** 7-agent analytics dashboard including RSE (15 days)
- **Phase 2 (Full System v3.0):** Voice interface + advanced agents (future)

---

## 📦 Phase 1: MVP — Core Analytics Platform (v2.1.0)

**Duration:** 15 days (Oct 14-28, 2025) — Extended by 1 day for RSE integration
**Goal:** Production-ready analytics dashboard with 7 agents (including RSE), Next.js UI, FastAPI backend
**Technology:** Interactive Brokers + Alpha Vantage + TradingView + Supabase + RSE (8-instrument cross-asset scoring)

###

 M1: Data Integration Layer (Days 1-3)

**Timeline:** Oct 14-16, 2025 (3 days)
**Status:** 🟡 Pending
**Dependencies:** None

#### Objectives
- Connect to Interactive Brokers TWS API for real trade data and positions
- Integrate Alpha Vantage for historical FX price data
- Embed TradingView widgets for chart visualization
- Implement Market Data Collector module with Supabase caching
- Secure API credentials with encryption

#### Deliverables
| File | Purpose |
|------|---------|
| `/src/services/ib_broker.py` | IBKR TWS API integration |
| `/src/services/alpha_vantage.py` | Historical data connector |
| `/backend/modules/market_data/collector.py` | Market Data Collector module |
| `/backend/db/schema.sql` | Supabase schema with market_data_cache table |
| `/tests/unit/test_market_data.py` | Unit tests for data collection |
| `/tests/integration/test_ib_connection.py` | IBKR connection integration test |
| `.env.example` | Template for API credentials |

#### Phase-Gate Criteria
- [ ] Real-time IBKR data fetched and cached successfully
- [ ] Alpha Vantage historical data retrieved for EUR/USD and GBP/USD
- [ ] TradingView widgets render in test environment
- [ ] Unit tests pass 100%
- [ ] Integration tests pass with 95%+ success rate
- [ ] Documentation updated (README + CHANGELOG)
- [ ] API credentials secured and encrypted
- [ ] Founder (Rob) approval

#### Success Metrics
- Data sync success rate: ≥ 95%
- API response time: < 3s per pair
- TradingView widget load time: < 2s

---

### M2: 7-Agent Analytics Engine including RSE (Days 4-9)

**Timeline:** Oct 17-22, 2025 (6 days) — Extended by 1 day for RSE
**Status:** 🟡 Pending
**Dependencies:** M1 complete

#### Objectives
- **Build Risk Sentiment Engine (RSE)** as foundational cross-asset risk regime layer
- Build 6 core analysis agents with modular architecture (all consuming RSE)
- Implement structured JSON output for agent interoperability
- Store analysis results in Supabase with proper schema
- Generate daily composite "Top-Down Analysis" report with RSE context
- Integrate Risk Manager with real-time alerting (RSE-adjusted thresholds)

#### Agent Development Schedule

| Day | Agent | Deliverables |
|-----|-------|--------------|
| Day 4 | **Risk Sentiment Engine (RSE)** ⭐ NEW | Cross-asset scoring (SPX/NDX/DXY/VIX/UST10Y/UST2Y/BRENT/XAU), regime classification, component breakdown |
| Day 5 | Portfolio Agent | Drawdown, win rate, expectancy, per-pair performance, RSE regime correlation |
| Day 6 | Macro + Sentiment Agents | Economic calendar (RSE-weighted), macro trends, news sentiment (RSE-filtered) |
| Day 7 | COT + Technical Agents | CFTC COT positioning (RSE context), support/resistance (RSE confluence) |
| Day 8 | Risk Manager | Drawdown monitoring (RSE-adjusted), damage control, threshold alerts |
| Day 9 | Integration & Testing | Agent coordination with RSE pipeline, composite report generation |

#### Deliverables
| File | Purpose |
|------|---------|
| `/backend/modules/rse/engine.py` ⭐ NEW | RSE core scoring logic with 7 components |
| `/backend/modules/rse/config.yaml` ⭐ NEW | RSE weights, hysteresis, staleness thresholds, pair overrides |
| `/backend/modules/rse/cache.py` ⭐ NEW | Redis/Supabase caching layer (30s TTL intraday) |
| `/src/agents/portfolio_agent.py` | Portfolio analytics (drawdown, win %, expectancy) |
| `/src/agents/macro_agent.py` | Macro trends and economic calendar integration (RSE-weighted) |
| `/backend/modules/sentiment_agent/core.py` | Sentiment scoring (hawkish/dovish bias, RSE-filtered) |
| `/src/agents/cot_agent.py` | CFTC COT report analysis (RSE context) |
| `/src/agents/technical_agent.py` | Support/resistance, trend detection (RSE confluence) |
| `/backend/modules/risk_manager/core.py` | Risk Manager with drawdown + damage control (RSE-adjusted) |
| `/backend/db/schema.sql` (updated) | Tables: rse_snapshots, sentiment_snapshots, macro_events, trades, risk_alerts, damage_control_levels |
| `/tests/integration/test_agent_pipeline.py` | Multi-agent integration tests (including RSE pipeline) |
| `/reports/daily_analysis_template.md` | Composite analysis report template with RSE regime context |

#### Phase-Gate Criteria
- [ ] **RSE scores calculated accurately (±5 points vs manual calculation)**
- [ ] **RSE regime classification 95% precision on historical data**
- [ ] **RSE component staleness monitoring operational (<20min critical, <60min non-critical)**
- [ ] **RSE score computation latency <500ms**
- [ ] Each agent returns structured JSON/dict output
- [ ] Risk Manager calculates drawdown within 0.1% accuracy
- [ ] Sentiment + Macro snapshots stored correctly in Supabase
- [ ] All 7 agents (including RSE) pass unit tests (100%)
- [ ] Integration tests pass including RSE pipeline (100%)
- [ ] Performance benchmarks met (<3s response per agent, <500ms RSE)
- [ ] Daily composite report generates successfully with RSE regime context
- [ ] Module READMEs and documentation complete (including RSE spec)
- [ ] Founder (Rob) approval

#### Agent Details

**Risk Sentiment Engine (RSE)** ⭐ NEW - Foundational Layer
- **Purpose:** Cross-asset risk regime scoring (-100 risk-off to +100 risk-on)
- **Components:** 7 weighted signals
  - Equities (SPX, NDX): 25% weight
  - Volatility (VIX): 20% weight (inverted)
  - USD (DXY): 15% weight (inverted)
  - Rates Level (UST10Y): 15% weight (inverted)
  - Curve Slope (UST10Y-UST2Y): 10% weight
  - Oil (BRENT): 10% weight (capped for stagflation)
  - Gold (XAU): 5% weight (inverted)
- **Normalization:** Rolling z-scores (5D intraday, 90D daily)
- **Hysteresis:** Prevents regime whipsawing (on: ±20, off: ±10)
- **Pair Overrides:** JPY crosses (+EQ/VOL), CHF (+VOL), Commodity FX (+OIL/EQ)
- **Output:** Score, regime (risk-on/off/neutral), component breakdown, confidence, staleness flags
- **Performance:** <500ms computation, 30s cache TTL intraday

**Portfolio Agent**
- Calculates portfolio-wide drawdown from peak equity
- Computes win rate, expectancy, and per-pair performance
- Identifies best/worst performing pairs
- **RSE Integration:** Correlates trade performance with historical RSE regimes

**Macro Agent**
- Integrates economic calendar (TradingEconomics or Forex Factory)
- Scores macro event impact (high/medium/low)
- Summarizes policy shifts (rates, inflation, central bank stance)
- **RSE Integration:** Weights macro bias by RSE regime context

**Sentiment Agent**
- Fetches news from FXStreet, NewsAPI
- Scores sentiment using FinBERT or similar NLP model
- Determines hawkish/dovish bias per currency
- **RSE Integration:** Filters news sentiment by RSE regime classification

**COT Agent**
- Parses CFTC COT reports (weekly)
- Tracks institutional net positioning
- Identifies positioning extremes and reversals
- **RSE Integration:** Contextualizes COT positioning with RSE regime

**Technical Agent**
- Detects support/resistance levels using historical price data
- Identifies trend direction (uptrend, downtrend, ranging)
- Calculates volatility zones and confluence areas
- **RSE Integration:** Adjusts confluence scores by RSE regime strength

**Risk Manager**
- Monitors real-time drawdown and exposure
- Tracks damage control levels per pair
- Triggers alerts when thresholds breached (<5s latency)
- Calculates R-multiples and position sizing recommendations
- **RSE Integration:** Adjusts damage control thresholds by RSE volatility component

---

### M3: Next.js Dashboard & Visualization (Days 10-13)

**Timeline:** Oct 23-26, 2025 (4 days)
**Status:** 🟡 Pending
**Dependencies:** M2 complete

#### Objectives
- Build production-ready Next.js frontend with modern UI/UX
- Integrate TradingView widgets with custom indicators
- Implement FastAPI backend with REST + WebSocket endpoints
- Enable real-time updates via WebSocket for risk alerts and price changes
- Create responsive mobile-friendly layout
- Docker containerization for deployment

#### Deliverables
| File | Purpose |
|------|---------|
| `/frontend/pages/dashboard.tsx` | Main dashboard UI with App Router |
| `/frontend/components/portfolio_panel.tsx` | Portfolio metrics display |
| `/frontend/components/tradingview_chart.tsx` | TradingView widget component |
| `/frontend/components/risk_alerts.tsx` | Real-time risk alert panel |
| `/frontend/components/macro_sentiment.tsx` | Macro + sentiment overview |
| `/frontend/hooks/useWebSocket.ts` | WebSocket hook for real-time data |
| `/backend/api/routes.py` | FastAPI REST endpoints |
| `/backend/api/websocket.py` | WebSocket handler for real-time updates |
| `/backend/api/models.py` | Pydantic models for API validation |
| `/docker-compose.yml` | Docker setup for frontend + backend + Supabase |
| `/tests/uat/test_dashboard_flows.py` | User acceptance test scenarios |

#### UI Layout

```
┌─────────────────────────────────────────────────────────┐
│ 🧭 Trading Copilot Dashboard                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [Portfolio] [Macro] [Sentiment] [Technical] [Risk]     │
│                                                          │
│  ┌────────────────┐  ┌────────────────────────────┐    │
│  │  TradingView   │  │  Risk Alerts (Live)        │    │
│  │  Chart Widget  │  │  • Drawdown: 2.3%          │    │
│  │                │  │  ⚠️  EUR/USD near DC level   │    │
│  │  [EUR/USD 4H]  │  │  • Exposure: 45% portfolio │    │
│  └────────────────┘  └────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Top-Down Analysis Summary                       │  │
│  │  Macro: 📈 Hawkish (USD strength expected)       │  │
│  │  Sentiment: 😐 Neutral retail positioning        │  │
│  │  COT: 📊 Institutional long USD (+12% vs avg)   │  │
│  │  Technical: 🎯 Key support at 1.0850            │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

#### Phase-Gate Criteria
- [ ] Dashboard loads in <3s
- [ ] TradingView charts render correctly with custom indicators
- [ ] All 6 agent data displayed in appropriate tabs
- [ ] WebSocket updates work without lag (<500ms latency)
- [ ] Mobile responsive design validated (Tailwind breakpoints)
- [ ] User acceptance testing (UAT) passed
- [ ] Docker Compose deployment tested locally
- [ ] API documentation generated (FastAPI OpenAPI)
- [ ] Founder (Rob) approval

#### Technology Stack
- **Frontend:** Next.js 14+ (App Router), Tailwind CSS, DaisyUI
- **Backend:** FastAPI, Pydantic, asyncio, uvicorn
- **Charts:** TradingView Widgets (JavaScript library)
- **Real-time:** WebSocket (native + React hooks)
- **Deployment:** Docker + Docker Compose

---

### M4: Testing, Validation & MVP Release (Days 14-15)

**Timeline:** Oct 27-28, 2025 (2 days)
**Status:** 🟡 Pending
**Dependencies:** M3 complete

#### Objectives
- Execute comprehensive end-to-end integration tests
- Validate performance benchmarks against success criteria
- Security audit (API keys, authentication, SQL injection prevention)
- Generate final reflection report with lessons learned
- Tag v2.0.0 release on GitHub
- Deploy to production environment

#### Deliverables
| File | Purpose |
|------|---------|
| `/tests/integration/test_full_pipeline.py` | E2E test: IBKR → Agents → Dashboard |
| `/tests/performance/benchmark_results.json` | Performance test results |
| `/docs/reflection_report.md` (final) | Post-MVP reflection with architecture notes |
| `/logs/final_validation.log` | Validation test logs |
| `/docs/deployment_guide.md` | Production deployment instructions |
| `/docs/user_guide.md` | End-user onboarding documentation |
| Git tag: `v2.0.0` | Official MVP release tag |

#### Test Coverage
- **Unit Tests:** 100% pass rate for all modules
- **Integration Tests:** Full data pipeline validation
- **Performance Tests:** Dashboard load <3s, agent latency <3s, risk alerts <5s
- **Security Tests:** API key encryption, SQL injection prevention, CORS config
- **UAT:** Manual validation of all user workflows

#### Phase-Gate Criteria
- [ ] All integration tests pass (100%)
- [ ] Performance benchmarks met (see success criteria)
- [ ] Risk alerts tested with simulated threshold events
- [ ] Security audit complete (OWASP checklist)
- [ ] Phase-gate checklist 100% for all M1-M3 modules
- [ ] CHANGELOG and version tags accurate
- [ ] Deployment guide tested on staging environment
- [ ] User guide reviewed for clarity
- [ ] Founder (Rob) final approval for production deployment

#### Success Criteria Validation
| Metric | Target | Result | Status |
|--------|--------|--------|--------|
| Data sync success rate | ≥ 95% | ___% | 🟡 TBD |
| Dashboard load time | < 3s | ___s | 🟡 TBD |
| Agent response latency | < 3s | ___s | 🟡 TBD |
| Risk alert timeliness | < 5s | ___s | 🟡 TBD |
| Test coverage | 100% pass | ___% | 🟡 TBD |
| Phase-gate completion | 100% | ___% | 🟡 TBD |

---

## 📅 Phase 1 Timeline Summary

| Week | Days | Milestones | Status |
|------|------|------------|--------|
| **Week 1** | Oct 14-16 | M1: Data Integration | 🟡 Pending |
| **Week 2** | Oct 17-21 | M2: 6-Agent Analytics Engine | 🟡 Pending |
| **Week 2-3** | Oct 22-25 | M3: Next.js Dashboard | 🟡 Pending |
| **Week 3** | Oct 26-27 | M4: Testing & MVP Release | 🟡 Pending |

**Total Duration:** 14 days
**Target Launch:** October 27, 2025 (v2.0.0)

---

## 🎨 Gantt Chart (Phase 1)

```
Week 1:
  M1: [###.......]  Oct 14-16 (Data Integration)
  M2: [....#####..]  Oct 17-21 (6 Agents)

Week 2:
  M3: [........####]  Oct 22-25 (Dashboard)
  M4: [..........##]  Oct 26-27 (Testing)
```

---

## 🚀 Phase 2: Full System — Voice & Advanced Agents (v3.0.0)

**Duration:** TBD (post-MVP)
**Goal:** Voice-controlled trading assistant with Trade Planner, Mentor, and Coordinator agents
**Status:** 📅 Planned for future iteration

### Scope (Phase 2)

#### Trade Planner Agent
- **Purpose:** Compile insights from all agents into structured trade plan
- **Features:** Pre-trade checklist validation, entry/exit criteria, risk/reward calculation
- **Timeline:** 5 days

#### Mentor Agent
- **Purpose:** Provide discipline coaching, trade review, critique of trade logic
- **Features:** Post-trade analysis, pattern recognition, behavior tracking
- **Timeline:** 5 days

#### Coordinator Agent
- **Purpose:** Orchestrate multi-agent workflows, resolve conflicting opinions
- **Features:** Agent prioritization, consensus scoring, decision tree logic
- **Timeline:** 4 days

#### Voice Interface
- **Purpose:** Enable voice-to-agent interaction for hands-free operation
- **Technology:** Whisper (STT) + ElevenLabs (TTS)
- **Features:** Natural language commands, spoken analysis summaries, voice alerts
- **Timeline:** 7 days

#### Long-Term Memory (Vector Search)
- **Purpose:** Enable contextual recall across trading sessions
- **Technology:** ChromaDB or Supabase pgvector
- **Features:** Semantic search of past trades, pattern matching, learning continuity
- **Timeline:** 6 days

### Phase 2 Timeline Estimate
- **Total Duration:** 27 days (~4 weeks)
- **Target Version:** v3.0.0
- **Launch:** Q1 2026 (tentative)

---

## 📦 Key Deliverables (All Phases)

### Phase 1 (MVP v2.0)
- [x] Planning documents (project_plan.yaml, roadmap.md, PRD.md)
- [ ] 6-agent analytics system (Portfolio, Macro, Sentiment, COT, Technical, Risk)
- [ ] Next.js dashboard with TradingView integration
- [ ] FastAPI backend with REST + WebSocket
- [ ] Supabase data persistence
- [ ] Docker containerization
- [ ] Comprehensive test suite
- [ ] Production deployment

### Phase 2 (Full System v3.0)
- [ ] Trade Planner Agent with checklists
- [ ] Mentor Agent with trade review
- [ ] Coordinator Agent for multi-agent orchestration
- [ ] Voice interface (Whisper + ElevenLabs)
- [ ] Long-term memory with vector search (ChromaDB)
- [ ] Enhanced mobile app experience

---

## 🔗 Dependencies & Prerequisites

### External Services (Phase 1)
- Interactive Brokers account (demo or live)
- Alpha Vantage API key (free or premium tier)
- TradingView account (free tier acceptable)
- Supabase project (free or pro tier)
- CFTC data access (public, no auth required)
- Economic calendar API (TradingEconomics or Forex Factory)

### Development Environment
- Python 3.10+ with virtual environment
- Node.js 18+ with npm/yarn
- Docker + Docker Compose
- Git version control
- Code editor (VS Code recommended)

### API Keys Checklist
- [ ] Interactive Brokers TWS API credentials
- [ ] Alpha Vantage API key
- [ ] Supabase project URL and anon key
- [ ] News API key (for sentiment)
- [ ] TradingEconomics API key (optional)

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation Strategy | Owner |
|------|--------|------------|---------------------|-------|
| IBKR API instability | High | Medium | Retry logic, caching, demo account fallback, API status monitoring | Rob |
| Alpha Vantage quota limits | Medium | Medium | Local caching, upgrade tier if needed, fallback data sources | Rob |
| Sentiment API drift | Medium | Medium | Multiple providers, confidence scoring, manual validation | Rob |
| TradingView integration complexity | Medium | Low | Prototype early (M1), official library, incremental rollout | Rob |
| COT data parsing errors | Low | Medium | Weekly cache, multi-source validation, quality checks | Rob |
| Phase-gate discipline breakdown | High | Low | Strict development_flow.md enforcement, mandatory docs updates | Rob |
| Next.js + FastAPI complexity | Medium | Medium | Start REST before WebSocket, Docker for consistency, early prototyping | Rob |

---

## 📋 Review Schedule

| Review Type | Date | Owner | Purpose |
|-------------|------|-------|---------|
| Kickoff Review | Oct 14 | Rob | Confirm scope, tech stack, timeline |
| M1 Review | Oct 16 | Planner Agent | Validate data integration before M2 |
| M2 Mid-Review | Oct 19 | Rob | Check agent progress, adjust if needed |
| M2 Final Review | Oct 21 | Planner Agent | Approve agents before dashboard work |
| M3 Review | Oct 25 | Rob | Validate UI/UX, performance |
| Final MVP Review | Oct 27 | Rob + Planner Agent | Production deployment approval |
| Post-Launch Retrospective | Oct 31 | Rob | Lessons learned, Phase 2 planning |

---

## 🎯 Success Metrics (Phase 1)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Data sync success rate | ≥ 95% | Monitor logs, track API errors |
| Dashboard load time | < 3s per tab | Performance profiling, Lighthouse audit |
| Agent response latency | < 3s per analysis | Benchmark tests, production monitoring |
| Risk alert timeliness | < 5s from threshold breach | Integration tests with simulated events |
| Test coverage | 100% pass rate | pytest execution, CI/CD gates |
| Phase-gate completion | 100% checklist per module | Manual review against development_flow.md |
| Documentation completeness | All modules documented | PRD, README, CHANGELOG review |
| Analysis alignment | Qualitative match with strategy | Manual validation, trader feedback |
| User engagement | Daily use (8+ hours) | Usage analytics, session logs |

---

## 🪞 Governance & Quality

### Phase-Gate Process
- Each milestone has mandatory exit criteria
- No proceeding to next phase without 100% checklist completion
- Founder (Rob) approval required for each phase
- CHANGELOG updated with every version tag
- Tests must pass 100% before merge

### Documentation Standards
- All code has docstrings (Google style)
- Type hints required (Python 3.10+)
- FastAPI endpoints auto-documented (OpenAPI)
- Module READMEs for each agent
- Architecture decisions logged in reflection_report.md

### Version Control
- **Major (X.0.0):** Architectural overhaul
- **Minor (X.Y.0):** New module or significant feature
- **Patch (X.Y.Z):** Bug fix, test update, doc refinement

### Testing Pyramid
- **Unit Tests:** Individual function validation
- **Integration Tests:** Multi-module data flow
- **Performance Tests:** Latency and throughput benchmarks
- **UAT:** Manual user acceptance testing

---

## 💡 Future Enhancements (Beyond Phase 2)

- **Machine Learning Bias Detector:** Identify strategy drift using ML models
- **Multi-Asset Support:** Extend to commodities, indices, cryptocurrencies
- **Advanced Risk Metrics:** Sharpe ratio, Sortino ratio, maximum adverse excursion
- **Correlation Matrix:** Real-time correlation analysis between currency pairs
- **Multi-Timeframe Analysis:** Synchronized 1H, 4H, Daily, Weekly views
- **Social Trading Features:** Share analysis with community (read-only)
- **Mobile Native App:** iOS/Android with push notifications
- **Backtesting Engine:** Historical strategy validation

---

## 🔮 Closing Vision

This roadmap transforms a complex trading analysis workflow into a structured, modular, and scalable AI-powered system. Phase 1 delivers immediate value with a production-ready analytics dashboard. Phase 2 extends capabilities with voice interaction and advanced planning/mentoring.

> "Every successful trade starts with clarity — the same applies to systems.
> This roadmap ensures structure, oversight, and disciplined execution."

---

**Generated by:** Planner Agent v1.1 (Enhanced with RSE integration)
**Template Version:** 2.1
**Last Updated:** 2025-10-11
**Status:** 🟢 Planning Complete — Ready for M1 Execution (MVP now 15 days with RSE)

**Next Step:** Begin M1 (Data Integration Layer) on October 14, 2025. M2 now includes RSE as foundational Day 4 deliverable.

---

**Reference Documents:**
- **Project Plan:** `/planning/project_plan.yaml`
- **PRD:** `/docs/PRD.md`
- **Development Flow:** `/docs/development_flow.md`
- **Claude Config:** `/control/Claude.md`
- **CHANGELOG:** `/docs/CHANGELOG.md`
