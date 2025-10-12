# 🏗️ Architecture Mapping - Trading Strategy Reference System

**Project:** Trading Strategy Reference System  
**Version:** 1.0  
**Date:** 2025-10-11  
**Purpose:** Map Management Layer outputs to implementation structure

---

## Layer Responsibilities

| Layer | Purpose | Claude / Cursor Role |
|-------|---------|----------------------|
| **docs/** | All human + machine-readable strategy docs | PRD context ingestion + milestone/risk extraction |
| **src/core/** | Implements the main trading logic | MethodologyEngine / TechnicalFramework / RiskManager |
| **src/integrations/** | Handles all data and API connectivity | IBKR, TradingView, COT, etc. |
| **src/analysis/** | Optional enhancements and AI interface features | Journaling, macro dashboards, voice input |
| **pine/** | TradingView visualization layer | Connects technical logic to user charts |
| **config/** | Controls thresholds, secrets, and runtime behavior | Adjustable without code changes |
| **tests/** | Maintains system integrity | Continuous validation of logic |
| **data/** | Stores persistent and cached data | Reference layer for training or review |
| **docker/** | Containerization and CI/CD setup | Deployable anywhere consistently |

---

## Management Team → Implementation Flow

### Phase 1: Planning (Management Layer)

**Inputs:**
- `docs/trading_strategy_prd.md` - Human-readable requirements
- `docs/trading_strategy_prd_addendum.yaml` - Machine-readable extensions

**Management Team Agents Execute:**
1. **Strategy Agent** - Extracts goals, constraints, risks, milestones
2. **Technical Architect** - Designs modules (MethodologyEngine, TechnicalFramework, RiskManager)
3. **Planning Agent** - Creates roadmap, dependency map, project plan
4. **Documentation Agent** - Generates technical specs, PRD summary

**Outputs:**
- `outputs/strategy_plan.yaml` - Complete strategy with 4 milestones, 3 risks, 3 phases
- `outputs/technical_design.yaml` - Module specifications with inputs/outputs
- `outputs/project_plan.yaml` - Merged plan with all extracted data
- `outputs/roadmap.md` - Timeline and deliverables

---

### Phase 2: Implementation (Claude Code / Cursor)

**Using Management Team outputs as context:**

#### 🎯 Milestone M1: Interactive Brokers Integration (14 days)

**From technical_design.yaml:**
```yaml
modules:
  - name: RiskManager
    inputs: [positions, account_balance, market_volatility]
    outputs: [exposure_alerts, hedge_recommendations]
```

**Implementation:**
```python
# src/integrations/ibkr_api.py
class IBKRClient:
    """Interactive Brokers API interface for real-time position data."""
    def get_positions(self) -> List[Position]: ...
    def get_account_balance(self) -> float: ...
    def place_hedge_order(self, symbol: str, quantity: int): ...

# src/core/risk_manager.py
class RiskManager:
    """Drawdown monitoring (5%/10% thresholds) and damage control."""
    def __init__(self, broker_client: IBKRClient):
        self.soft_threshold = 0.05  # From config/settings.yaml
        self.hard_threshold = 0.10
        self.broker = broker_client
    
    def calculate_drawdown(self) -> float:
        """Calculate current drawdown from peak equity."""
        positions = self.broker.get_positions()
        balance = self.broker.get_account_balance()
        # Implementation based on PRD section 3.3
        ...
    
    def trigger_damage_control(self) -> List[Action]:
        """PRD section 3.3 protocol: Detect → Assess → Hedge → Pause → Log."""
        actions = []
        if self.calculate_drawdown() >= self.hard_threshold:
            actions.append(self._hedge_positions())
            actions.append(self._pause_new_entries())
            actions.append(self._log_event())
        return actions
```

**Tests:**
```python
# tests/test_risk_manager.py
def test_drawdown_threshold_trigger():
    """Verify damage control triggers at 10% drawdown (PRD requirement)."""
    mock_broker = MockIBKRClient(balance=90000, peak=100000)
    risk_mgr = RiskManager(mock_broker)
    assert risk_mgr.calculate_drawdown() == 0.10
    actions = risk_mgr.trigger_damage_control()
    assert "hedge" in [a.type for a in actions]
```

**Config:**
```yaml
# config/settings.yaml
risk_management:
  drawdown_soft_threshold: 0.05  # Warning level
  drawdown_hard_threshold: 0.10  # Damage control trigger
  exposure_caps:
    per_pair: 0.02  # 2% max per currency pair
    correlated_cluster: 0.05  # 5% max EUR/USD + DXY
```

---

#### 🎯 Milestone M2: TradingView Integration (14 days)

**From technical_design.yaml:**
```yaml
modules:
  - name: TechnicalFramework
    purpose: "Confluence scoring (0–10) combining timeframe alignment, momentum, sentiment."
    inputs: [price_data, structure_levels, indicators]
    outputs: [scored_setups, trade_signals]
```

**Implementation:**
```python
# src/core/technical_framework.py
class TechnicalFramework:
    """Confluence scoring system (0-10) per PRD section 3.2."""
    
    def calculate_confluence(self, symbol: str, timeframe: str) -> ConfluenceScore:
        """
        Combines:
        - Timeframe alignment (Monthly → Weekly → Daily → 4H)
        - Momentum (20 EMA, 50 SMA, 200 SMA, Stoch RSI)
        - Sentiment (COT, retail positioning)
        - Liquidity context (volume profile)
        - Event clearance (economic calendar)
        
        Returns score 0-10 per PRD specification.
        """
        score = 0
        score += self._check_timeframe_alignment(symbol)  # Max 3 points
        score += self._check_momentum(symbol, timeframe)  # Max 3 points
        score += self._check_sentiment(symbol)  # Max 2 points
        score += self._check_liquidity(symbol)  # Max 1 point
        score += self._check_event_clearance(symbol)  # Max 1 point
        return ConfluenceScore(symbol=symbol, score=score, timestamp=now())

# src/integrations/tradingview_client.py
class TradingViewClient:
    """Chart overlays, confluence scoring visuals, and alert system."""
    
    def publish_confluence_overlay(self, scores: List[ConfluenceScore]):
        """Send confluence scores to TradingView for visual overlay."""
        # Connects to pine/confluence_scoring_tool.pine
        ...
```

**Pine Script:**
```pinescript
// pine/confluence_scoring_tool.pine
//@version=5
indicator("Confluence Scoring (0-10)", overlay=true)

// Receives scores from src/core/technical_framework.py via TradingView API
confluenceScore = input.int(0, "Confluence Score", minval=0, maxval=10)

// Color-coded levels per PRD visualization requirements
scoreColor = confluenceScore >= 8 ? color.green : 
             confluenceScore >= 6 ? color.yellow : color.red

// Display score label
label.new(bar_index, high, str.tostring(confluenceScore), 
          color=scoreColor, textcolor=color.white, size=size.large)
```

---

#### 🎯 Milestone M3: COT & Sentiment Feed Integration (14 days)

**From technical_design.yaml:**
```yaml
modules:
  - name: MethodologyEngine
    purpose: "Bias formation using multi-timeframe analysis (Monthly→Weekly→Daily→4H)."
    inputs: [price_data, cot_data, sentiment_feeds]
    outputs: [directional_bias, market_narrative]
```

**Implementation:**
```python
# src/integrations/sentiment_feeds.py
class SentimentAggregator:
    """COT, retail sentiment, correlation data - PRD section 3.1."""
    
    def get_cot_positioning(self, symbol: str) -> COTReport:
        """Fetch Commitment of Traders data for bias validation."""
        # Downloads from CFTC weekly reports
        ...
    
    def get_retail_sentiment(self, symbol: str) -> float:
        """Get retail trader positioning (contrarian indicator)."""
        # Fetches from sentiment provider APIs
        ...
    
    def get_correlation_matrix(self, symbols: List[str]) -> pd.DataFrame:
        """Calculate correlation for exposure cap enforcement."""
        # Used by RiskManager for cluster exposure (EUR/USD ↔ DXY)
        ...

# src/core/methodology_engine.py
class MethodologyEngine:
    """Multi-timeframe bias formation - PRD section 3.1 'I trade levels, but I follow flow'."""
    
    def form_bias(self, symbol: str) -> MarketBias:
        """
        Top-down analysis: Monthly → Weekly → Daily → 4H
        Returns: BULLISH, BEARISH, NEUTRAL with confidence score
        """
        monthly_trend = self._analyze_timeframe(symbol, "1M")
        weekly_trend = self._analyze_timeframe(symbol, "1W")
        daily_trend = self._analyze_timeframe(symbol, "1D")
        h4_trend = self._analyze_timeframe(symbol, "4H")
        
        cot_data = self.sentiment.get_cot_positioning(symbol)
        retail_sentiment = self.sentiment.get_retail_sentiment(symbol)
        
        # Confluence across timeframes + sentiment validation
        bias = self._calculate_bias(
            trends=[monthly_trend, weekly_trend, daily_trend, h4_trend],
            cot=cot_data,
            retail=retail_sentiment
        )
        
        return MarketBias(
            symbol=symbol,
            direction=bias.direction,
            confidence=bias.confidence,
            narrative=self._generate_narrative(bias)
        )
```

**Data Storage:**
```
data/
├── cot_reports/
│   ├── EUR_2025_W01.csv
│   ├── EUR_2025_W02.csv
│   └── ...
├── trade_logs/
│   ├── 2025-10-11_EURUSD_entry.json
│   └── ...
└── market_data/
    ├── EURUSD_1M.parquet
    ├── EURUSD_1W.parquet
    └── ...
```

---

#### 🎯 Milestone M4: Drawdown Dashboard (14 days)

**From technical_design.yaml + PRD section 3.3:**

**Implementation:**
```python
# src/integrations/dashboard_api.py
from flask import Flask, jsonify
from src.core.risk_manager import RiskManager

app = Flask(__name__)

@app.route('/api/drawdown/current')
def get_current_drawdown():
    """Real-time drawdown % - mirrors PRD section 3.3."""
    risk_mgr = RiskManager(broker_client)
    return jsonify({
        'drawdown_percent': risk_mgr.calculate_drawdown(),
        'soft_threshold': 0.05,
        'hard_threshold': 0.10,
        'status': risk_mgr.get_status()  # OK, WARNING, DAMAGE_CONTROL
    })

@app.route('/api/exposure/summary')
def get_exposure_summary():
    """Exposure across pairs & correlated clusters - PRD section 3.3."""
    exposure = risk_mgr.calculate_exposure()
    return jsonify({
        'by_pair': exposure.per_pair,  # e.g., {'EURUSD': 0.015, 'GBPUSD': 0.020}
        'by_cluster': exposure.clusters,  # e.g., {'EUR+DXY': 0.045}
        'total': exposure.total
    })

# Frontend dashboard consumes these endpoints
# Shows live drawdown gauge, exposure breakdown, risk alerts
```

**Pine Script Integration:**
```pinescript
// pine/drawdown_calculator.pine
//@version=5
indicator("Live Drawdown Monitor", overlay=false)

// Synced with src/core/risk_manager.py calculations
drawdownPercent = input.float(0.0, "Current Drawdown %")
softThreshold = 5.0
hardThreshold = 10.0

// Visual indicators matching PRD requirements
plot(drawdownPercent, "Drawdown", color=color.blue, linewidth=2)
hline(softThreshold, "Soft Threshold", color=color.yellow, linestyle=hline.style_dashed)
hline(hardThreshold, "Hard Threshold", color=color.red, linestyle=hline.style_solid)

// Alert when hard threshold breached (PRD damage control trigger)
alertcondition(drawdownPercent >= hardThreshold, "Damage Control", "Drawdown ≥ 10% - Trigger Protocol")
```

---

## File Connection Matrix

| Document | Consumes / Feeds | Implementation |
|----------|------------------|----------------|
| **trading_strategy_prd.md** | Defines logic and requirements for `src/core/` | All core modules implement PRD specifications |
| **trading_strategy_prd_addendum.yaml** | Parsed by Management Layer → creates phases, milestones, module structure | Strategy Agent extracts → Technical Architect consumes |
| **config/settings.yaml** | Configures drawdown thresholds, confluence weights, exposure caps | Loaded by `RiskManager`, `TechnicalFramework`, `MethodologyEngine` |
| **src/integrations/dashboard_api.py** | Displays live data defined by `risk_manager.py` | Flask API exposes RiskManager methods |
| **pine/drawdown_calculator.pine** | Mirrors `RiskManager` behavior for TradingView overlay | Synced calculations via TradingView API |
| **src/analysis/journaling.py** | Writes structured entries into `data/trade_logs/` for agent review | Post-trade analysis, pattern recognition |

---

## Configuration Hierarchy

### Priority Order (Highest to Lowest):
1. **Environment Variables** (`.env`) - Secrets, API keys
2. **settings.yaml** - User-configurable thresholds, pairs, timeframes
3. **PRD Specifications** - Hard requirements (e.g., drawdown thresholds 5%/10%)
4. **Code Defaults** - Fallback values in module initialization

### Example: Drawdown Threshold Configuration

**Defined in PRD (Section 3.3):**
> Drawdown Thresholds: Soft (5%) → warning; Hard (10%) → trigger damage control

**Configured in settings.yaml:**
```yaml
risk_management:
  drawdown_soft_threshold: 0.05
  drawdown_hard_threshold: 0.10
```

**Loaded in code:**
```python
# src/core/risk_manager.py
class RiskManager:
    def __init__(self, config_path="config/settings.yaml"):
        config = yaml.safe_load(open(config_path))
        self.soft_threshold = config['risk_management']['drawdown_soft_threshold']
        self.hard_threshold = config['risk_management']['drawdown_hard_threshold']
        # PRD requirement enforced: must be 0.05 and 0.10
        assert self.soft_threshold == 0.05, "PRD requires 5% soft threshold"
        assert self.hard_threshold == 0.10, "PRD requires 10% hard threshold"
```

**Monitored in dashboard:**
```python
# src/integrations/dashboard_api.py
@app.route('/api/risk/thresholds')
def get_thresholds():
    """Returns configured thresholds for dashboard display."""
    return jsonify({
        'soft': risk_mgr.soft_threshold,
        'hard': risk_mgr.hard_threshold,
        'current_drawdown': risk_mgr.calculate_drawdown(),
        'status': 'OK' if risk_mgr.calculate_drawdown() < risk_mgr.soft_threshold else 'WARNING'
    })
```

**Visualized in TradingView:**
```pinescript
// pine/drawdown_calculator.pine
softThreshold = 5.0  // Must match settings.yaml
hardThreshold = 10.0  // Must match settings.yaml
```

---

## Development Workflow

### 1. Planning Phase (Management Layer)
```bash
# Run Management Team orchestrator
cd /path/to/ManagementTeam
PYTHONPATH=. python agents/orchestrator/orchestrator.py

# Review generated outputs
cat outputs/technical_design.yaml  # Module specifications
cat outputs/roadmap.md             # Implementation timeline
cat outputs/project_plan.yaml      # Complete plan with milestones
```

### 2. Implementation Phase (Claude Code / Cursor)
```bash
# Create project structure
mkdir -p trading-strategy-reference-system/{src/core,src/integrations,src/analysis,pine,config,tests,data,docker}

# Implement modules according to technical_design.yaml
# Use PRD sections as specification reference
# Follow roadmap.md timeline (M1 → M2 → M3 → M4)
```

### 3. Testing Phase
```bash
# Unit tests validate PRD requirements
pytest tests/test_risk_manager.py::test_drawdown_threshold_trigger
pytest tests/test_technical_framework.py::test_confluence_scoring_range

# Integration tests verify end-to-end flow
pytest tests/test_integrations.py::test_ibkr_to_risk_manager_flow
```

### 4. Deployment Phase
```bash
# Docker containerization
docker-compose up -d

# Verify dashboard accessible
curl http://localhost:5000/api/drawdown/current
curl http://localhost:5000/api/exposure/summary
```

---

## Maintenance & Evolution

### When PRD Changes:
1. Update `trading_strategy_prd.md` (human-readable requirements)
2. Update `trading_strategy_prd_addendum.yaml` (structured milestones/risks)
3. Re-run Management Team orchestrator
4. Review diff in `outputs/technical_design.yaml`
5. Update affected modules in `src/`
6. Update tests to match new requirements
7. Regenerate documentation

### When Thresholds Change:
1. Update `config/settings.yaml`
2. No code changes required (configuration-driven)
3. Verify tests still pass with new thresholds

### When Adding New Features:
1. Add milestone to `trading_strategy_prd_addendum.yaml`
2. Re-run orchestrator to update project plan
3. Implement according to generated technical specification
4. Add tests, update documentation

---

## References

- **Management Layer System**: `/path/to/ManagementTeam/`
- **PRD**: `docs/trading_strategy_prd.md`
- **Addendum**: `docs/trading_strategy_prd_addendum.yaml`
- **Generated Specs**: `/path/to/ManagementTeam/outputs/technical_design.yaml`
- **Implementation Guide**: This document

---

**Generated by:** Management Layer Documentation Agent  
**Based on:** Management Team outputs + Implementation architecture  
**Last Updated:** 2025-10-11
