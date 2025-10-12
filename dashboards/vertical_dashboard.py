"""
vertical_dashboard.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Streamlit Dashboard for Vertical Agent

Interactive dashboard for evaluating and ranking business verticals
using RICE or ICE scoring frameworks.

Usage:
    streamlit run dashboards/vertical_dashboard.py

Location: dashboards/vertical_dashboard.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import pandas as pd
import json
import yaml
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agents.vertical_agent.vertical_agent import run_vertical_agent

# Page config
st.set_page_config(
    page_title="Vertical Agent - Business Idea Evaluator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🎯 Vertical Agent Dashboard</h1>', unsafe_allow_html=True)
st.markdown("**Evaluate and rank business ideas using RICE or ICE scoring**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    framework = st.selectbox(
        "Scoring Framework",
        ["RICE", "ICE"],
        help="RICE = (Reach × Impact × Confidence) / Effort\nICE = (Impact + Confidence + Ease) / 3"
    )
    
    st.markdown("---")
    
    input_method = st.radio(
        "Input Method",
        ["📁 Upload File", "✏️ Manual Entry", "📋 Load Examples"],
        help="Choose how to input your business ideas"
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Scoring Guide")
    st.markdown("""
    **All scores: 1-10**
    
    **Reach:** Market size
    - 1-3: Niche
    - 7-10: Large
    
    **Impact:** Value created
    - 1-3: Minor
    - 7-10: Major
    
    **Confidence:** Certainty
    - 1-3: Risky
    - 7-10: Proven
    
    **Effort:** Complexity
    - 1-3: Easy
    - 7-10: Hard
    """)

# Main content area
ideas = []

# Input Section
if input_method == "📁 Upload File":
    st.subheader("📁 Upload Business Ideas")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload JSON or YAML file",
            type=["json", "yaml", "yml"],
            help="Upload a file with your business vertical ideas"
        )
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.json'):
                    data = json.load(uploaded_file)
                else:
                    data = yaml.safe_load(uploaded_file)
                
                # Handle both formats
                if isinstance(data, dict) and 'verticals' in data:
                    ideas = data['verticals']
                elif isinstance(data, list):
                    ideas = data
                else:
                    st.error("Invalid file format. Expected list or dict with 'verticals' key.")
                
                if ideas:
                    st.success(f"✅ Loaded {len(ideas)} business ideas")
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
    
    with col2:
        st.info("""
        **File Format:**
        ```json
        [
          {
            "name": "Idea Name",
            "reach": 7,
            "impact": 8,
            "confidence": 6,
            "effort": 4
          }
        ]
        ```
        """)

elif input_method == "✏️ Manual Entry":
    st.subheader("✏️ Enter Business Ideas Manually")
    
    num_ideas = st.number_input("How many ideas to evaluate?", min_value=1, max_value=10, value=2)
    
    for i in range(num_ideas):
        with st.expander(f"💡 Idea #{i+1}", expanded=(i == 0)):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                name = st.text_input(
                    "Business Idea Name",
                    key=f"name_{i}",
                    placeholder="e.g., Pet Grooming App"
                )
            
            with col2:
                reach = st.slider("Reach", 1, 10, 5, key=f"reach_{i}")
                impact = st.slider("Impact", 1, 10, 5, key=f"impact_{i}")
            
            with col3:
                confidence = st.slider("Confidence", 1, 10, 5, key=f"confidence_{i}")
                effort = st.slider("Effort", 1, 10, 5, key=f"effort_{i}")
            
            description = st.text_area(
                "Description (optional)",
                key=f"desc_{i}",
                placeholder="Brief description of the idea..."
            )
            
            if name:
                idea = {
                    "name": name,
                    "reach": reach,
                    "impact": impact,
                    "confidence": confidence,
                    "effort": effort
                }
                if description:
                    idea["description"] = description
                ideas.append(idea)

else:  # Load Examples
    st.subheader("📋 Example Business Ideas")
    
    examples = {
        "Service Businesses (8 ideas)": "inputs/verticals.json",
        "Quick Test (3 ideas)": "inputs/example_simple.json",
        "Your Ideas (2 ideas)": "inputs/ideas.json"
    }
    
    example_choice = st.selectbox("Choose example set", list(examples.keys()))
    
    example_file = project_root / examples[example_choice]
    
    if example_file.exists():
        with open(example_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'verticals' in data:
                ideas = data['verticals']
            else:
                ideas = data
        
        st.success(f"✅ Loaded {len(ideas)} example ideas")
        
        # Show preview
        with st.expander("👀 Preview Ideas"):
            for idea in ideas:
                st.markdown(f"**{idea['name']}** - R:{idea['reach']}, I:{idea['impact']}, C:{idea['confidence']}, E:{idea['effort']}")
    else:
        st.error(f"Example file not found: {example_file}")

# Evaluation Section
if ideas:
    st.markdown("---")
    
    if st.button("🚀 Evaluate Ideas", type="primary", use_container_width=True):
        with st.spinner(f"Evaluating {len(ideas)} ideas using {framework} framework..."):
            try:
                result = run_vertical_agent(ideas, framework=framework)
                
                # Store in session state
                st.session_state['result'] = result
                st.session_state['ideas'] = ideas
                st.session_state['framework'] = framework
                
            except Exception as e:
                st.error(f"❌ Error during evaluation: {e}")

# Results Section
if 'result' in st.session_state:
    result = st.session_state['result']
    
    # Handle errors
    if "error" in result:
        st.error(f"❌ {result['error']}")
        if "action" in result:
            st.info(f"💡 {result['action']}")
        if "missing" in result:
            st.warning("Missing data for:")
            for item in result["missing"]:
                st.write(f"- {item}")
    else:
        # Success - show results
        st.success("✅ Evaluation Complete!")
        
        # Top Recommendation Card
        st.markdown("---")
        st.subheader("🏆 Top Recommendation")
        
        top = result['top_choice']
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🎯 Top Choice", top['name'])
        with col2:
            st.metric("Score", f"{top['score']:.2f}")
        with col3:
            st.metric("Reach", f"{top['reach']}/10")
        with col4:
            st.metric("Impact", f"{top['impact']}/10")
        with col5:
            st.metric("Confidence", f"{top['confidence']}/10")
        
        if 'description' in top:
            st.info(f"📝 {top['description']}")
        
        # Proactive Insights
        if 'proactive_notes' in result and result['proactive_notes']:
            st.markdown("---")
            st.subheader("🤖 Proactive Insights")
            
            for i, note in enumerate(result['proactive_notes'], start=1):
                if "⚠️" in note or "🚨" in note:
                    st.warning(f"{i}. {note}")
                elif "✅" in note or "🎯" in note:
                    st.success(f"{i}. {note}")
                else:
                    st.info(f"{i}. {note}")
        
        # Rankings Table
        st.markdown("---")
        st.subheader("📊 Complete Rankings")
        
        # Create DataFrame
        all_ranked = result['all_ranked']
        df = pd.DataFrame(all_ranked)
        
        # Add rank column
        df.insert(0, 'Rank', range(1, len(df) + 1))
        
        # Add medal emoji
        df['Medal'] = df['Rank'].apply(
            lambda x: "🥇" if x == 1 else "🥈" if x == 2 else "🥉" if x == 3 else ""
        )
        
        # Reorder columns
        cols = ['Medal', 'Rank', 'name', 'score', 'reach', 'impact', 'confidence', 'effort']
        if 'description' in df.columns:
            cols.append('description')
        df = df[cols]
        
        # Display table
        st.dataframe(
            df.style.background_gradient(subset=['score'], cmap='Greens'),
            use_container_width=True,
            hide_index=True
        )
        
        # Visualizations
        st.markdown("---")
        st.subheader("📈 Visual Analysis")
        
        tab1, tab2, tab3 = st.tabs(["📊 Bar Chart", "🎯 Radar Chart", "📉 Scatter Plot"])
        
        with tab1:
            # Bar chart of scores
            fig_bar = px.bar(
                df,
                x='name',
                y='score',
                color='score',
                title=f'{st.session_state["framework"]} Scores by Vertical',
                color_continuous_scale='Viridis',
                text='score'
            )
            fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_bar.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with tab2:
            # Radar chart for top 3
            top_3 = df.head(3)
            
            fig_radar = go.Figure()
            
            for idx, row in top_3.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row['reach'], row['impact'], row['confidence'], 10 - row['effort']],
                    theta=['Reach', 'Impact', 'Confidence', 'Ease (10-effort)'],
                    fill='toself',
                    name=row['name']
                ))
            
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                showlegend=True,
                title="Top 3 Ideas - Factor Comparison",
                height=500
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with tab3:
            # Scatter plot: Impact vs Effort
            fig_scatter = px.scatter(
                df,
                x='effort',
                y='impact',
                size='score',
                color='confidence',
                hover_data=['name', 'reach'],
                title='Impact vs Effort (size = score, color = confidence)',
                labels={'effort': 'Effort (Lower is Better)', 'impact': 'Impact (Higher is Better)'},
                color_continuous_scale='RdYlGn'
            )
            
            # Add quadrant lines
            fig_scatter.add_hline(y=5.5, line_dash="dash", line_color="gray", opacity=0.5)
            fig_scatter.add_vline(x=5.5, line_dash="dash", line_color="gray", opacity=0.5)
            
            # Add annotations for quadrants
            fig_scatter.add_annotation(x=8, y=8, text="High Impact<br>High Effort", showarrow=False, opacity=0.5)
            fig_scatter.add_annotation(x=2, y=8, text="High Impact<br>Low Effort<br>✅ BEST", showarrow=False, opacity=0.5, bgcolor="lightgreen")
            fig_scatter.add_annotation(x=8, y=2, text="Low Impact<br>High Effort<br>⚠️ AVOID", showarrow=False, opacity=0.5, bgcolor="lightcoral")
            fig_scatter.add_annotation(x=2, y=2, text="Low Impact<br>Low Effort", showarrow=False, opacity=0.5)
            
            fig_scatter.update_layout(height=500)
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Download Section
        st.markdown("---")
        st.subheader("💾 Download Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as JSON
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name="vertical_evaluation.json",
                mime="application/json"
            )
        
        with col2:
            # Download as CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="vertical_ranking.csv",
                mime="text/csv"
            )
        
        with col3:
            # Download markdown report
            report_path = project_root / "outputs" / "recommendation.md"
            if report_path.exists():
                with open(report_path, 'r') as f:
                    md_content = f.read()
                st.download_button(
                    label="📥 Download Report",
                    data=md_content,
                    file_name="recommendation.md",
                    mime="text/markdown"
                )

else:
    # No ideas yet
    st.info("👆 Choose an input method in the sidebar and add your business ideas to get started!")
    
    # Show example
    with st.expander("💡 Example JSON Format"):
        st.code("""
[
  {
    "name": "AI Receptionist for Hair Salons",
    "reach": 7,
    "impact": 8,
    "confidence": 6,
    "effort": 4,
    "description": "Optional description"
  },
  {
    "name": "Tyre Fitters Booking Bot",
    "reach": 5,
    "impact": 7,
    "confidence": 8,
    "effort": 5
  }
]
        """, language="json")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <p><strong>Vertical Agent Dashboard</strong> v1.0</p>
    <p>Management Team AI System | 
    <a href='https://github.com/fateddie/ManagementTeam' target='_blank'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)

