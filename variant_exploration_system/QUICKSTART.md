# Variant Exploration System - QUICKSTART GUIDE

## 🎯 **YOU'RE READY TO GO!**

The complete Variant Exploration System is now installed and ready to use.

---

## 📁 **WHAT YOU HAVE**

```
/variant_exploration_system/
├── README.md                     ✅ System overview
├── QUICKSTART.md                 ✅ This guide
├── orchestrator.py               ✅ Interactive runner
├── SOP/
│   └── variant_exploration_SOP.md  ✅ Complete 13-phase methodology
├── agent/
│   ├── orchestrator_script.md      ✅ Orchestrator logic
│   ├── state_schema.json           ✅ State tracking
│   └── prompts/
│       ├── kick_off.txt            ✅ Phase 0 prompt
│       ├── variant_generation.txt  ✅ Variant suggestions
│       ├── phase_template.txt      ✅ Generic phase template
│       └── comparison_prompt.txt   ✅ Cross-variant comparison
├── projects/
│   └── _TEMPLATE_variant/          ✅ Copy this for each variant
│       ├── idea_intake.json
│       ├── scope.yaml
│       ├── research_plan.md
│       └── [9 more template files]
├── reports/                        (empty - generated during comparison)
├── data/
│   ├── raw/                        (empty - filled during Phase 3)
│   ├── clean/                      (empty - filled during Phase 4)
│   └── processed/                  (empty - filled during analysis)
└── logs/                           (empty - filled during execution)
```

---

## 🚀 **START YOUR FIRST VARIANT EXPLORATION**

### **Step 1: Run the Orchestrator**

```bash
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/variant_exploration_system
python orchestrator.py
```

This will:
- Start the interactive 13-phase workflow
- Create `variant_1/` folder automatically
- Guide you through each phase with prompts
- Save all your inputs to structured files
- Log all decisions to `logs/audit_trail.json`

### **Step 2: Answer the Kick-Off Questions**

You'll be asked:

1️⃣ **Your base idea** (one sentence)
   - Example: "AI-powered personal assistant for busy entrepreneurs"

2️⃣ **Regions/markets** to explore
   - Example: "North America, Europe" or "Global"

3️⃣ **Success criteria**
   - Example: "Payback < 12 months, LTV:CAC > 3.0, 10 paying customers in Month 1"

4️⃣ **Key assumptions/risks**
   - Example: "Assumes solo founders will pay €25/month, Risk: Google competition"

### **Step 3: Go Through Each Phase**

For each phase (1-12), you'll:
1. See the phase name and instructions
2. Provide your analysis/data
3. Choose: **Confirm** (continue) / **Revise** (redo) / **Park** (pause)

**Tip:** Type `END` on a new line to finish multi-line input.

### **Step 4: Review Your Outputs**

All data is saved to:
```
/variant_exploration_system/projects/variant_1/
├── idea_intake.json        (Phase 0)
├── scope.yaml              (Phase 1)
├── research_plan.md        (Phase 2)
├── pains_tagged.json       (Phase 5)
├── pain_scores.json        (Phase 6)
├── market_competition.md   (Phase 7)
├── unit_economics.json     (Phase 8)
├── feasibility_risk.md     (Phase 9)
├── gtm_options.md          (Phase 10)
├── report_ADSR.md          (Phase 11)
└── decision_log.json       (Phase 12)
```

---

## 🔄 **EXPLORE MULTIPLE VARIANTS**

### **Run Variant 2:**

```bash
python orchestrator.py --variant variant_2
```

This creates and runs through variant_2.

### **Run Variant 3:**

```bash
python orchestrator.py --variant variant_3
```

---

## 📊 **COMPARE ALL VARIANTS**

After completing 2+ variants, run:

```bash
python orchestrator.py --compare
```

This will:
- Load all completed variants
- Generate comparison matrix
- Show side-by-side metrics
- Save to `reports/comparison_matrix.md`
- Prompt you to: Advance one, Combine into hybrid, or Park all

---

## 💡 **EXAMPLE: Personal Assistant Idea**

Let me show you a complete example:

### **Kick-Off Input:**

```
1️⃣  Base idea:
AI-powered personal assistant that manages email, calendar, and daily routines

2️⃣  Regions:
North America, Europe

3️⃣  Success criteria:
- Payback < 6 months
- LTV:CAC > 3.0
- 50 paying customers in Year 1
- €30K ARR minimum

4️⃣  Assumptions/Risks:
- Assumes busy professionals will pay €20-30/month
- Risk: Google Calendar dominates calendar space
- Assumption: Can build MVP in 2-3 weeks as solo founder
```

### **Generated Variants:**

**Variant 1: Email Management for Freelance Designers**
- ICP: Freelance designers ages 25-40
- Problem: Miss client emails in cluttered inbox
- Unique Angle: Integration with Behance, Dribbble portfolios

