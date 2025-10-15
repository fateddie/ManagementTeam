# Essential Analysis Questions (Investor-Grade)

**Purpose:** Define the minimal set of questions that provide maximum analytical value  
**Philosophy:** Like an investor analyzing for GO/NO-GO decision  
**Goal:** Improve the product OR kill it if fundamentally flawed

---

## 🎯 **INVESTOR'S CORE QUESTIONS**

When a VC evaluates an idea, they ask these critical questions. Our workshop must answer all of them with evidence:

### **1. MARKET SIZE (Can this be big?)**

**Essential Questions:**

```
Q1: What's the Total Addressable Market (TAM)?
    - Calculation: # of potential customers × average spending
    - Source: Industry reports, analyst forecasts
    - Justification: "X million people spend $Y each = $Z billion TAM"

Q2: What's the Serviceable Addressable Market (SAM)?
    - Calculation: TAM × % you can realistically reach
    - Justification: "Of $X TAM, we can address Y% due to [geography/segment/channel] = $Z SAM"

Q3: What's the Serviceable Obtainable Market (SOM - Year 1)?
    - Calculation: SAM × realistic capture rate
    - Justification: "Competing against [X, Y, Z], we can capture A% in Year 1 = $B SOM"
    - Benchmark: "Similar startups captured X% in Year 1"

Q4: Is the market growing or shrinking?
    - CAGR: X% per year
    - Source: Industry analyst reports
    - Justification: "Market growing because [specific drivers: remote work, AI adoption, etc.]"

Q5: Why is the timing right NOW?
    - What changed recently to make this possible/necessary?
    - Evidence: Technology matured, regulation changed, behavior shifted
```

**Why these questions:**

- Investors need TAM/SAM/SOM to assess if this can be a $100M+ business
- Growth rate determines if they can raise Series A/B
- Timing determines if you're too early (no demand) or too late (competition)

---

### **2. COMPETITORS (Why hasn't someone already won?)**

**Essential Questions:**

```
Q1: Who are the top 3-5 direct competitors?
    - Name specific companies (not "established players")
    - Their metrics: Revenue, users, market share, funding
    - Example: "Google Calendar: 1B users, 80% share, free"

Q2: What does each competitor offer and HOW do they differentiate?
    - Google: What features? Why do people use it? (free, integrated)
    - Motion.ai: What features? Why $34/month? (AI scheduling)
    - Superhuman: What features? Why $30/month? (email speed, UX)
    - Justification: Understand what works and what doesn't

Q3: Who tried and FAILED? Why?
    - Sunrise Calendar: Raised $30M, acquired by Microsoft, shut down - WHY?
    - Mailbox: Acquired by Dropbox, shut down - WHY?
    - Astro: Raised $X, shut down - WHY?
    - Lesson: What does this teach us about this market?

Q4: What's YOUR unfair advantage vs these competitors?
    - Can't just be "different" - must be "10x better" or "uniquely positioned"
    - Evidence: Do you have distribution, technology, insight they don't?
    - Justification: "We can win because [specific advantage they can't replicate]"

Q5: Why haven't the incumbents (Google, Microsoft) already built your solution?
    - If it's valuable, why hasn't Google done it?
    - Possible answers: Different incentives, technical constraints, strategic focus
    - Red flag: If answer is unclear, maybe it's not valuable
```

**Why these questions:**

- Investors need to know you understand the competitive landscape
- Failed startups show what NOT to do
- Unfair advantage determines if you can win
- If Google could easily build this, you probably can't compete

---

### **3. UNIT ECONOMICS (Can this make money?)**

**Essential Questions:**

```
Q1: What's the expected ARPU (Average Revenue Per User)?
    - Calculation: Pricing tier × conversion rate
    - Benchmark: "Competitor X charges $Y, we charge $Z"
    - Justification: "Users will pay $X because [value provided]"

Q2: What's the expected CAC (Customer Acquisition Cost)?
    - Calculation: Marketing spend / new customers
    - Benchmark: "Industry average is $X, we expect $Y because..."
    - Channels: Organic (low CAC) vs paid (high CAC)

Q3: What's the LTV:CAC ratio?
    - Calculation: (ARPU × avg lifetime in months × gross margin) / CAC
    - Target: >3:1 for viability
    - Justification: "Our ratio is X:1 because ARPU=$A, lifetime=B months, CAC=$C"

Q4: What's the payback period?
    - Calculation: CAC / (monthly ARPU × gross margin)
    - Target: <12 months for SaaS
    - Justification: "Takes X months to recover CAC"

Q5: What's the gross margin?
    - Calculation: (Revenue - COGS) / Revenue
    - Target: >70% for SaaS
    - Components: Hosting, APIs, support costs
```

**Why these questions:**

- LTV:CAC >3:1 is minimum for investor interest
- Payback <12 months means sustainable growth
- Gross margin >70% means scalable business

---

### **4. RISKS (What could kill this?)**

**Essential Questions:**

