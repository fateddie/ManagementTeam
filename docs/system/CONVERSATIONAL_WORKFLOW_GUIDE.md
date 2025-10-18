# Conversational Workflow System Guide

## Overview

A natural, conversation-style workflow for validating business ideas - similar to having a chat with Claude. The system guides you through idea refinement and research with soft validation, auto-save, and educational context.

## Quick Start

### Option 1: Use the Startup Script (Recommended)

```bash
./start.sh
```

This will:
- Check dependencies (Python, Redis, packages)
- Start required services (API server)
- Show you an interactive menu

Choose option 1 or 2 to start a new idea workflow.

### Option 2: Direct CLI

**Guided Mode (Conversational):**
```bash
python cli/interactive_workflow.py
```

**Expert Mode (Fast Input):**
```bash
python cli/interactive_workflow.py --expert
```

**Resume Existing Project:**
```bash
python cli/interactive_workflow.py --resume PROJECT_ID
```

## How It Works

### Conversational Style

The workflow feels like this conversation we're having right now:

```
Hey! I'm here to help you explore and validate your idea.

Tell me about your idea. What problem are you trying to solve?
→ I want to build a tool that helps developers find bugs faster

That's interesting! Can you tell me more about why this problem matters?
→ Developers spend hours debugging and it's frustrating

I'm thinking this could be for: small businesses, large enterprises,
individual consumers, or developers. Which feels closest?
→ developers

What's their role? What do they do day-to-day?
→ Full-stack developers building web applications
```

### Key Features

1. **Conversational Prompts** - Natural questions, not rigid forms
2. **Suggested Options** - 5 options to choose from (or describe your own)
3. **Follow-up Questions** - System asks for more detail when helpful
4. **Soft Validation** - Warns but never blocks you
5. **Auto-Save** - Every answer saved immediately
6. **Confidence Scoring** - Shows data quality with visual bars
7. **Educational Context** - Explains why each step matters

### Workflow Steps

**Step 1: Idea Refinement** (Conversational Q&A)
- Core idea and problem
- Target customer
- Value proposition
- Timeline

**Step 2: Pain Discovery** (Auto-triggered Research)
- Searches Reddit, X/Twitter, YouTube
- Finds real conversations about the problem
- Validates pain points

**Step 3: Market Sizing** (Auto-triggered Research)
- Market size and growth
- Geographic data
- Trend analysis

**Step 4: Competitive Analysis** (Auto-triggered Research)
- Direct competitors
- Alternative solutions
- Market positioning

## Modes

### Guided Mode (Default)

Perfect for:
- First-time users
- Exploring new ideas
- Learning the process

Features:
- Conversational questions one at a time
- 5 suggested options for most questions
- Follow-up questions for depth
- Gentle suggestions to improve answers
- Educational context at each step

### Expert Mode

Perfect for:
- Experienced users
- Quick validation
- When you know exactly what to say

Features:
- All fields shown at once
- Skip prompts and explanations
- Fast input
- Still has auto-save and validation

## Gated Workflow

### Soft Gates (Default)

After each step, you see:
- Summary of what you entered
- Confidence score (0-100%)
- Warnings if data is light
- Options:
  1. Continue - looks good!
  2. Refine - add more detail
  3. Skip this step (with confirmation)
  4. Save & exit

**Important:** You can ALWAYS proceed, even with low confidence. The system guides but never blocks.

### Override

At any gate, you can:
- Skip the step
- Continue with low completion
- Exit and resume later

All progress is auto-saved.

## Dashboard Integration

View workflow progress in the dashboard:

1. Start dashboard: `./start.sh` → Option 5
2. Navigate to "📋 Project Context"
3. Select your project
4. Click "🔄 Workflow Progress" tab

You'll see:
- Progress bar (X/4 steps complete)
- Each step's status (Completed/In Progress/Pending)
- Confidence scores with visual bars
- All collected data
- Commands to continue or run research

## Data Persistence

### Auto-Save

**When:**
- After every field (guided mode)
- After all fields (expert mode)
- On step completion
- On exit

