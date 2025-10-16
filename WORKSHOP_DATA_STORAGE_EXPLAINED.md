# Workshop Agent Data Storage - Where Everything Is

## 📁 **Where Are Workshop Results Stored?**

### **The Current Situation:**

The Workshop Agent results are **NOT permanently saved to disk** by default. They are passed through the agent pipeline in **memory only**. Here's what is and isn't saved:

---

## ✅ **WHAT IS SAVED:**

### **1. Logs (Complete Execution History)**

**Location:** `/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/logs/workshop_agent.log`

**What's Captured:**

- Timestamp of each run
- Which rounds executed (Round 1, 2, 3)
- Perplexity queries and source counts
- Initial and final viability scores
- Improvement calculations

**Last Run (from logs):**

```
2025-10-16 00:17:45 | Workshop complete: 29 → 41 (+12)
```

**View Recent Runs:**

```bash
tail -100 logs/workshop_agent.log
```

**View Specific Run:**

```bash
grep "Workshop complete" logs/workshop_agent.log
```

### **2. Refined Ideas (Input to Workshop)**

**Location:** `/Users/robertfreyne/Documents/ClaudeCode/ManagementTeam/data/refined/refined_ideas.json`

**What's Captured:**

- Original raw idea
- Refined title, description, target customer
- Value proposition
- Critique and clarifying questions
- Refinement timestamp

**Example from Your Runs:**

```json
{
  "title": "Holistic Personal Assistant App",
  "description": "All-in-one assistant with email, calendar, coaching...",
  "target_customer": "Busy professionals aged 25-45...",
  "refined_at": "2025-10-15T23:31:51.672771"
}
```

**Latest entry** in this file is the most recent refined idea that went through the workshop.

---

## ❌ **WHAT IS NOT SAVED (Currently):**

### **1. Workshop Reasoning & Analysis**

- ❌ Round 1 assessment details (risks, opportunities, scores)
- ❌ Round 2 risk mitigation solutions
- ❌ Round 3 opportunity capture strategies
- ❌ LLM's thinking process and justifications
- ❌ Perplexity sources and URLs

**Why Not Saved:**
The workshop agent returns this data via `AgentOutput.data_for_next_agent` for the next agent in the pipeline, but it's **not persisted to disk**.

### **2. User Feedback to LLM**

- ❌ Your responses to workshop recommendations
- ❌ Choices you make during the process
- ❌ Whether you accepted or rejected suggestions

**Why Not Captured:**
The current system is **non-interactive** - it runs the complete analysis automatically and outputs results. It doesn't wait for user input during execution.

---

## 🔍 **HOW TO SEE YOUR LAST WORKSHOP RESULTS:**

### **Option 1: View Logs (High-Level Summary)**

```bash
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam
tail -50 logs/workshop_agent.log | grep -E "(Workshop complete|Round|Retrieved)"
```

**Output:**

```
Round 1: Quick Assessment
Retrieved pain_validation: 9 sources
Retrieved competitor_analysis: 16 sources
... [more queries]
Round 2: Risk Mitigation
Round 3: Opportunity Capture
Workshop complete: 29 → 41 (+12)
```

### **Option 2: Re-Run Workshop (Get Fresh Analysis)**

```bash
cd /Users/robertfreyne/Documents/ClaudeCode/ManagementTeam
source venv/bin/activate
python scripts/run_idea_to_project.py "Your idea here"
```

This will:

- Refine your idea
- Run the 3-round workshop
- Display complete reasoning on screen
- Save refined idea to `data/refined/refined_ideas.json`

### **Option 3: Check Refined Ideas (Input Data)**

```bash
cat data/refined/refined_ideas.json | jq '.[-1]'  # Last refined idea
```

Or view the entire file to see all ideas you've refined.

---

## 💡 **GAP: User Feedback Is Not Captured**

### **Current Flow:**

```
User Input (Idea)
    ↓
RefinementAgent (refines idea)
    ↓
WorkshopAgent (analyzes, scores, recommends)
    ↓
Results displayed on screen
    ↓
[END - No user feedback captured]
```

