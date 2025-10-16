# Interactive User Guidance System - Feature Specification

**Feature Name:** Interactive Project Wizard  
**Target Users:** New users of the AI Management Team system  
**Goal:** Make the idea-to-project pipeline educational, transparent, and user-friendly  
**Priority:** High - improves user experience significantly

---

## 🎯 Problem Statement

**Current State:**

- Users run CLI commands with minimal feedback
- No explanation of what each agent does
- Files created silently - users don't know what to review
- No opportunity for input between steps
- Learning curve is steep

**Desired State:**

- Interactive wizard that guides users step-by-step
- Each step explained in plain language
- Users asked for input/confirmation before proceeding
- Files highlighted and offered for review
- Educational experience that teaches the system

---

## 🏗️ Architecture Design

### **New Component: `InteractiveGuide` Class**

**Location:** `src/utils/interactive_guide.py`

**Responsibilities:**

1. Orchestrate the idea-to-project workflow
2. Elicit information from users via prompts
3. Explain what each step does before executing
4. Show progress indicators
5. Offer file review after creation
6. Collect user feedback at each stage

### **Modified Components:**

1. **`cli/manage.py`** - Add new command: `python cli/manage.py guided`
2. **`src/utils/elicitation_utils.py`** - Enhanced question templates
3. **Each Agent** - Add `.explain()` method to describe what they do
4. **New Dashboard View** - Web-based wizard interface (optional Phase 2)

---

## 🔄 User Flow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: WELCOME & IDEA CAPTURE                             │
│  • Show welcome message                                     │
│  • Ask for initial idea (voice or text)                     │
│  • Educational note: "We'll refine your idea using AI"      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: CLARIFYING QUESTIONS                               │
│  • Identify gaps in the idea                                │
│  • Ask targeted questions (5-7 questions max)               │
│  • Show why each question matters                           │
│  • Save answers to context                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: IDEA REFINEMENT                                    │
│  • Explain: "RefinementAgent will clarify your concept"     │
│  • Show progress: "🤖 Refining... (30-60 seconds)"          │
│  • Display refined idea                                     │
│  • Ask: "Review refined idea? (yes/no)"                     │
│  • If yes → Open file, wait for feedback                    │
│  • Ask: "Approve to continue? (yes/edit/abort)"            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: BUSINESS SCORING                                   │
│  • Explain: "VerticalAgent evaluates business viability"    │
│  • Show criteria: RICE framework (Reach/Impact/etc.)        │
│  • Run scoring                                              │
│  • Display results visually                                 │
│  • Highlight: "Score: 42/60 - Good potential!"             │
│  • Ask: "View detailed scoring? (yes/no)"                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: STRATEGIC PLANNING                                 │
│  • Explain: "StrategyAgent creates execution plan"          │
│  • Show what will be generated (PRD, roadmap, etc.)         │
│  • Ask: "Proceed with planning? (yes/no)"                   │
│  • Run planning agents                                      │
│  • Show created files list                                  │
│  • Ask: "Review any file? (list/file_name/continue)"        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: PROJECT SCAFFOLDING                                │
│  • Explain: "Creating project structure"                    │
│  • Show directory tree as it's created                      │
│  • Highlight key files                                      │
│  • Final summary of what was created                        │
│  • Next steps guidance                                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  COMPLETION                                                 │
│  • Show success message                                     │
│  • List all generated files                                 │
│  • Provide commands to run next                             │
│  • Ask: "Start development wizard? (yes/no)"                │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 Implementation Plan

### **Phase 1: Core Interactive CLI (Week 1-2)**

**Files to Create:**

1. `src/utils/interactive_guide.py` - Main wizard class
2. `src/utils/question_templates.py` - Predefined question sets
3. `src/utils/display_helpers.py` - Pretty output formatting
4. `cli/commands/guided.py` - CLI command handler

**Key Methods:**

```python
class InteractiveGuide:
    def __init__(self):
        self.context = {}
        self.step = 1

    def welcome(self):
        """Show welcome message and capture initial idea"""

    def elicit_details(self, idea):
        """Ask clarifying questions based on idea type"""

    def explain_step(self, step_name, agent_name):
        """Explain what's about to happen"""

    def run_with_progress(self, agent, inputs):
        """Run agent with progress indicator"""

    def offer_review(self, filepath):
        """Ask if user wants to review a file"""

    def show_file(self, filepath):
        """Display file contents with syntax highlighting"""

    def get_confirmation(self, message):
        """Get yes/no/edit confirmation from user"""

    def show_summary(self):
        """Final summary of all created files"""
```

### **Phase 2: Web Dashboard (Week 3-4)**

**Files to Create:**

1. `dashboard/wizard_ui.py` - Streamlit wizard interface
2. `dashboard/components/step_indicator.py` - Progress visualization
3. `dashboard/components/file_viewer.py` - Inline file preview

**Features:**

- Visual progress bar
- Inline file editing
- Drag-and-drop for inputs
- Chat-like interface for questions

---

## 🎨 User Experience Examples

### **Example 1: Welcome Screen**

```
═══════════════════════════════════════════════════════════════
🎯 AI Management Team - Interactive Project Wizard
═══════════════════════════════════════════════════════════════

Welcome! I'll guide you through turning your idea into a complete
project plan. This process takes about 10-15 minutes.

What we'll do together:
  1. Capture your idea (1 min)
  2. Ask clarifying questions (3 min)
  3. Refine and score your concept (5 min)
  4. Generate project plan (5 min)
  5. Create project structure (2 min)

Let's start! What's your project idea?
(Tip: Even a vague idea is fine - we'll clarify it together)

Your idea: _
```

