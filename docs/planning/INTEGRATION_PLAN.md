# Integration Plan: Evidence-Based Critique Into Existing System

**Goal:** Add data-driven, evidence-based critique without duplicating existing scoring  
**Approach:** Enhance current agents + add new CriticAgent as "reality check" layer

---

## 🎯 Current System Analysis

### What We Have:
```
RefinementAgent → scoring_prompts → VerticalAgent → OpportunityRankingAgent
    (gentle)         (subjective)      (user scores)      (weighted scores)
```

### What We Need:
```
RefinementAgent → **CriticAgent** → scoring_prompts → VerticalAgent → OpportunityRankingAgent
    (refine)      (CHALLENGE + DATA)   (validate)       (score)          (rank)
```

---

## 🔄 Integration Strategy

### Option A: **Enhance Existing Agents** (Faster - 1 week)

Modify existing prompts to require evidence:

#### 1. Update `scoring_prompts.py`:
```python
SCORE_PROMPT = """
You are a VC analyst scoring startup ideas.

For EACH dimension, you MUST provide:
1. Score (0-10)
2. Evidence (competitor data, market research, or comparable)
3. Risk assessment (what could make this score wrong?)

Example:
{
  "Market Size": {
    "score": 7,
    "evidence": "Productivity software market = $96.36B (Grand View Research, 2024). Voice assistant subset = $4.2B, growing 18% CAGR.",
    "risk": "Voice adoption may plateau if accuracy doesn't improve (15% probability)",
    "comparable": "Otter.ai ($50M ARR) proves voice transcription market exists"
  }
}
```

#### 2. Update `RefinementAgent` critique field:
Add `brutal_assessment` section:
```python
{
  "critique": "...",  # Keep existing gentle critique
  "brutal_assessment": {
    "fatal_flaws": [
      {
        "flaw": "Voice UX requires $50K+ investment",
        "evidence": "Voice AI startups average $120K MVP cost (2024 survey)",
        "probability_kills_project": "40%"
      }
    ],
    "comparable_failures": [
      {
        "company": "Clara Labs",
        "raised": "$8M",
        "failed": "2022",
        "reason": "Email assistant market too competitive",
        "similarity_to_your_idea": "85%"
      }
    ]
  }
}
```

**Pros:**
- Uses existing structure
- Faster implementation
- No new agent to maintain

**Cons:**
- Makes existing agents more complex
- Mixes refinement with critique (different purposes)

---

### Option B: **Add Dedicated CriticAgent** (Better - 2 weeks)

Keep existing agents focused, add new specialized critique layer:

```
Flow:
1. RefinementAgent - Refines vague idea (UNCHANGED)
2. 🆕 CriticAgent - Challenges with data (NEW)
   - Pulls competitor data
   - Estimates costs
   - Finds comparable failures
   - Quantifies risks
   - GO/NO-GO recommendation
3. User Decision Point (NEW)
4. scoring_prompts - Scores if user proceeds (UNCHANGED)
5. VerticalAgent - RICE scoring (UNCHANGED)
6. OpportunityRankingAgent - Advanced ranking (UNCHANGED)
```

**Implementation:**

```python
# agents/critic_agent/critic_agent.py

class CriticAgent(BaseAgent):
    """
    Evidence-based critique with data sources.
    Challenges assumptions before scoring/planning.
    """
    
    def execute(self, context: AgentContext) -> AgentOutput:
        refined_idea = context.get_input("refined_idea")
        
        # 1. Gather evidence
        market_data = self._research_market_size(refined_idea)
        competitors = self._find_competitors(refined_idea)
        similar_failures = self._find_failed_companies(refined_idea)
        cost_estimate = self._estimate_costs(refined_idea)
        
        # 2. Generate critique with data
        critique = {
            "cost_of_bad_idea": cost_estimate,
            "market_analysis": market_data,
            "competitors": competitors,
            "failed_examples": similar_failures,
            "red_flags": self._identify_risks(refined_idea, competitors),
            "tough_questions": self._generate_questions(refined_idea),
            "recommendation": self._make_recommendation(refined_idea, competitors, market_data)
        }
        
        # 3. Return as AgentOutput
        return AgentOutput(
            agent_name="CriticAgent",
            decision="conditional_approve" if critique['recommendation'] == 'CONDITIONAL_GO' else "approve",
            reasoning=critique['recommendation']['reasoning'],
            data_for_next_agent=critique,
            confidence=0.85,
            metadata={
                "data_sources": ["competitor_analysis", "market_research", "cost_estimation"],
                "critique_saved_to": "data/critiques/latest.md"
            }
        )
    
    def _research_market_size(self, idea):
        """Pull real market data or use LLM to estimate with sources"""
        # Could integrate with:
        # - Statista API
        # - CB Insights data
        # - LLM with prompt: "Research [market] size. Cite sources."
        pass
    
    def _find_competitors(self, idea):
        """Find real competitors with revenue/user data"""
        # Could integrate with:
        # - Crunchbase API
        # - SimilarWeb
        # - LLM search: "List top 5 competitors to [idea] with revenue data"
        pass
    
    def _find_failed_companies(self, idea):
        """Find similar companies that failed"""
        # Could use:
        # - Crunchbase (companies that shut down)
        # - LLM: "Find failed startups similar to [idea]. Why did they fail?"
        pass
    
    def _estimate_costs(self, idea):
        """Calculate realistic MVP and operating costs"""
        features = idea.get('key_features', [])
        tech_stack = idea.get('technical_requirements', {})
        
        # Cost model based on features
        costs = {
            "email_integration": 80 * 100,  # hours * rate
            "voice_interface": 120 * 100,
            "mobile_app": 200 * 100,
            # ...
        }
        
        return {
            "mvp_cost": sum(costs.values()),
            "monthly_burn": self._calculate_operating_costs(tech_stack),
            "time_to_mvp": "6-8 months",
            "total_risk": sum(costs.values()) + (8 * monthly_burn)
        }
```