### **What's Missing:**

1. **No interactive prompts** - Workshop doesn't ask "Do you agree with this assessment?"
2. **No decision tracking** - System doesn't know if you chose to proceed or pivot
3. **No feedback loop** - Your insights aren't fed back to improve future analyses

### **Your Earlier Request:**

You said: _"I want the application to educate me at each step, ask for review, and prompt for confirmation before proceeding."_

**Status:** This feature was **designed** (see `docs/planning/INTERACTIVE_GUIDE_FEATURE.md`) but **not yet implemented**.

---

## 🛠️ **SOLUTIONS TO CAPTURE WORKSHOP RESULTS:**

### **Short-Term Solution (Immediate):**

**Save workshop output to file manually:**

```python
# Add to scripts/run_idea_to_project.py
import json
from datetime import datetime

# After workshop execution:
workshop_output = {
    "timestamp": datetime.now().isoformat(),
    "idea": idea_description,
    "initial_score": workshop_result.data_for_next_agent["initial_score"],
    "final_score": workshop_result.data_for_next_agent["final_score"],
    "improvement": workshop_result.data_for_next_agent["improvement"],
    "recommendation": workshop_result.data_for_next_agent["recommendation"],
    "risks": workshop_result.data_for_next_agent.get("risks", []),
    "opportunities": workshop_result.data_for_next_agent.get("opportunities", []),
    "market_data": workshop_result.data_for_next_agent.get("market_data", {}),
    "reasoning": workshop_result.reasoning
}

# Save to file
output_dir = "data/workshops"
os.makedirs(output_dir, exist_ok=True)
filename = f"{output_dir}/workshop_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(filename, 'w') as f:
    json.dump(workshop_output, f, indent=2)

print(f"Workshop results saved to: {filename}")
```

### **Medium-Term Solution (1-2 days work):**

**Create Workshop Storage System:**

```python
# New file: agents/workshop_agent/storage.py

class WorkshopStorage:
    """Persist workshop results to disk and database."""

    def __init__(self, storage_dir="data/workshops"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_workshop_session(self, idea, round_1, round_2, round_3):
        """Save complete workshop session with all reasoning."""
        session = {
            "timestamp": datetime.now().isoformat(),
            "idea": idea,
            "round_1_assessment": round_1,
            "round_2_risk_mitigation": round_2,
            "round_3_opportunity_capture": round_3,
            "sources": self._extract_sources(round_1, round_2, round_3)
        }

        # Save as JSON
        filename = f"{self.storage_dir}/session_{session['timestamp']}.json"
        with open(filename, 'w') as f:
            json.dump(session, f, indent=2)

        # Also save as Markdown for easy reading
        md_filename = f"{self.storage_dir}/session_{session['timestamp']}.md"
        self._save_as_markdown(session, md_filename)

        return filename, md_filename

    def get_latest_session(self):
        """Retrieve the most recent workshop session."""
        files = sorted(glob.glob(f"{self.storage_dir}/session_*.json"))
        if files:
            with open(files[-1], 'r') as f:
                return json.load(f)
        return None
```

### **Long-Term Solution (Interactive System):**

**Implement Interactive Workshop with Feedback Capture:**

```python
# New file: agents/workshop_agent/interactive.py

class InteractiveWorkshop:
    """Interactive workshop that captures user feedback."""

    def run_with_feedback(self, idea):
        """Run workshop with user interaction at each step."""

        # Round 1: Assessment
        round_1 = self.execute_round_1(idea)
        print("\n" + "="*70)
        print("ROUND 1: QUICK ASSESSMENT")
        print("="*70)
        self._display_results(round_1)

        # Get user feedback
        feedback_1 = self._prompt_user_feedback([
            "Do you agree with these risk assessments? (yes/no/partially)",
            "Are there risks we missed?",
            "Do these opportunities make sense for your situation?"
        ])

        # Save feedback
        self.storage.save_feedback(idea, "round_1", feedback_1)

        # Round 2: Risk Mitigation
        round_2 = self.execute_round_2(idea, round_1, feedback_1)
        # ... repeat with user prompts ...

        # Round 3: Opportunity Capture
        round_3 = self.execute_round_3(idea, round_1, round_2, feedback_1, feedback_2)
        # ... repeat with user prompts ...

        # Final decision
        final_decision = self._prompt_final_decision([
            "Do you want to proceed with this idea? (yes/no/pivot)",
            "If yes, which strategy will you pursue first?",
            "If pivot, what would you change?"
        ])

        # Save complete session with user feedback
        self.storage.save_complete_session(
            idea, round_1, round_2, round_3,
            feedback_1, feedback_2, final_decision
        )
```

