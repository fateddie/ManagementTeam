# Variant Exploration SOP (Standard Operating Procedure)

## Purpose

Guide the end-to-end evaluation of multiple idea variants through identical, auditable phases — from intake to final decision.

This SOP ensures that every variant is evaluated using the same rigorous methodology, enabling fair comparison and data-backed decisions.

---

## Phases

### **Phase 0: Intake & Ownership**

**Goal:** Capture the base idea and define success criteria.

**Questions:**
1. What is your base idea in one sentence?
2. Which regions or markets do you want to explore?
3. What are your success criteria? (e.g., payback < 12 months, 5 LOIs, ROI > 300%)
4. What key assumptions or risks do you already see?

**Output:** `idea_intake.json`

**Gate:** Confirm intake details before proceeding.

---

### **Phase 1: Hypothesis & Scope**

**Goal:** Define the specific hypothesis, boundaries, and variant-specific positioning.

**Questions:**
1. What is the core hypothesis for this variant? (e.g., "Freelance designers will pay €25/mo for email triage")
2. Who is the ideal customer profile (ICP) for this variant?
3. What problem/pain are you focusing on?
4. What is explicitly OUT of scope for this variant?

**Output:** `scope.yaml`

**Gate:** Confirm scope before research planning.

---

### **Phase 2: Research Plan**

**Goal:** Define what evidence you need and how you'll gather it.

**Questions:**
1. What questions do you need answered to validate this variant?
2. What data sources will you use? (Perplexity, interviews, surveys, etc.)
3. What is the minimum viable evidence to make a decision?
4. What would constitute "strong evidence" vs "weak evidence"?

**Output:** `research_plan.md`

**Gate:** Approve research methodology before data collection.

---

### **Phase 3: Evidence Collection**

**Goal:** Gather raw data from approved sources.

**Process:**
1. Execute research plan using Perplexity API (integrated with Workshop Agent)
2. Conduct user interviews (if applicable)
3. Analyze competitor data
4. Gather pricing intelligence
5. Collect market size estimates

**Output:** Raw data saved to `/data/raw/variant_X/`

**Logging:** Every source must be logged to `/logs/source_log.csv` with:
- Source URL
- Date accessed
- Query used
- Relevance score

**Gate:** Verify sufficient data quality before proceeding.

---

### **Phase 4: Cleaning & Chain-of-Custody**

**Goal:** Validate, clean, and document data provenance.

**Process:**
1. Remove duplicates
2. Verify source credibility
3. Flag contradictory data
4. Normalize formats (dates, currencies, etc.)
5. Document all transformations

**Output:** 
- Cleaned data saved to `/data/clean/variant_X/`
- Cleaning log saved to `/logs/cleaning_log.txt`

**Gate:** Approve data quality before analysis.

---

### **Phase 5: Pain Extraction & Tagging**

**Goal:** Identify and categorize pain points from evidence.

**Questions:**
1. What specific pain points did you find in the evidence?
2. How do you categorize them? (e.g., time waste, cost, frustration, risk)
3. Which pain points are most frequently mentioned?
4. Which pain points have quantifiable impact?

**Output:** `pains_tagged.json`

**Example:**
```json
{
  "pains": [
    {
      "pain_id": "P001",
      "description": "Freelancers miss important client emails in cluttered inbox",
      "category": "time_waste",
      "frequency_mentioned": 45,
      "sources": ["source_1", "source_3", "source_7"],
      "tags": ["email", "organization", "client_communication"]
    }
  ]
}
```

**Gate:** Confirm pain categorization before quantification.

---

### **Phase 6: Pain Quantification**

**Goal:** Score pain points on severity, frequency, and willingness to pay.

**Scoring Dimensions:**
1. **Severity** (1-10): How painful is this problem?
2. **Frequency** (1-10): How often does it occur?
3. **Economic Impact** (€/month): What does this pain cost the user?
4. **Willingness to Pay** (€/month): What would they pay to solve it?

**Output:** `pain_scores.json`

**Example:**
```json
{
  "pain_scores": [
    {
      "pain_id": "P001",
      "severity": 8.5,
      "frequency": 9.0,
      "economic_impact": 450,
      "willingness_to_pay": 25,
      "average_pain_score": 8.75,
      "justification": "Based on 45 user interviews and 12 survey responses",
      "sources": ["source_1", "source_3"]
    }
  ],
  "overall_avg_pain_score": 8.2
}
```

**Logging:** All scoring calculations logged to `/logs/scoring_log.json`

**Gate:** Approve pain scores before market analysis.

---

### **Phase 7: Market & Competition**

**Goal:** Understand market size, growth, and competitive landscape.

**Analysis Areas:**
1. **Total Addressable Market (TAM)**: How big is the market?
2. **Serviceable Addressable Market (SAM)**: How much can you realistically reach?
3. **Serviceable Obtainable Market (SOM)**: What's your realistic Year 1 target?
4. **Competitors**: Who else solves this problem? How?
5. **Market Gaps**: What are competitors missing?

