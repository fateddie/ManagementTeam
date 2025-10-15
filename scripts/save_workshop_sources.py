"""
save_workshop_sources.py

Save workshop sources to HTML file with clickable links
Enables verification of all data and claims

Why: Users need to verify AI analysis by checking original sources
Creates: outputs/workshops/sources_[session_id].html with all clickable links

Usage:
    python scripts/save_workshop_sources.py "Your idea"
    
Output: HTML file with organized sources by category for easy verification
"""

import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.refinement_agent.refinement_agent import RefinementAgent
from agents.workshop_agent.workshop_agent import IterativeWorkshopAgent
from core.base_agent import AgentContext


def create_sources_html(market_data, idea_title, session_id):
    """
    Create HTML file with all sources organized by category.
    
    Why: HTML provides clickable links for easy verification
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Workshop Sources - {idea_title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 1200px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .category {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .category-title {{
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 15px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .query {{
            background: #f8f9fa;
            padding: 10px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
            font-style: italic;
        }}
        .summary {{
            margin: 15px 0;
            line-height: 1.6;
        }}
        .sources {{
            margin-top: 15px;
        }}
        .source-link {{
            display: block;
            padding: 8px 12px;
            margin: 5px 0;
            background: #e3f2fd;
            border-left: 3px solid #2196f3;
            border-radius: 4px;
            text-decoration: none;
            color: #1976d2;
            transition: all 0.2s;
        }}
        .source-link:hover {{
            background: #bbdefb;
            padding-left: 20px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 Workshop Research Sources</h1>
        <h2>{idea_title}</h2>
        <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p class="timestamp">Session ID: {session_id}</p>
    </div>
"""
    
    categories = {
        "market_overview": "MARKET OVERVIEW",
        "competitor_landscape": "COMPETITOR LANDSCAPE",
        "competitor_offerings": "COMPETITOR PRODUCTS & USPs",
        "pricing_strategies": "PRICING MODELS",
        "marketing_strategies": "MARKETING & CUSTOMER ACQUISITION",
        "failed_startups": "FAILED STARTUPS (Lessons Learned)",
        "market_trends": "CURRENT TRENDS",
        "market_direction": "MARKET DIRECTION (Future Outlook)",
        "unit_economics": "UNIT ECONOMICS BENCHMARKS",
        "entry_barriers": "BARRIERS TO ENTRY"
    }
    
    for category_key, category_title in categories.items():
        if category_key in market_data:
            data = market_data[category_key]
            
            if isinstance(data, dict) and not data.get("error"):
                html += f"""
    <div class="category">
        <div class="category-title">{category_title}</div>
        <div class="query">
            <strong>Query:</strong> {data.get('query', 'N/A')}
        </div>
        <div class="summary">
            {data.get('summary', 'No summary available')}
        </div>
        <div class="sources">
            <strong>📎 Sources for Verification:</strong>
"""
                sources = data.get('sources', [])
                if sources:
                    for i, source in enumerate(sources, 1):
                        html += f"""            <a href="{source}" target="_blank" class="source-link">
                [{i}] {source}
            </a>
"""
                else:
                    html += """            <p>No sources available</p>
"""
                html += """        </div>
    </div>
"""
    
    html += """
    <div class="header" style="background: #28a745;">
        <h3>✅ How to Verify Data</h3>
        <ol>
            <li>Click any source link to open in new tab</li>
            <li>Verify the claims made in the summary</li>
            <li>Check if numbers match (market size, growth rates, etc.)</li>
            <li>Look for any missing context or nuance</li>
        </ol>
        <p><strong>Why verification matters:</strong> AI analysis is only as good as its data. 
        Verify key claims (especially numbers) before making major decisions.</p>
    </div>
</body>
</html>
"""
    
    return html


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/save_workshop_sources.py \"Your idea\"")
        return
    
    idea = sys.argv[1]
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\n" + "="*70)
    print("📚 WORKSHOP SOURCES SAVER")
    print("="*70 + "\n")
    print(f"Idea: {idea}")
    print(f"Session: {session_id}\n")
    
    # Create context
    context = AgentContext(
        session_id=session_id,
        inputs={"raw_idea": idea},
        shared_data={}
    )
    
    # Refinement
    print("⏳ Step 1: Refining idea...")
    ref_agent = RefinementAgent()
    ref_output = ref_agent.execute(context)
    context.shared_data["RefinementAgent"] = ref_output
    
    refined_title = ref_output.data_for_next_agent.get("title", idea)
    
    # Workshop (mainly to gather market data)
    print("⏳ Step 2: Gathering market intelligence from Perplexity...")
    print("   This will query 10 different aspects of your market")
    print("   Collecting competitor data, pricing, trends, failures, etc.\n")
    
    workshop_agent = IterativeWorkshopAgent()
    
    # Just gather market data (don't run full workshop if user only wants sources)
    market_data = workshop_agent._gather_market_context(ref_output.data_for_next_agent)
    
    # Create HTML file
    output_dir = Path("outputs/workshops")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    html_content = create_sources_html(market_data, refined_title, session_id)
    html_file = output_dir / f"sources_{session_id}.html"
    
    html_file.write_text(html_content)
    
    # Count total sources
    total_sources = sum(
        len(data.get('sources', [])) 
        for data in market_data.values() 
        if isinstance(data, dict)
    )
    
    print("\n" + "="*70)
    print("✅ SOURCES SAVED")
    print("="*70 + "\n")
    print(f"📁 File: {html_file}")
    print(f"📊 Total sources collected: {total_sources}")
    print(f"\n🔍 To verify the data:")
    print(f"   1. Open: {html_file}")
    print(f"   2. Click any source link to verify")
    print(f"   3. Check if claims match source material")
    print(f"\n💡 Or open directly:")
    print(f"   open {html_file}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