```
Q1: What's the #1 risk that could kill this idea?
    - Probability: X% (based on comparable failures)
    - Impact: $Y (show calculation)
    - Evidence: "Z% of similar startups faced this and X% failed"

Q2: Can this risk be mitigated? How? At what cost?
    - Solution: Specific action
    - Cost: $ and time
    - Risk reduction: X% → Y%
    - Justification: "This worked for Competitor Z who faced same risk"

Q3: What assumptions must be true for this to work?
    - List all critical assumptions
    - How would you test each assumption?
    - Cost to validate: $X per assumption

Q4: What's the cost of being WRONG about this idea?
    - Development: $X
    - Opportunity cost: $Y (6 months × alternative revenue)
    - Total: $Z wasted if this fails
    - Justification: Show the math
```

**Why these questions:**

- Investors want to know you've thought about failure scenarios
- Mitigation strategies show you're not naive
- Cost of being wrong determines if it's worth the risk

---

### **5. DIFFERENTIATION (Why you vs existing solutions?)**

**Essential Questions:**

```
Q1: What makes this 10x better (not just different)?
    - Specific: "10x faster", "1/10th the cost", "10x better accuracy"
    - Evidence: How measured? Compared to what?
    - Justification: "Users currently spend X hours, we reduce to X/10"

Q2: Can competitors copy this? How long would it take?
    - Google: Could they add this feature? Timeline?
    - Motion.ai: Could they replicate? What stops them?
    - Assessment: If easy to copy, not defensible

Q3: What creates a sustainable moat?
    - Network effects: Value increases with users
    - Data moat: Proprietary data competitors can't access
    - Switching costs: Hard for users to leave
    - Justification: Quantify the moat strength

Q4: Why hasn't this been done already?
    - If idea is obvious, why doesn't it exist?
    - Possible: Technology just matured, market just emerged, incumbents have wrong incentives
    - Red flag: If no good answer, maybe it's not viable
```

**Why these questions:**

- "Different" isn't enough - must be "better" in meaningful way
- Defensibility determines long-term value
- If it's obvious and unbuilt, there's usually a reason

---

## 📊 **OPTIMAL QUESTION SET FOR WORKSHOP**

### **6 Perplexity Queries (Essential Only):**

```python
queries = {
    # Q1-3: Market Size
    "market_size_and_growth":
        "What's the TAM, SAM for {industry} in 2025? Include market size, growth rate (CAGR),
         and key market drivers. Where is this market coming from?",

    # Q1-4: Competitors
    "competitor_analysis":
        "Who are the top 5 competitors for {title}? For each: company name, market share %,
         revenue, users, pricing, key features, and their main differentiator. Include Google
         Calendar, Motion.ai, Superhuman, Reclaim.ai if relevant.",

    # Q2-3: Failed Competitors
    "failed_competitors":
        "What {industry} startups failed in last 5 years? Include Sunrise Calendar, Mailbox,
         Astro. For each: funding raised, why they failed, what lessons can be learned. Be specific.",

    # Q3: Unit Economics
    "unit_economics_benchmarks":
        "What's the average ARPU, CAC, LTV:CAC ratio, churn rate, and gross margin for
         successful {industry} SaaS products? Cite industry benchmarks and specific companies.",

    # Q4: Risks
    "market_risks":
        "What are the biggest risks for new entrants in {industry}? What % of startups fail
         and why? What competitive barriers exist (Google's advantages, network effects, etc.)?",

    # Q5: Market Direction
    "future_outlook":
        "Where is {industry} market headed in next 2-3 years? What emerging technologies,
         customer needs are unmet, and what opportunities exist? What trends are growing vs declining?"
}
```

**Result:** 6 focused queries instead of 10 = **~2 minutes** instead of ~3 minutes

---

### **Fix 2: Simplify Round 3 Justification Format**

**Current (Too Complex):**

```json
"revenue_justification": {
  "question_1_market_size": "...",
  "question_2_current_arpu": "...",
  "question_3_new_arpu": "...",
  "question_4_customer_increase": "...",
  "question_5_calculation": "...",
  "question_6_timeframe": "..."
}
```

**Optimized (Essential Only):**

```json
"revenue_justification": "Market size: $X. Capture rate: Y%. ARPU: $Z. Calculation: $X × Y% × $Z = revenue. Benchmark: Competitor A has $B ARPU."
```

**Why:**

- Still shows calculation
- Still provides evidence
- Much faster for LLM to generate
- Easier for humans to read

---

## 🎯 **IMPLEMENTATION PLAN**

**Shall I implement these optimizations?**

**Changes:**

1. ✅ Reduce Perplexity queries: 10 → 6 (keep most valuable)
2. ✅ Simplify Round 3 justification format (single string vs nested objects)
3. ✅ Increase timeout: 30s → 60s
4. ✅ Keep Round 1 & 2 detailed (foundation)
5. ✅ Make Round 3 lighter (builds on previous rounds)

**Expected Results:**

- **Speed:** 3-6 min → 2-3 min (40-50% faster)
- **Reliability:** Fewer timeouts
- **Quality:** Maintained (asking the RIGHT questions)
- **Usability:** Easier to read and understand

**This maintains analytical rigor while improving efficiency!**