**Where:**
- Stored in ProjectContext metadata
- Accessible via dashboard
- Resumable at any time

### Resume Workflow

```bash
# Option 1: Via startup script
./start.sh
→ Choose option 3: Continue existing project
→ Enter project ID

# Option 2: Direct CLI
python cli/interactive_workflow.py --resume PROJECT_ID
```

The system remembers:
- Current step
- All completed steps
- Every answer you gave
- Confidence scores
- Timestamps

## Validation Strategy

### Soft Validation

**Checks:**
- Minimum length (e.g., 20 characters for core idea)
- Vague terms (e.g., "stuff", "things", "something")
- Confidence factors (e.g., industry mentioned, role mentioned)

**Responses:**
- ⚠️ Warnings shown
- 💡 Gentle suggestions offered
- Never blocks you from continuing
- Confidence score shows quality

**Example:**

```
Your answer: "A tool for people"

⚠️ Vague terms: people
💡 Could you paint me a picture of a specific person who has this problem?

Confidence: [████░░░░░░] 40%

Want to add more detail? (y/N):
```

### Confidence Scoring

**Factors that boost confidence:**
- Specific details (industry, role, metrics)
- Problem and solution mentioned
- Comparisons to alternatives
- Timeframes and numbers
- Length and completeness

**Visual feedback:**
```
[██████████] 100% - Excellent!
[████████░░] 80%  - Great!
[██████░░░░] 60%  - Good
[████░░░░░░] 40%  - Light detail
[██░░░░░░░░] 20%  - Very vague
```

## File Structure

**Core System:**
- `core/workflow_gates.py` - Step definitions, prompts, validation
- `core/workflow_state.py` - Persistence and auto-save
- `core/interactive_orchestrator.py` - Conversational orchestrator

**CLI & Startup:**
- `cli/interactive_workflow.py` - CLI wrapper
- `start.sh` - Comprehensive startup script

**Dashboard:**
- `dashboard/streamlit_dashboard.py` - Workflow Progress tab added

## Example Session

```bash
$ ./start.sh

╔════════════════════════════════════════════════════════════╗
║           Management Team - Starting Up...                ║
╚════════════════════════════════════════════════════════════╝

✅ Python 3.11.5 found
✅ Redis is already running on port 6379
✅ All required packages installed
✅ Environment configuration found

✅ API server started (PID: 12345)

╔════════════════════════════════════════════════════════════╗
║           Management Team - Idea Validation               ║
╚════════════════════════════════════════════════════════════╝

What would you like to do today?

  1) 💬 Work on new idea (guided conversation)
  2) 🚀 Work on new idea (expert mode - fast input)
  3) 📂 Continue existing project
  4) ⚙️  Run full pipeline (all research agents)
  5) 📊 Open dashboard only
  6) 🔍 System status
  7) 🚪 Exit

Enter your choice [1-7]: 1

============================================================
🚀 Interactive Workflow - GUIDED MODE
============================================================

Hey! I'm here to help you explore and validate your idea.

We'll have a conversation to understand:
  • What you're building
  • Who it's for
  • Why it matters

Then I'll research real pain points, market size, and competition.

Let's get started!

────────────────────────────────────────────────────────────
📍 Idea Refinement
────────────────────────────────────────────────────────────
🎯 **Why This Matters**
This conversation helps me understand your idea deeply so I can
give you the best research and insights. The more context you
share, the better I can help identify opportunities and challenges.

Tell me about your idea. What problem are you trying to solve?

→ I want to build an AI assistant that helps product managers
   prioritize features based on customer feedback

💾 Auto-saved

That's interesting! Can you tell me more about why this problem matters?

→ PMs waste hours manually reading feedback and guessing what to
   build next. They need data-driven insights.

💾 Auto-saved

Who is this for? Who would benefit most from this?

I'm thinking this could help: small businesses, large enterprises,
individual consumers, or developers. Which feels closest?

Here are some options (or describe in your own words):
  1) Small businesses (1-50 employees)
  2) Mid-market companies (50-500 employees)
  3) Large enterprises (500+ employees)
  4) Individual consumers (B2C)
  5) Developers/technical users
  6) Let me describe them...

Your choice (number or custom answer): 2
✓ Mid-market companies (50-500 employees)

💾 Auto-saved

[... continues through all questions ...]

============================================================
📋 SUMMARY
============================================================

• Core Idea: AI assistant that helps product managers prioritize
  features based on customer feedback - PMs waste hours manually
  reading feedback and guessing what to build next

• Target Customer: Mid-market companies (50-500 employees) in SaaS

• Value Proposition: Automated analysis of customer feedback with
  data-driven prioritization recommendations

• Timeline: Currently building - need market validation

[██████████] 90% Confidence

✅ Great! I have good context to work with.

────────────────────────────────────────────────────────────
What would you like to do?
  1) Continue - looks good!
  2) Refine - I want to add more detail
  3) Skip this step (not recommended)
  4) Save & exit

Choice [1-4]: 1

🔍 Starting research for step_2_pain_discovery...
This will take a few minutes.

Query: AI assistant that helps product managers prioritize features
based on customer feedback for Mid-market companies (50-500 employees)
in SaaS - Automated analysis of customer feedback with data-driven
prioritization recommendations

[Research agents running...]
```