**Output:** `market_competition.md`

**Required Metrics:**
- TAM (€M)
- SAM (€M)
- SOM (€M)
- Market growth rate (% CAGR)
- Top 5 competitors with pricing and market share
- All metrics must include sources

**Gate:** Approve market analysis before economics modeling.

---

### **Phase 8: Unit Economics**

**Goal:** Model the financial viability of this variant.

**Calculations:**
1. **Customer Acquisition Cost (CAC)**: Cost to acquire one customer
2. **Lifetime Value (LTV)**: Revenue per customer over their lifetime
3. **LTV:CAC Ratio**: Must be > 3.0 for viable business
4. **Payback Period**: Months to recover CAC
5. **Break-even Point**: Customers needed to cover fixed costs

**Output:** `unit_economics.json`

**Example:**
```json
{
  "pricing": {
    "monthly_price": 25,
    "annual_price": 240,
    "discount_annual": 20
  },
  "costs": {
    "cac": 60,
    "cac_breakdown": {
      "ads": 30,
      "sales": 20,
      "onboarding": 10
    },
    "cogs_per_customer_monthly": 3,
    "fixed_costs_monthly": 2000
  },
  "metrics": {
    "ltv": 300,
    "ltv_cac_ratio": 5.0,
    "payback_months": 3,
    "break_even_customers": 100,
    "gross_margin": 88
  },
  "assumptions": [
    "Average customer lifetime: 15 months",
    "Churn rate: 6.5% monthly",
    "CAC assumes €30 CPC on Google Ads"
  ],
  "sources": ["competitor_pricing_analysis", "industry_benchmarks"]
}
```

**Gate:** Approve unit economics before risk assessment.

---

### **Phase 9: Feasibility & Risk**

**Goal:** Assess technical feasibility and identify risks.

**Risk Categories:**
1. **Technical Risk**: Can you build it? How complex?
2. **Market Risk**: Will customers buy it?
3. **Competitive Risk**: Can competitors crush you?
4. **Regulatory Risk**: Any compliance issues?
5. **Execution Risk**: Can you as a solo founder deliver this?

**Output:** `feasibility_risk.md`

**Risk Scoring:**
- Each risk scored 1-10 (1 = low risk, 10 = high risk)
- Mitigation strategies for all risks > 5
- All risk assessments must include evidence/sources

**Gate:** Approve risk assessment before GTM planning.

---

### **Phase 10: GTM Options & Prioritisation**

**Goal:** Define go-to-market strategies and prioritize them.

**Strategy Areas:**
1. **Customer Acquisition Channels**: Where will you find customers?
2. **Messaging**: What's your core value proposition?
3. **Pricing Strategy**: How will you price? (freemium, tiered, usage-based)
4. **Launch Sequence**: What to build/launch first?

**Output:** `gtm_options.md`

**Format:**
```markdown
## GTM Strategy 1: Content Marketing + SEO
- **Channels**: Blog, YouTube, SEO
- **Timeline**: 3-6 months to see traction
- **Cost**: €500/month
- **Expected CAC**: €40
- **Pros**: Low cost, scalable, builds authority
- **Cons**: Slow, requires consistent content creation
- **Priority**: High (for solo founder)

## GTM Strategy 2: Paid Ads (Google, LinkedIn)
[... similar structure ...]
```

**Gate:** Approve GTM strategy before synthesis.

---

### **Phase 11: Synthesis (ADSR Report)**

**Goal:** Synthesize all findings into a clear, actionable report.

**ADSR Framework:**
- **Assess**: What did we learn?
- **Decide**: What should we do?
- **Set**: What are the next steps?
- **Review**: What are the open questions?

**Output:** `report_ADSR.md`