### **Example 2: Step Explanation**

```
─────────────────────────────────────────────────────────────
📊 STEP 3: IDEA REFINEMENT
─────────────────────────────────────────────────────────────

What's happening now:
  The RefinementAgent (powered by AI) will:
  • Analyze your idea for clarity
  • Identify missing information
  • Ask clarifying questions
  • Create a refined, specific concept
  • Suggest alternatives

This takes about 30-60 seconds.

Ready to proceed? (yes/no): _
```

### **Example 3: File Review Offer**

```
✅ Refinement complete!

📁 Created: data/refined/refined_ideas.json

Your refined concept:
┌─────────────────────────────────────────────────────────────┐
│ Title: asksharon.ai - AI Productivity Companion             │
│ Target: Busy entrepreneurs and solopreneurs                 │
│ Key Features: Email management, voice interaction, coaching │
│ Unique Angle: Voice-first with integrated wellness support  │
└─────────────────────────────────────────────────────────────┘

Options:
  [V]iew full file
  [E]dit refinement
  [C]ontinue to next step

Your choice: _
```

### **Example 4: Progress Indicator**

```
Progress: [████████░░░░░░] Step 3 of 6

Currently running: VerticalAgent (Business Scoring)
Estimated time: 45 seconds remaining

What's being evaluated:
  ✓ Market size
  ✓ Pain severity
  ⏳ Differentiation (analyzing...)
  ⏸ Monetization potential
  ⏸ Technical feasibility
```

---

## 🎓 Educational Content

### **Agent Explanations (For Each Step):**

**RefinementAgent:**

```
What is RefinementAgent?
  An AI-powered agent that takes vague ideas and turns them into
  clear, actionable concepts.

Why this matters:
  Specific ideas are easier to plan and build. This agent saves you
  hours of brainstorming by identifying gaps and asking the right
  questions.

What it creates:
  • Refined concept description
  • Target customer profile
  • Value proposition
  • Alternative approaches
  • Next steps recommendations
```

**VerticalAgent:**

```
What is VerticalAgent?
  A business analysis agent that scores your idea using proven
  frameworks (RICE/ICE).

Why this matters:
  Not all ideas are worth building. This agent helps you objectively
  evaluate business potential before investing time.

What it evaluates:
  • Reach: How many people need this?
  • Impact: How much will it improve their lives?
  • Confidence: How sure are we about the market?
  • Effort: How hard is it to build?

Score interpretation:
  0-20:  Rethink the idea
  21-40: Promising, but needs refinement
  41-60: Strong potential - proceed!
```

---

## 📊 Success Metrics

**For this feature:**

- 90%+ of new users complete the wizard (vs. <30% who complete CLI)
- Average time to first project: <15 minutes (vs. 60+ minutes currently)
- User satisfaction score: >4/5
- Users report "understanding what each step does": >80%

---

## 🛠️ Technical Requirements

**Dependencies:**

- `rich` - Terminal formatting and progress bars
- `inquirer` - Interactive prompts
- `pygments` - Syntax highlighting for file preview
- `click` - CLI framework (already installed)

**Install:**

```bash
pip install rich inquirer pygments
```

---

## 📝 Implementation Checklist

### Phase 1: Core CLI Wizard

- [ ] Create `src/utils/interactive_guide.py`
- [ ] Create question templates for common project types
- [ ] Add `cli/commands/guided.py` command
- [ ] Implement step-by-step flow
- [ ] Add educational content for each agent
- [ ] Create file review functionality
- [ ] Add confirmation prompts
- [ ] Test with 3 different project types

### Phase 2: Enhanced UX

- [ ] Add progress indicators
- [ ] Implement file preview with syntax highlighting
- [ ] Create visual summary of created files
- [ ] Add "explain more" option for each step
- [ ] Implement back/skip navigation
- [ ] Save session state (resume if interrupted)

### Phase 3: Web Interface (Optional)

- [ ] Create Streamlit wizard UI
- [ ] Add chat-like interaction
- [ ] Inline file editing
- [ ] Visual progress tracking
- [ ] Mobile-responsive design

---

## 🚀 Example Usage

**Command:**

```bash
python cli/manage.py guided
```

**Or:**

```bash
./dashboard/start_wizard.sh  # Web interface
```

---

## 🔄 Integration Points

**Where this fits in current system:**

- Uses existing agents (no changes needed)
- Wraps orchestrator with interactive layer
- Saves all outputs to same locations
- Compatible with existing workflows
- Can be bypassed for power users

---

## 📚 Documentation Needed

1. **User Guide:** "Getting Started with Interactive Wizard"
2. **Developer Guide:** "Adding New Question Templates"
3. **Video Tutorial:** "Your First Project in 10 Minutes"
4. **FAQ:** "Wizard vs CLI: When to Use Each"

---

## 💡 Future Enhancements

- Voice input for initial idea capture
- Multi-language support
- Collaborative mode (multiple stakeholders)
- Integration with project management tools
- AI-powered question generation (learns from user patterns)
- Template library for common project types

---

**Created:** 2025-10-15  
**Author:** AI Management Team  
**Status:** Specification Complete - Ready for Implementation  
**Estimated Effort:** 2-3 weeks for Phase 1