## Voice Agent Integration

This system is designed for voice agent integration:

**Conversational by Default:**
- Natural language prompts
- Follow-up questions
- No rigid forms

**Audio-Friendly:**
- Clear prompts
- Option-based choices
- Confirmation loops

**Future Enhancement:**
Voice agent can conduct the entire workflow as an interview, with the same soft validation and auto-save features.

## Tips

### Getting Better Results

1. **Be Specific:** Instead of "people", say "healthcare administrators"
2. **Add Context:** Explain why the problem matters
3. **Use Numbers:** "Saves 5 hours/week" is better than "saves time"
4. **Compare:** "Better than X because..." shows you understand the market

### Workflow Management

1. **Take Your Time:** Auto-save means you can pause anytime
2. **Refine Later:** Low confidence? Come back and add more detail
3. **Check Dashboard:** Visual progress helps you see what's missing
4. **Resume Anytime:** Project ID lets you continue from any step

### Troubleshooting

**"No workflow progress yet"**
- You haven't started the interactive workflow for this project
- Run: `python cli/interactive_workflow.py --resume PROJECT_ID`

**"Failed to load project data"**
- API server may not be running
- Run: `./start.sh` to start all services

**"Some packages may be missing"**
- Install requirements: `pip install -r requirements.txt`

## Next Steps

After completing the workflow:

1. **View Results:** Check dashboard → Project Context → Workflow Progress
2. **Run Research:** `python cli/manage.py run --project PROJECT_ID`
3. **Review Findings:** Dashboard shows research results
4. **Iterate:** Refine your idea based on insights

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Conversational Workflow                 │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  start.sh                                                │
│     │                                                     │
│     ├─→ Dependency Checks                               │
│     ├─→ Start Services (Redis, API)                     │
│     └─→ Interactive Menu                                │
│           │                                               │
│           ├─→ Option 1/2: cli/interactive_workflow.py   │
│           │      │                                        │
│           │      └─→ core/interactive_orchestrator.py   │
│           │             │                                 │
│           │             ├─→ core/workflow_gates.py       │
│           │             │   (Step definitions)           │
│           │             │                                 │
│           │             ├─→ core/workflow_state.py       │
│           │             │   (Auto-save, resume)          │
│           │             │                                 │
│           │             └─→ core/project_context.py      │
│           │                 (Persistence)                │
│           │                                               │
│           └─→ Option 5: Dashboard                        │
│                  └─→ Workflow Progress Tab               │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Success Criteria

✅ Single command startup: `./start.sh`
✅ Conversational style (like Claude chat)
✅ Soft validation (warn, never block)
✅ Auto-save after every answer
✅ Resume capability
✅ Expert mode for fast input
✅ Dashboard integration
✅ Educational context
✅ Confidence scoring
✅ Gated workflow with override

---

**Ready to validate your idea?**

Run: `./start.sh` and choose option 1! 🚀