---

## 📊 **WHAT YOU CAN SEE RIGHT NOW:**

### **From Logs:**

```bash
# See all workshop runs
grep "Workshop complete" logs/workshop_agent.log

# Output:
2025-10-16 00:04:55 | Workshop complete: 33 → 41 (+8)
2025-10-16 00:12:12 | Workshop complete: 30 → 41 (+11)
2025-10-16 00:17:45 | Workshop complete: 29 → 41 (+12)
```

**Your Last Run:**

- **Idea:** Personal assistant with email and calendar management (last refined idea in `refined_ideas.json`)
- **Initial Score:** 29/50 (needs improvement)
- **Final Score:** 41/50 (viable with conditions)
- **Improvement:** +12 points (41% improvement)
- **Time:** 2025-10-16 00:17:45

### **From Refined Ideas:**

```bash
# See your last refined idea
cat data/refined/refined_ideas.json | jq '.[-1]'
```

This shows the **input** to the workshop (title, description, target customer, etc.).

### **Missing:**

- ❌ Detailed risk analysis from Round 1
- ❌ Mitigation solutions from Round 2
- ❌ Opportunity strategies from Round 3
- ❌ LLM's reasoning and justifications
- ❌ Perplexity sources (URLs for verification)
- ❌ Your feedback/decisions

---

## 🚀 **RECOMMENDATION:**

**Immediate Action (5 minutes):**

1. Run workshop again and capture screen output:
   ```bash
   python scripts/run_idea_to_project.py "Your idea" | tee workshop_results.txt
   ```

**Short-Term (30 minutes):** 2. I can modify `workshop_agent.py` to automatically save results to `data/workshops/`

**Medium-Term (1-2 days):** 3. Implement proper workshop storage system with:

- JSON storage for structured data
- Markdown storage for human-readable reports
- Source tracking with URLs
- Session history and comparison

**Long-Term (1 week):** 4. Implement interactive workshop that:

- Pauses after each round
- Asks for your feedback
- Records your decisions
- Adapts analysis based on your input

---

## ❓ **YOUR QUESTIONS ANSWERED:**

### **Q1: Where are the reasoning from the last run stored?**

**A:** Only in:

- **Logs** (high-level summary): `logs/workshop_agent.log`
- **Screen output** (if you saved it)
- **Memory** (passed to next agent, then lost)

**Not saved:** Detailed reasoning, risks, opportunities, strategies, sources.

### **Q2: Is feedback from me to the LLM captured?**

**A:** **No.** Currently the system:

- ❌ Doesn't prompt for feedback
- ❌ Doesn't capture your decisions
- ❌ Doesn't track whether you accepted/rejected recommendations
- ❌ Doesn't use your input to improve future analyses

**This was identified as a gap** and designed (see `docs/planning/INTERACTIVE_GUIDE_FEATURE.md`) but not yet implemented.

---

## 💡 **NEXT STEPS:**

**Want me to:**

1. ✅ **Modify workshop agent to save results automatically?** (30 minutes)
2. ✅ **Create a script to view last workshop session?** (15 minutes)
3. ✅ **Implement interactive workshop with feedback capture?** (1-2 days)
4. ✅ **Show you how to manually save results for now?** (5 minutes)

Let me know which you'd prefer!