**Required Sections:**
1. Executive Summary (3-5 sentences)
2. Key Findings (pain scores, market size, economics, risks)
3. Recommendation (GO / NO-GO / PIVOT)
4. Confidence Level (High / Medium / Low)
5. Next Steps (if GO)
6. Open Questions (what we still don't know)

**Gate:** Approve synthesis before final decision.

---

### **Phase 12: Decision & Logging**

**Goal:** Make final decision and document rationale.

**Decision Options:**
- **GO**: Proceed to build this variant
- **NO-GO**: Abandon this variant
- **PIVOT**: Modify hypothesis and re-run specific phases
- **PARK**: Defer decision pending more information

**Output:** `decision_log.json`

**Example:**
```json
{
  "decision": "GO",
  "confidence": "High",
  "rationale": "Strong pain scores (8.2/10), viable economics (LTV:CAC 5.0), low technical risk, clear GTM path",
  "next_steps": [
    "Build MVP email triage feature (2-3 weeks)",
    "Recruit 10 beta testers from freelance designer communities",
    "Launch on Product Hunt for initial traction"
  ],
  "success_metrics": [
    "10 paying customers within 4 weeks",
    "CAC < €60",
    "Churn < 10% monthly"
  ],
  "approver": "Robert Freyne",
  "timestamp": "2025-10-16T10:30:00Z",
  "evidence_summary": {
    "sources_reviewed": 75,
    "interviews_conducted": 12,
    "surveys_completed": 45
  }
}
```

**Logging:** Decision logged to `/logs/audit_trail.json`

**Gate:** Final approval before moving to comparison (if multiple variants).

---

### **Phase 13: Cross-Variant Comparison & Hybridization**

**Goal:** Compare all completed variants and decide on final approach.

**Process:**
1. Load all variant reports
2. Create comparison matrix
3. Rank variants by success criteria
4. Identify opportunities for hybridization (combining best elements)
5. Make final decision: Advance one variant, create hybrid, or park all

**Output:**
- `reports/comparison_matrix.md`
- `reports/variant_summary.json`
- `reports/variant_rankings.json`
- `reports/hybrid_scope.yaml` (if combining variants)

**Comparison Metrics:**
| Metric | Variant 1 | Variant 2 | Variant 3 |
|---------|-----------|-----------|-----------|
| Avg Pain Score | 8.2/10 | 7.5/10 | 9.1/10 |
| TAM (€M) | €450M | €280M | €620M |
| Payback (months) | 3 | 6 | 4 |
| LTV:CAC | 5.0 | 3.2 | 4.5 |
| Compliance Risk | Low | Medium | Low |
| Technical Feasibility | High | Medium | High |
| Confidence | High | Medium | High |

**Decision Options:**
- **Advance Variant X**: Pick the winner
- **Hybrid**: Combine elements (e.g., Variant 1's ICP + Variant 3's pricing)
- **Park All**: None are viable

**Gate:** Final decision documented in audit trail.

---

## Governance Rules

### 1. **Evidence Requirement**
Every metric must include:
- Source URL or identifier
- Date accessed
- Method of collection
- Confidence level

### 2. **Approval Gates**
Each phase ends with **Confirm / Revise / Park**:
- **Confirm**: Proceed to next phase
- **Revise**: Re-do current phase with new inputs
- **Park**: Defer this variant pending more information

### 3. **Chain of Custody**
All data transformations must be logged:
- What changed?
- Why did it change?
- Who approved the change?
- Timestamp

### 4. **Comparability**
All variants must:
- Use identical phase structure
- Use identical scoring methodology
- Use identical units (€, months, percentages)
- Use identical data sources where possible

### 5. **Audit Trail**
Every decision logged to `/logs/audit_trail.json`:
```json
[
  {
    "variant": "variant_1",
    "phase": 6,
    "decision": "Approved",
    "approver": "Robert Freyne",
    "timestamp": "2025-10-16T09:15:00Z",
    "notes": "Pain scores validated with 45 data points"
  }
]
```

---

## Best Practices

### **Start Small**
Don't try to explore 10 variants. Start with 2-3 focused variants.

### **Be Ruthless**
Park variants early if evidence doesn't support them. Don't waste time on weak hypotheses.

### **Document Assumptions**
Explicitly state all assumptions. Many "facts" are actually assumptions in disguise.

### **Triangulate Evidence**
Don't rely on a single source. Aim for 3+ independent sources per key metric.

### **Update as You Learn**
If new evidence contradicts earlier phases, go back and revise. The SOP is iterative, not linear.

### **Time-box Phases**
Set time limits to avoid analysis paralysis:
- Phases 0-2: 1-2 hours total
- Phases 3-4: 2-4 hours
- Phases 5-6: 1-2 hours
- Phases 7-9: 3-4 hours
- Phases 10-12: 1-2 hours
- Phase 13: 1 hour

**Total per variant: 10-15 hours** (can be done in 2-3 days)

---

## Success Criteria

A variant is considered **ready for Phase 13 comparison** when:
- ✅ All 12 phase files are complete
- ✅ All metrics have sources
- ✅ All approval gates passed
- ✅ Audit trail is complete
- ✅ Confidence level is documented

A variant is considered **GO-ready** when:
- ✅ Avg Pain Score > 7.0/10
- ✅ LTV:CAC > 3.0
- ✅ Payback < 6 months
- ✅ Confidence: High or Medium
- ✅ Clear GTM strategy
- ✅ Solo founder can execute (for your context)

---

## Next Steps

1. Read the [Orchestrator Script](../agent/orchestrator_script.md) to understand execution flow
2. Review the [prompt templates](../agent/prompts/) to see how phases are facilitated
3. Copy the [template folder](../projects/_TEMPLATE_variant/) to start your first variant
4. Run the kick-off prompt to begin Phase 0

---

**Version:** 1.0  
**Last Updated:** 2025-10-16  
**Maintained by:** Robert Freyne

