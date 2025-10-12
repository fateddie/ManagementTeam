"""
app.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Startup Idea Refinement & Scoring Dashboard

Interactive Streamlit dashboard for refining and scoring business ideas.

Usage:
    streamlit run streamlit_app/app.py
    
Location: streamlit_app/app.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import streamlit as st
import os
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

st.set_page_config(
    page_title="Startup Idea Dashboard",
    page_icon="💡",
    layout="wide"
)

st.title("💡 Idea Refinement & Scoring Dashboard")
st.markdown("**Refine vague ideas and score them for strategic planning**")

# Sidebar navigation
page = st.sidebar.radio("Navigate", ["🏠 Home", "🔄 Refine Idea", "📊 Score Ideas", "📈 View Results"])

if page == "🏠 Home":
    st.header("Welcome to the Idea Refinement System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Refinement")
        st.markdown("""
        Turn vague ideas into clear concepts:
        - "AI Call Catcher" 
        - → "AI Receptionist for Hair Salons"
        
        The system will:
        - Critique the vagueness
        - Ask clarifying questions
        - Suggest niche alternatives
        - Output a clear concept
        """)
    
    with col2:
        st.subheader("📊 Scoring")
        st.markdown("""
        Score refined ideas on 6 criteria:
        - Clarity
        - Niche Focus  
        - Market Size
        - Pain Severity
        - Differentiation
        - Monetization
        
        Get AI-powered analysis and recommendations.
        """)
    
    st.markdown("---")
    st.info("👈 Use the sidebar to navigate to Refine or Score pages")

elif page == "🔄 Refine Idea":
    st.header("🔄 Refine Your Business Idea")
    
    raw_idea = st.text_input(
        "💡 Enter your raw/vague idea",
        placeholder="e.g., AI Call Catcher, SaaS for dentists, etc."
    )
    
    if st.button("🚀 Refine Idea", type="primary"):
        if not raw_idea:
            st.error("Please enter an idea first")
        else:
            with st.spinner("Refining your idea..."):
                from agents.refinement_agent.refinement_agent import RefinementAgent
                
                agent = RefinementAgent()
                refined = agent.refine_idea(raw_idea)
                
                if 'refined_idea' in refined:
                    st.success("✅ Refinement complete!")
                    
                    st.subheader("📋 Refined Concept")
                    
                    concept = refined['refined_idea']
                    for key, value in concept.items():
                        st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                    
                    if 'critique' in refined:
                        st.warning(f"💭 **Critique:** {refined['critique']}")
                    
                    if 'clarifying_questions' in refined:
                        with st.expander("❓ Clarifying Questions"):
                            for q in refined['clarifying_questions']:
                                st.markdown(f"- {q}")
                    
                    if 'suggested_refinements' in refined:
                        with st.expander("💡 Alternative Refinements"):
                            for r in refined['suggested_refinements']:
                                st.markdown(f"- {r}")
                    
                    # Save button
                    if st.button("💾 Save This Refinement"):
                        agent.save_refined_idea(refined)
                        st.success("Saved to data/refined/refined_ideas.json")

elif page == "📊 Score Ideas":
    st.header("📊 Score Refined Ideas")
    
    refined_path = Path("data/refined/refined_ideas.json")
    
    if not refined_path.exists():
        st.warning("No refined ideas found. Go to 'Refine Idea' first.")
    else:
        with open(refined_path, 'r') as f:
            refined_ideas = json.load(f)
        
        if not refined_ideas:
            st.info("No ideas to score yet")
        else:
            idea_names = [idea.get('refined_idea', {}).get('name', f'Idea {i}') for i, idea in enumerate(refined_ideas)]
            selected_idx = st.selectbox("Select idea to score", range(len(idea_names)), format_func=lambda x: idea_names[x])
            
            selected_idea = refined_ideas[selected_idx]
            
            if st.button("📊 Score This Idea", type="primary"):
                with st.spinner("Scoring..."):
                    from cli.utils.scoring_prompts import score_idea
                    
                    scores = score_idea(selected_idea.get('refined_idea', {}))
                    
                    st.success("✅ Scoring complete!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📈 Scores")
                        for k, v in scores.items():
                            if k not in ["Comments", "Verdict", "Overall_Score"] and isinstance(v, (int, float)):
                                st.metric(k, f"{v}/10")
                    
                    with col2:
                        if 'Overall_Score' in scores:
                            st.metric("Overall Score", f"{scores['Overall_Score']}/60", delta="Total")
                        
                        if 'Verdict' in scores:
                            st.info(f"**Verdict:** {scores['Verdict']}")

elif page == "📈 View Results":
    st.header("📈 View All Results")
    
    # Check for existing results
    ideas_path = Path("data/refined/refined_ideas.json")
    scores_path = Path("data/scores")
    
    if ideas_path.exists():
        with open(ideas_path, 'r') as f:
            ideas = json.load(f)
        
        st.subheader(f"📋 Refined Ideas ({len(ideas)} total)")
        
        for i, idea_data in enumerate(ideas, 1):
            with st.expander(f"{i}. {idea_data.get('refined_idea', {}).get('name', 'Unnamed')}"):
                idea = idea_data.get('refined_idea', {})
                for k, v in idea.items():
                    st.markdown(f"**{k.title()}:** {v}")
    else:
        st.info("No refined ideas yet. Start refining!")

st.sidebar.markdown("---")
st.sidebar.markdown("**Idea Refinement System**")
st.sidebar.markdown("Management Team AI")

