# 📊 Vertical Agent Dashboard

**Interactive Streamlit Dashboard for Business Idea Evaluation**

---

## 🚀 Quick Start

```bash
streamlit run dashboards/vertical_dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## ✨ Features

### **1. Three Input Methods**

#### 📁 **Upload File**
- Upload JSON or YAML files
- Supports both formats
- Auto-detects file type

#### ✏️ **Manual Entry**
- Add 1-10 ideas directly in the dashboard
- Interactive sliders for scoring
- Optional descriptions

#### 📋 **Load Examples**
- 8 Service Businesses
- 3 Quick Test Ideas  
- Your Ideas (Hair Salons & Tyre Fitters)

### **2. Scoring Frameworks**
- **RICE:** (Reach × Impact × Confidence) / Effort
- **ICE:** (Impact + Confidence + Ease) / 3

### **3. Visual Analysis**
- 📊 **Bar Chart** - Score comparison
- 🎯 **Radar Chart** - Top 3 factor breakdown
- 📉 **Scatter Plot** - Impact vs Effort quadrants

### **4. Proactive Insights**
- Smart suggestions based on scores
- Risk warnings
- Opportunity identification

### **5. Downloads**
- 📥 JSON results
- 📥 CSV ranking
- 📥 Markdown report

---

## 🎮 How to Use

### Step 1: Choose Input Method
In the sidebar, select one of:
- Upload File
- Manual Entry
- Load Examples

### Step 2: Select Framework
Choose between RICE or ICE scoring

### Step 3: Add Your Ideas
Depending on input method:

**Upload:** Drop your `ideas.json` or `verticals.yaml`

**Manual:** Fill in the form for each idea:
- Name
- Reach (1-10)
- Impact (1-10)
- Confidence (1-10)
- Effort (1-10)
- Description (optional)

**Examples:** Pick from pre-loaded examples

### Step 4: Evaluate
Click the **🚀 Evaluate Ideas** button

### Step 5: Review Results
- See top recommendation
- Read proactive insights
- Explore visualizations
- Download results

---

## 📊 Dashboard Sections

### **🏆 Top Recommendation**
- Clear winner with metrics
- Score breakdown
- Description

### **🤖 Proactive Insights**
Smart suggestions like:
- 🔍 Low confidence warnings
- 📣 Limited reach advice
- ⚠️ High effort warnings
- ⚖️ Close competition alerts
- 🎯 Clear winner confirmation

### **📊 Complete Rankings**
- Sortable table
- Color-coded scores
- Medals for top 3 (🥇🥈🥉)

### **📈 Visual Analysis**

#### **Bar Chart**
- Compare scores across all ideas
- Green gradient for easy reading

#### **Radar Chart**
- Top 3 ideas
- All 4 factors visualized
- Easy comparison

#### **Scatter Plot**
- Impact vs Effort quadrants
- Size = Score
- Color = Confidence
- Identifies best opportunities

---

## 💡 Tips for Best Results

### **Scoring Guidance**

**Reach (Market Size):**
- 1-3: Niche (< 10K customers)
- 4-6: Medium (10K-100K)
- 7-10: Large (> 100K)

**Impact (Value):**
- 1-3: Minor improvement
- 4-6: Moderate value
- 7-10: Game-changer

**Confidence (Certainty):**
- 1-3: High risk/uncertainty
- 4-6: Moderate confidence
- 7-10: Proven model

**Effort (Complexity):**
- 1-3: Simple/quick
- 4-6: Moderate
- 7-10: Complex/long

### **Best Practices**
1. Be honest with scores
2. Compare similar types of ideas
3. Review proactive suggestions carefully
4. Use scatter plot to find "sweet spot"
5. Download results for team discussion

---

## 🎯 Understanding the Scatter Plot

The scatter plot shows 4 quadrants:

```
High Impact, Low Effort ✅ BEST
├─ Top-left quadrant
└─ These are your winners!

High Impact, High Effort ⚠️
├─ Top-right quadrant  
└─ Good but resource-intensive

Low Impact, Low Effort
├─ Bottom-left quadrant
└─ Easy but limited value

Low Impact, High Effort ❌ AVOID
├─ Bottom-right quadrant
└─ Worst combination
```

---

## 📥 File Formats

### **JSON Format**
```json
[
  {
    "name": "Business Idea Name",
    "reach": 7,
    "impact": 8,
    "confidence": 6,
    "effort": 4,
    "description": "Optional description"
  }
]
```

### **YAML Format**
```yaml
verticals:
  - name: "Business Idea Name"
    reach: 7
    impact: 8
    confidence: 6
    effort: 4
    description: "Optional description"
```

---

## 🎨 Dashboard Features

### **Interactive Elements**
- Sliders for all scores
- File upload drag-and-drop
- Expandable idea forms
- Tabbed visualizations
- Color-coded metrics

### **Visual Design**
- Gradient headers
- Metric cards
- Color-coded insights
- Professional charts
- Responsive layout

### **Export Options**
- JSON (full results)
- CSV (rankings only)
- Markdown (report)

---

## 🔧 Troubleshooting

### Dashboard won't start
```bash
# Install streamlit
pip install streamlit plotly

# Check version
streamlit --version
```

### Port already in use
```bash
# Use different port
streamlit run dashboards/vertical_dashboard.py --server.port 8502
```

### Charts not showing
```bash
# Install plotly
pip install plotly
```

---

## 📚 Related Documentation

- **Vertical Agent README:** `agents/vertical_agent/README.md`
- **CLI Usage:** `QUICK_START.md`
- **Complete Status:** `outputs/VERTICAL_AGENT_COMPLETE.md`

---

## 🎊 Example Workflow

1. **Quick Evaluation:**
   ```bash
   streamlit run dashboards/vertical_dashboard.py
   ```

2. **Load examples** → Click "Load Examples"

3. **Select:** "Your Ideas (2 ideas)"

4. **Click:** 🚀 Evaluate Ideas

5. **Review:** Rankings and visualizations

6. **Download:** CSV for team discussion

7. **Decision:** Pick winner based on insights

---

## 🌟 Key Benefits

- ✅ **Visual** - See scores at a glance
- ✅ **Interactive** - No coding required
- ✅ **Smart** - Proactive suggestions
- ✅ **Fast** - Instant evaluation
- ✅ **Flexible** - Multiple input methods
- ✅ **Professional** - Beautiful charts
- ✅ **Shareable** - Download results

---

**Perfect for:**
- Team workshops
- Client presentations
- Quick decision-making
- Portfolio reviews
- Stakeholder alignment

---

*Vertical Agent Dashboard v1.0*  
*Management Team AI System*

