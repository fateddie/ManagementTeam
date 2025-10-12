---
project:
  name: "Trading Strategy Reference System"
  version: "1.0"
  owner: "Rob Freyne"
  date: "2025-10-11"
  type: "Trading Strategy PRD"
  category: "AI Trading / Market Analysis"
  status: "Active"
  description: >
    Defines the methodology, technical analysis framework, and risk-management
    logic for Rob Freyne’s discretionary swing-trading system. 
    Serves as a foundational document for Claude and management-layer AI agents.
  dependencies:
    - Broker API: Interactive Brokers
    - Charting: TradingView API / Pine Script
    - Feeds: COT, sentiment, correlation, macro indicators
    - Tools: Drawdown Calculator, Risk Dashboard
  outputs:
    - Market narrative & directional bias
    - Scored trade setups
    - Exposure and drawdown alerts
---

# 🧭 Product Requirements Document (PRD)
**Project:** Trading Strategy Reference System  
**Version:** 1.0  
**Owner:** Rob Freyne  
**Date:** 2025-10-11  

---

## 1. Overview

### 1.1 Purpose
To formalize the trading logic, technical framework, and risk-management rules that define Rob’s discretionary swing-trading methodology.  
This PRD ensures Claude (and related AI agents) can interpret, test, and expand trading logic without deviating from the trader’s philosophy.

### 1.2 Goals
- Encode trading philosophy, structure, and decision-making logic into standardized layers.  
- Enable Claude to reference this system when generating trading plans, checklists, or Pine/Python modules.  
- Guarantee consistency across strategy documentation, execution scripts, and dashboards.  

### 1.3 Scope
Covers methodology (why), technical analysis (how), and risk control (safety).  
Future integration will include journaling, macro dashboards, and real-time automation.

---

## 2. System Architecture

### 2.1 Core Layers
| Layer | Description | Output |
|-------|--------------|--------|
| **Methodology** | Defines mindset, bias formation, and multi-timeframe logic. | Market narrative & directional bias. |
| **Technical Framework** | Identifies levels, structure, and confluence factors. | Scored trade setups. |
| **Risk Management** | Monitors drawdown, exposure, and triggers defense actions. | Capital protection & alerts. |

### 2.2 Data Sources
- **Chart data:** Price, volume, structure levels  
- **External feeds:** COT, retail sentiment, correlation, macro indicators  
- **Internal metrics:** Drawdown %, confluence scores, exposure logs

---

## 3. Functional Requirements

### 3.1 Core Trading Methodology
| Component | Requirement |
|------------|-------------|
| **Trading Style** | Swing-based level trading with momentum confirmation |
| **Market Context** | Trades both risk-on and risk-off; direction derived from structure & sentiment, not regime bias |
| **Timeframes** | Monthly → Weekly → Daily → 4H (top-down continuity required) |
| **Execution Logic** | Enter at/near key levels after momentum confirmation; opposite trades allowed for hedging or range exploitation |
| **Data Inputs** | COT, sentiment feeds, correlation data, technical indicators (MAs, Stoch RSI) |
| **Guiding Statement** | “I trade levels, but I follow flow.” |

---

### 3.2 Technical Analysis Framework
| Component | Requirement |
|------------|-------------|
| **Structure Mapping** | Nested: Monthly/Weekly (macro), Daily (swing), 4H (tactical) |
| **Confluence Scoring** | 0–10 system combining timeframe alignment, momentum, sentiment, liquidity context, and event clearance |
| **Indicators** | 20 EMA, 50 SMA, 200 SMA, Stoch RSI (14,3,3), ATR, Volume Profile (if available) |
| **Visualization** | Multi-panel TradingView layout with color-coded levels & confluence overlays |
| **Trend Logic** | Classify moves as Impulse, Correction, or Transition; bias valid only when trend & confluence align |

---

### 3.3 Risk Management & Damage Control
| Component | Requirement |
|------------|-------------|
| **Primary Objective** | Capital preservation via dynamic exposure and drawdown control |
| **Drawdown Thresholds** | Soft (5%) → warning; Hard (10%) → trigger damage control |
| **Position Sizing** | Based on confluence, volatility, correlation, and drawdown buffer |
| **Exposure Caps** | Enforced across pairs & correlated clusters (e.g., EUR/USD ↔ DXY) |
| **Damage Control Protocol** | 1. Detect trigger breach → 2. Assess exposure → 3. Hedge → 4. Pause entries → 5. Log & review |
| **Monitoring Tools** | Drawdown Calculator + Risk Dashboard with live broker sync |
| **Review Loop** | Every event logged; root cause analyzed; thresholds refined |
| **Guiding Statement** | “Beyond the trigger, I defend the account — not the idea.” |

---

## 4. Non-Functional Requirements
| Area | Requirement |
|-------|-------------|
| **Consistency** | All AI outputs must align with methodology, technical, and risk rules |
| **Modularity** | Each layer can be upgraded independently |
| **Transparency** | All rule changes logged and version-controlled |
| **Extensibility** | Future integration with journaling, macro dashboards, broker APIs |
| **Performance** | Minimal latency for alerts (<2s for threshold triggers) |

---

## 5. Dependencies
- **Broker API (Interactive Brokers)** for trade and exposure data  
- **TradingView API/Pine Scripts** for visual overlays & alerts  
- **COT/Sentiment Feeds** for bias validation  
- **Drawdown Database / Dashboard** for persistent tracking

---

## 6. Future Enhancements
- Automated journaling with trade tagging  
- Confluence auto-learning via historical back-testing  
- AI-driven sentiment aggregation (multi-feed weighting)  
- Macro dashboard integration for global risk sentiment  
- Voice/agent interface for real-time decision discussion  

---

## 7. Acceptance Criteria
- ✅ Core methodology accurately reproduced in AI-generated plans  
- ✅ Technical layer produces scored, justifiable levels per asset  
- ✅ Risk system enforces drawdown thresholds automatically  
- ✅ Damage control triggers and logging validated via test trades  
- ✅ Documentation versioned and accessible to all management-layer agents  

---

## 8. Reference
**Source Documents:**  
- *Trading Strategy Reference Document (TSRD)*  
- *Drawdown Calculator Specification*  
- *Agent Governance Framework*  