**Pros:**
- Clean separation of concerns
- Reusable across projects
- Doesn't touch existing agents
- Can be toggled on/off

**Cons:**
- New agent to maintain
- Adds one more step to workflow

---

## 🎯 **RECOMMENDED APPROACH:**

**Option B: Add CriticAgent**

**Why:**
1. Your existing agents are working well - don't break them
2. Critique is a DIFFERENT purpose than scoring
3. Makes workflow more educational (step-by-step)
4. Can be optional (--skip-critique flag)

**Implementation Timeline:**

```
Week 1: Core CriticAgent
- [ ] Create agent class
- [ ] Build evidence-based prompt
- [ ] Cost estimation logic
- [ ] Competitor research (LLM-based initially)
- [ ] Output format (markdown report)

Week 2: Integration & Enhancement
- [ ] Integrate into workflow (after RefinementAgent)
- [ ] Add user decision prompts
- [ ] Test with 5 real ideas
- [ ] Add data source integrations (optional)
- [ ] Documentation

Week 3: Optional Enhancements
- [ ] Crunchbase API integration
- [ ] Market size database
- [ ] Failure pattern database
- [ ] Automated cost modeling
```

---

## 📊 Enhanced Workflow Example

### **asksharon.ai Example:**

```
1. USER INPUT:
   "Voice-first AI assistant for entrepreneurs..."

2. REFINEMENT AGENT: ✅
   Refined Concept:
   - Title: "asksharon.ai"
   - Target: Busy entrepreneurs
   - Features: Email + Calendar + Coaching + Voice
   
3. 🆕 CRITIC AGENT (NEW):
   
   💰 COST OF PROCEEDING IF BAD IDEA:
   - MVP: $50,000 (6 months)
   - Operating: $2,500/month
   - Total Risk: $65,000 + 6 months
   
   🏆 COMPETITORS (Real Data):
   - Motion.ai: $10M ARR, 50K users, $15/mo
   - Reclaim.ai: $5M ARR, 25K users, $10/mo
   - Both added voice in 2024 ← YOUR "unique" feature exists
   
   📊 MARKET DATA:
   - TAM: $4.2B (voice productivity), 18% CAGR
   - SAM: ~500K entrepreneurs (addressable)
   - SOM Year 1: 100-500 customers (realistic)
   
   🚨 RED FLAGS:
   1. Scope too broad (6 different apps)
      - Probability of failure: 70%
      - Cost if fails: $50K + 6 months
   
   2. Voice UX underestimated
      - Similar failures: Clara Labs ($8M raised, failed 2022)
      - Mitigation cost: $20K for voice specialist
   
   ❓ TOUGH QUESTIONS (Must answer with evidence):
   1. Have you interviewed 10 entrepreneurs willing to pay $20/mo?
      Without this: 80% chance of no market fit
   
   2. Why can't Motion add your features in 6 weeks?
      Without moat: 60% chance of being crushed
   
   🎯 RECOMMENDATION: CONDITIONAL GO (32/50 score)
   
   CONDITIONS TO PROCEED:
   - [ ] Interview 10 users (get 5 to commit)
   - [ ] Narrow to ONE feature for MVP
   - [ ] Build voice prototype in 1 week
   - [ ] Budget: $5K validation BEFORE $50K MVP
   
4. USER DECISION:
   > Proceed? (yes/no/pivot): [User responds]
   
   [If yes, continue to scoring...]
   
5. SCORING PROMPTS: ✅
   [Existing 6-dimension scores]
   
6. VERTICAL AGENT: ✅
   [RICE scoring]
   
7. OPPORTUNITY RANKING: ✅
   [7-criteria weighted]
```

---

## 🎛️ Configuration

```yaml
# config/critic_agent.yaml

critic:
  enabled: true
  mode: "brutal"  # brutal | balanced | gentle
  
  require_evidence: true
  min_data_sources: 2  # Require at least 2 cited sources
  
  cost_estimation:
    hourly_rate: 100
    include_opportunity_cost: true
  
  competitor_research:
    max_competitors: 5
    require_revenue_data: true
  
  failure_analysis:
    find_similar_failures: true
    max_examples: 3
  
  decision_thresholds:
    go_score: 40  # /50
    conditional_go_score: 30
    below_30: "NO_GO"
```

---

## 🚀 Quick Start (Once Built)

```bash
# Full workflow with critique
python cli/manage.py guided --with-critique

# Skip critique (use existing scoring only)
python cli/manage.py guided --skip-critique

# Critique only (for existing refined ideas)
python scripts/critique_idea.py data/refined/asksharon_ai.json
```

---

**Decision Point:** Should we build Option A (enhance existing) or Option B (new CriticAgent)?

**My Recommendation:** Option B - keeps your working system intact, adds powerful new capability.

**Next Step:** Start with Week 1 implementation?

