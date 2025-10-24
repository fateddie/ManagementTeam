# 🚀 Quick Start Guide

Get the AI Management Team system running in 2 minutes.

---

## Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

That's it! Redis and API keys are optional.

---

## Step 2: Start the Application

### **Interactive Workflow** (Recommended)

```bash
python3 cli/interactive_workflow.py
```

This starts a conversational workflow that guides you through:
- Refining your idea
- Discovering pain points
- Market analysis
- Strategic recommendations

### **Traditional Agent Pipeline**

```bash
python cli/manage.py run
```

This runs the full 10-agent research pipeline.

---

## Step 3: Follow the Prompts

The system will guide you through everything else!

- Answer questions naturally
- The system auto-saves after each step
- If interrupted, just re-run and it will resume

---

## 🎯 That's It!

You're ready to validate ideas and get strategic insights.

### **Need Help?**

- Type `python3 cli/interactive_workflow.py --help` for options
- Check [README.md](README.md) for full documentation
- Resume after crash: `python3 cli/interactive_workflow.py --resume PROJECT_ID`

---

**Enjoy!** 🚀