**Variant 2: Calendar for ADHD Entrepreneurs**
- ICP: Entrepreneurs with ADHD
- Problem: Forget meetings, poor time management
- Unique Angle: Dopamine-driven reminders, task gamification

**Variant 3: Morning Routine Coach for Busy Parents**
- ICP: Parents of young children
- Problem: Chaotic mornings, no structure
- Unique Angle: Voice-first, kid-friendly interface

### **After 13 Phases:**

| Metric | Variant 1 | Variant 2 | Variant 3 |
|---------|-----------|-----------|-----------|
| Avg Pain Score | 8.2/10 | 9.1/10 | 7.5/10 |
| TAM (€M) | €450M | €280M | €620M |
| Payback (months) | 3 | 6 | 8 |
| LTV:CAC | 5.0 | 3.2 | 4.5 |
| Decision | GO | PIVOT | NO-GO |

**Final Decision:** Advance Variant 1 (email for designers)

---

## 🎓 **TIPS FOR SUCCESS**

### **1. Be Evidence-Based**
- Don't guess - cite sources (URLs, surveys, interviews)
- Every metric needs a justification
- "I think X" → "Data shows X [Source #1, #2]"

### **2. Time-Box Each Phase**
- Don't spend more than 1-2 hours per phase
- Set a timer if needed
- Perfect is the enemy of good

### **3. Park Weak Variants Early**
- If evidence doesn't support it, park it at Phase 7
- Don't waste time on variants with obvious fatal flaws
- You can always resume later

### **4. Use the Template Files**
- The template files show you what format to use
- JSON files should be valid JSON
- YAML files should follow YAML syntax
- Markdown files can be freeform

### **5. Document Assumptions**
- Explicitly state every assumption
- Most "facts" are actually assumptions in disguise
- Example: "Assuming €30 CPC on Google Ads" vs "CPC will be €30"

---

## 🔗 **INTEGRATION WITH EXISTING WORKSHOP AGENT**

The Variant Exploration System **works alongside** your existing Workshop Agent:

**Phase 3 (Evidence Collection):** Can call Workshop Agent's Perplexity integration
```python
# In orchestrator.py, Phase 3 can trigger:
from agents.workshop_agent.workshop_agent import IterativeWorkshopAgent
workshop = IterativeWorkshopAgent()
market_data = workshop._gather_market_data(variant_idea)
```

This gives you:
- ✅ 75+ sources per variant
- ✅ Chain-of-Thought reasoning
- ✅ Solo founder optimization
- ✅ Evidence-based recommendations

---

## ⏸️  **RESUME A PARKED VARIANT**

If you parked a variant at Phase 6:

```bash
python orchestrator.py --variant variant_1
```

The orchestrator will:
- Load saved state from `agent/state_schema.json`
- Resume at Phase 6
- Continue where you left off

---

## 📋 **NEXT STEPS**

### **For Your Personal Assistant Idea:**

1. **Run Variant 1:** Email management for freelancers
   ```bash
   python orchestrator.py --variant email_for_freelancers
   ```

2. **Run Variant 2:** Calendar for ADHD entrepreneurs
   ```bash
   python orchestrator.py --variant calendar_for_adhd
   ```

3. **Run Variant 3:** Morning coach for parents
   ```bash
   python orchestrator.py --variant morning_coach
   ```

4. **Compare all three:**
   ```bash
   python orchestrator.py --compare
   ```

5. **Pick the winner or create hybrid**

---

## 🐛 **TROUBLESHOOTING**

### **"ModuleNotFoundError" when running orchestrator**

Make sure you're in the right directory:
```bash
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/variant_exploration_system
python orchestrator.py
```

### **"File not found" errors**

The orchestrator creates missing directories automatically. If you see errors, check:
```bash
ls -la projects/
ls -la agent/prompts/
```

### **Want to start fresh?**

Delete the variant folder and run again:
```bash
rm -rf projects/variant_1
python orchestrator.py --variant variant_1
```

---

## 📚 **LEARN MORE**

- **Full methodology:** Read `SOP/variant_exploration_SOP.md`
- **Orchestrator logic:** Read `agent/orchestrator_script.md`
- **System overview:** Read `README.md`

---

## ✅ **YOU'RE READY!**

**Run your first variant exploration NOW:**

```bash
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/variant_exploration_system
python orchestrator.py
```

**The system will guide you through everything step-by-step!** 🚀

---

**Questions? Issues? Want to extend the system?**

All code is in:
- `orchestrator.py` - Main orchestrator logic
- `agent/prompts/*.txt` - Prompt templates (customize these!)
- `SOP/variant_exploration_SOP.md` - Complete methodology

**Happy exploring!** 🎯

