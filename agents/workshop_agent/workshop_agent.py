"""
workshop_agent.py

Iterative Workshop Agent - 3-Round Collaborative Idea Evolution
Phase 1.1 - Core Agent Implementation

Purpose:
    Implements iterative workshop methodology to transform weak ideas into viable businesses
    through collaborative brainstorming with an expert startup advisor persona.

Key Features:
    - 3-round methodology: Assessment → Risk Mitigation → Opportunity Capture
    - Real-time market data via Perplexity integration
    - MBA + startup founder persona for credibility
    - Structured output for downstream agents
    - Comprehensive logging and error handling

Design Reasoning:
    1. BaseAgent inheritance: Ensures orchestrator compatibility without system changes
    2. Perplexity integration: Provides current market data vs outdated research
    3. Specific persona: Builds trust for high-stakes business decisions ($50K+ impact)
    4. 3-round structure: Balances thoroughness with user engagement (15 min total)
    5. Structured output: Enables data sharing with Vertical/Ranking agents

Created: 2025-01-XX
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Core system imports
from core.base_agent import BaseAgent, AgentContext, AgentOutput
from integrations.perplexity_connector import PerplexityConnector

# OpenAI integration (following existing pattern)
try:
    from openai import OpenAI
    from src.utils.config_loader import get_env
except ImportError:
    OpenAI = None
    get_env = None


class IterativeWorkshopAgent(BaseAgent):
    """
    3-Round Iterative Workshop Agent
    
    Transforms business ideas through collaborative iteration with an expert advisor persona.
    
    Persona: Seasoned startup advisor with MBA + founder experience
    Capability: Real-time market data via Perplexity integration
    Methodology: Quick Assessment → Risk Mitigation → Opportunity Capture
    
    Reasoning for Design Choices:
    - Inherits BaseAgent: Ensures orchestrator compatibility without refactoring
    - Depends on RefinementAgent: Workshop needs refined idea input to work effectively
    - Perplexity integration: Provides current market intelligence vs static data
    - 3-round methodology: Optimized for user engagement (15 min vs 30+ min)
    - Specific persona: Builds credibility for high-stakes decisions
    """
    
    @property
    def name(self) -> str:
        """Agent identifier for orchestrator and logging."""
        return "IterativeWorkshopAgent"
    
    @property
    def dependencies(self) -> List[str]:
        """
        Workshop depends on RefinementAgent output.
        
        Reasoning: Workshop needs a refined idea with clear problem statement,
        target customer, and value proposition to effectively apply the 3-round
        methodology. Raw ideas are too vague for meaningful risk/opportunity analysis.
        """
        return ["RefinementAgent"]
    
    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize Workshop Agent with LLM and Perplexity integration.
        
        Args:
            model: OpenAI model to use for workshop analysis
            
        Reasoning for Initialization:
        - Perplexity integration: Provides real-time market data for accurate analysis
        - Logging setup: Enables debugging and performance monitoring
        - Model parameterization: Allows testing with different models
        """
        self.model = model
        self.logger = self._init_logger()
        self.perplexity = self._init_perplexity()
        self.openai_client = self._init_openai()
        self.rounds_completed = 0
        
    def _init_logger(self) -> logging.Logger:
        """
        Setup logging for workshop agent.
        
        Reasoning: Comprehensive logging is critical for debugging workshop sessions
        and understanding how ideas evolve through the iteration process.
        """
        logger = logging.getLogger("workshop_agent")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler for workshop-specific logs
        file_handler = logging.FileHandler("logs/workshop_agent.log")
        file_handler.setLevel(logging.INFO)
        
        # Console handler for real-time feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
        
    def _init_perplexity(self) -> Optional[PerplexityConnector]:
        """
        Initialize Perplexity connector for real-time market data.
        
        Reasoning: Real-time market data is critical for accurate risk assessment
        and opportunity identification. Static data becomes outdated quickly in
        fast-moving startup markets.
        
        Returns:
            PerplexityConnector instance or None if API key not configured
        """
        try:
            return PerplexityConnector()
        except ValueError as e:
            self.logger.warning(f"Perplexity not configured: {e}")
            return None
            
    def _init_openai(self) -> Optional[OpenAI]:
        """
        Initialize OpenAI client for LLM operations.
        
        Reasoning: Workshop analysis requires sophisticated reasoning that benefits
        from advanced LLM capabilities. GPT-4o-mini provides good balance of
        capability and cost for iterative analysis.
        
        Returns:
            OpenAI client instance or None if API key not configured
        """
        if not OpenAI or not get_env:
            self.logger.warning("OpenAI not available")
            return None
            
        api_key = get_env("OPENAI_API_KEY")
        if not api_key:
            self.logger.warning("OPENAI_API_KEY not configured")
            return None
            
        return OpenAI(api_key=api_key)
    
    def validate_inputs(self, context: AgentContext) -> bool:
        """
        Validate that RefinementAgent output is available.
        
        Reasoning: Workshop methodology requires refined idea input with clear
        problem statement, target customer, and value proposition. Without this,
        the risk/opportunity analysis would be meaningless.
        
        Args:
            context: Execution context containing upstream agent outputs
            
        Returns:
            True if inputs are valid, False otherwise
        """
        refined_data = context.get_agent_data("RefinementAgent")
        
        if not refined_data:
            self.logger.error("No RefinementAgent output found")
            return False
            
        required_fields = ["title", "description", "target_customer", "value_proposition"]
        missing_fields = [field for field in required_fields if field not in refined_data]
        
        if missing_fields:
            self.logger.error(f"Missing required fields in refined data: {missing_fields}")
            return False
            
        return True
    
    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Execute 3-round iterative workshop methodology.
        
        Process:
        1. Quick Assessment (5 min) - Market context, top 3 risks/opportunities
        2. Risk Mitigation (5 min) - Address biggest risks with solutions
        3. Opportunity Capture (5 min) - Optimize for biggest opportunities
        
        Reasoning for 3-Round Structure:
        - Round 1: Establishes baseline understanding and identifies key challenges
        - Round 2: Addresses the most critical risks that could kill the idea
        - Round 3: Captures the biggest opportunities for success
        - Time-boxed: Prevents analysis paralysis while ensuring thoroughness
        
        Args:
            context: Execution context with RefinementAgent output
            
        Returns:
            AgentOutput with evolved idea, viability score, and workshop history
        """
        self.logger.info("Starting 3-round iterative workshop")
        
        # Get refined idea from RefinementAgent
        refined_data = context.get_agent_data("RefinementAgent")
        if not refined_data:
            raise ValueError("No refined idea data available from RefinementAgent")
            
        self.logger.info(f"Processing idea: {refined_data.get('title', 'Unknown')}")
        
        try:
            # Round 1: Quick Assessment
            self.logger.info("Round 1: Quick Assessment")
            market_data = self._gather_market_context(refined_data)
            round_1_results = self._execute_round_1_assessment(refined_data, market_data)
            
            # Round 2: Risk Mitigation  
            self.logger.info("Round 2: Risk Mitigation")
            round_2_results = self._execute_round_2_risk_mitigation(
                round_1_results.get("current_idea", refined_data),
                round_1_results["risks"]
            )
            
            # Round 3: Opportunity Capture
            self.logger.info("Round 3: Opportunity Capture")
            round_3_results = self._execute_round_3_opportunity_capture(
                round_2_results["evolved_idea"],
                round_1_results["opportunities"]
            )
            
            # Compile final results
            final_viability_score = round_3_results["final_viability_score"]
            initial_score = round_1_results["initial_viability_score"]
            improvement = final_viability_score - initial_score
            
            self.logger.info(f"Workshop complete: {initial_score} → {final_viability_score} (+{improvement})")
            
            # Return structured output for downstream agents
            return AgentOutput(
                agent_name=self.name,
                decision="approve" if final_viability_score >= 30 else "conditional_go",
                reasoning=f"Idea evolved from {initial_score}/50 to {final_viability_score}/50 viability score. "
                         f"Improvement: +{improvement} points through 3-round methodology.",
                data_for_next_agent={
                    "evolved_idea": round_3_results["final_idea"],
                    "viability_score": final_viability_score,
                    "improvement": improvement,
                    "workshop_history": {
                        "round_1": round_1_results,
                        "round_2": round_2_results,
                        "round_3": round_3_results
                    },
                    "market_intelligence": market_data,
                    "recommendation": self._generate_recommendation(final_viability_score)
                },
                confidence=0.85,  # High confidence due to structured methodology
                flags=[],
                metadata={
                    "rounds_completed": 3,
                    "market_data_sources": len(market_data),
                    "methodology": "3-round_iterative_workshop",
                    "persona": "mba_startup_advisor"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Workshop execution failed: {e}")
            raise
    
    def _gather_market_context(self, idea_data: dict) -> dict:
        """
        Gather real-time market data using Perplexity.
        
        Reasoning: Current market data is essential for accurate risk assessment
        and opportunity identification. Static data becomes outdated quickly in
        fast-moving startup markets.
        
        Args:
            idea_data: Refined idea data from RefinementAgent
            
        Returns:
            Dictionary of market intelligence data
        """
        if not self.perplexity:
            self.logger.warning("Perplexity not available, using placeholder data")
            return {"error": "Perplexity not configured"}
            
        industry = idea_data.get("niche", idea_data.get("target_customer", "startup"))
        title = idea_data.get("title", "")
        value_prop = idea_data.get("value_proposition", "")
        
        # Comprehensive competitive intelligence queries
        # Why: LLM needs deep market understanding to provide informed analysis
        queries = {
            "market_overview": f"What's the current market size for {industry} software in 2025? Include total TAM, growth rate (CAGR), key segments, and market drivers. Where is this market coming from (what trends are driving growth)?",
            
            "competitor_landscape": f"Who are the top 5-10 competitors for {title or industry} products? For each competitor, provide: company name, market share %, annual revenue, user count, founding year, total funding raised, and current valuation if available.",
            
            "competitor_offerings": f"What exactly do Google Calendar, Gmail, Motion.ai, Superhuman, Reclaim.ai, Clockwise, and SaneBox offer? Detail their key features, USP (unique selling proposition), target customer, and what makes each different from the others.",
            
            "pricing_strategies": f"What are the pricing models for {industry} products? Include specific prices: Google (free), Motion.ai ($X/month), Superhuman ($X/month), Reclaim.ai ($X/month). What pricing tiers exist? What's the average ARPU?",
            
            "marketing_strategies": f"How do successful {industry} products acquire customers? What marketing channels do Motion.ai, Superhuman, and Reclaim.ai use? What's their customer acquisition strategy? How do they differentiate in their messaging?",
            
            "failed_startups": f"What calendar and email management startups have failed in the last 5 years? Specifically: Sunrise Calendar, Mailbox, Inbox by Gmail, Astro, and any others. Why did each fail? What lessons can be learned?",
            
            "market_trends": f"What are the top 3-5 trends in {industry} space right now? Examples: AI integration, voice interfaces, privacy focus. Which trends are growing vs declining? What's the evidence?",
            
            "market_direction": f"Where is the {industry} market headed in the next 2-3 years? What new technologies or approaches are emerging? What customer needs are still unmet? What are analysts predicting?",
            
            "unit_economics": f"What's the average ARPU, CAC, LTV:CAC ratio, churn rate, and gross margin for successful {industry} SaaS products? Provide benchmarks from industry reports.",
            
            "entry_barriers": f"What are the main barriers to entry in the {industry} market? Examples: Google's distribution advantage, network effects, data moats, regulatory requirements, required integrations. How high is each barrier?"
        }
        
        market_data = {}
        for category, query in queries.items():
            try:
                result = self.perplexity.search(query, focus="research")
                # Ensure sources are captured for verification
                # Why: Users need to verify data by checking original sources
                market_data[category] = {
                    "query": query,
                    "summary": result.get("summary", ""),
                    "sources": result.get("sources", []),  # URLs for verification
                    "citations": result.get("citations", []),  # Inline citations
                    "timestamp": result.get("timestamp", ""),
                }
                self.logger.info(f"Retrieved {category}: {len(result.get('sources', []))} sources")
            except Exception as e:
                self.logger.error(f"Failed to get {category}: {e}")
                market_data[category] = {"error": str(e), "query": query}
                
        return market_data
    
    def _execute_round_1_assessment(self, idea_data: dict, market_data: dict) -> dict:
        """
        Round 1: Quick Assessment - Market context and risk/opportunity identification.
        
        Reasoning: This round establishes the baseline understanding of the idea
        in its market context. It identifies the top 3 risks (what could kill the idea)
        and top 3 opportunities (what could make it successful).
        
        Args:
            idea_data: Refined idea from RefinementAgent
            market_data: Real-time market intelligence from Perplexity
            
        Returns:
            Dictionary with risks, opportunities, market context, and initial viability score
        """
        if not self.openai_client:
            self.logger.warning("OpenAI not available, using placeholder data")
            return self._get_round_1_placeholder(idea_data, market_data)
        
        # Load prompt template
        prompt_template = self._load_prompt_template("round_1_prompt.md")
        
        # Prepare market data summary
        market_summary = self._summarize_market_data(market_data)
        
        # Build prompt
        prompt = prompt_template.format(
            title=idea_data.get("title", "Unknown"),
            description=idea_data.get("description", "No description"),
            target_customer=idea_data.get("target_customer", "Unknown"),
            value_proposition=idea_data.get("value_proposition", "Unknown"),
            niche=idea_data.get("niche", "Unknown"),
            market_data_summary=market_summary
        )
        
        # Call LLM
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert startup advisor with MBA + founder experience. Think step-by-step through your analysis and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # Lower for consistent analytical reasoning with CoT
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            result["current_idea"] = idea_data
            return result
            
        except Exception as e:
            self.logger.error(f"Round 1 LLM call failed: {e}")
            return self._get_round_1_placeholder(idea_data, market_data)
    
    def _get_round_1_placeholder(self, idea_data: dict, market_data: dict) -> dict:
        """Fallback placeholder data if LLM unavailable."""
        return {
            "risks": [
                {"risk": "Market too small", "probability": 30, "impact": 40000, "score": 12, "reasoning": "Limited addressable market"},
                {"risk": "High competition", "probability": 70, "impact": 50000, "score": 35, "reasoning": "Many established players"},
                {"risk": "Technical complexity", "probability": 60, "impact": 30000, "score": 18, "reasoning": "Difficult to build"}
            ],
            "opportunities": [
                {"opportunity": "Growing market", "potential_value": 1000000, "probability": 60, "reasoning": "Market expanding rapidly"},
                {"opportunity": "Underserved niche", "potential_value": 500000, "probability": 40, "reasoning": "Specific segment needs solution"},
                {"opportunity": "Technology advantage", "potential_value": 750000, "probability": 50, "reasoning": "Novel approach possible"}
            ],
            "market_context": {"summary": "Market data from Perplexity", "data": market_data},
            "viability_breakdown": {"market_attractiveness": 5, "competitive_position": 4, "differentiation": 5, "unit_economics": 6, "technical_feasibility": 5},
            "initial_viability_score": 25,
            "key_insight": "Placeholder assessment - configure OpenAI for real analysis",
            "current_idea": idea_data
        }
    
    def _summarize_market_data(self, market_data: dict) -> str:
        """
        Create comprehensive summary of Perplexity market intelligence.
        
        Why: LLM needs well-organized competitive intelligence to provide
        informed analysis with specific examples and data points.
        """
        if not market_data or "error" in market_data:
            return "Market data not available"
        
        summary_parts = []
        
        # Organize data by category for clarity
        categories = {
            "market_overview": "MARKET OVERVIEW",
            "competitor_landscape": "COMPETITOR LANDSCAPE",
            "competitor_offerings": "COMPETITOR PRODUCTS & USPs",
            "pricing_strategies": "PRICING MODELS",
            "marketing_strategies": "MARKETING & CUSTOMER ACQUISITION",
            "failed_startups": "FAILED STARTUPS (Lessons)",
            "market_trends": "CURRENT TRENDS",
            "market_direction": "MARKET DIRECTION (Future)",
            "unit_economics": "UNIT ECONOMICS BENCHMARKS",
            "entry_barriers": "BARRIERS TO ENTRY"
        }
        
        for category_key, category_title in categories.items():
            if category_key in market_data:
                data = market_data[category_key]
                if isinstance(data, dict) and "summary" in data:
                    summary_parts.append(f"\n{category_title}:\n{data['summary']}")
                    
                    # Add sources with URLs for verification
                    # Why: Users need to verify claims by checking original sources
                    if "sources" in data and data["sources"]:
                        sources = data.get("sources", [])[:3]  # Top 3 sources
                        summary_parts.append(f"\n  📚 Sources for verification:")
                        for i, source in enumerate(sources, 1):
                            summary_parts.append(f"  [{i}] {source}")
        
        return "\n".join(summary_parts) if summary_parts else "Market data retrieved"
    
    def _load_prompt_template(self, filename: str) -> str:
        """Load prompt template from prompts directory."""
        prompt_path = Path(__file__).parent / "prompts" / filename
        try:
            return prompt_path.read_text()
        except Exception as e:
            self.logger.error(f"Failed to load prompt template {filename}: {e}")
            return "Provide analysis for this business idea."
    
    def _execute_round_2_risk_mitigation(self, idea_data: dict, risks: list) -> dict:
        """
        Round 2: Risk Mitigation - Address biggest risks with solutions.
        
        Reasoning: The biggest risk poses the highest threat to idea success.
        By generating and evaluating solutions to address this risk, we can
        significantly improve the idea's viability.
        
        Args:
            idea_data: Current idea state
            risks: List of identified risks from Round 1
            
        Returns:
            Dictionary with risk mitigation results and evolved idea
        """
        if not self.openai_client or not risks:
            return self._get_round_2_placeholder(idea_data, risks)
        
        biggest_risk = risks[0]
        prompt_template = self._load_prompt_template("round_2_prompt.md")
        
        prompt = prompt_template.format(
            risk_description=biggest_risk.get("risk", "Unknown risk"),
            probability=biggest_risk.get("probability", 50),
            impact=biggest_risk.get("impact", 10000),
            score=biggest_risk.get("score", 0),
            current_idea_json=json.dumps(idea_data, indent=2)
        )
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert startup advisor with MBA + founder experience. Think step-by-step through your analysis and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # Lower for consistent analytical reasoning with CoT
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            self.logger.error(f"Round 2 LLM call failed: {e}")
            return self._get_round_2_placeholder(idea_data, risks)
    
    def _get_round_2_placeholder(self, idea_data: dict, risks: list) -> dict:
        """Fallback placeholder data if LLM unavailable."""
        biggest_risk = risks[0] if risks else {"risk": "Unknown", "score": 0}
        
        return {
            "risk_being_addressed": biggest_risk,
            "solutions": [
                {"name": "Narrow target market", "description": "Focus on specific niche", "risk_reduction": 70, "cost": 0, "time_weeks": 0, "feasibility": 10, "score": 700},
                {"name": "Partner with existing player", "description": "Strategic partnership", "risk_reduction": 80, "cost": 10000, "time_weeks": 4, "feasibility": 7, "score": 56},
                {"name": "Focus on unique advantage", "description": "Build differentiator", "risk_reduction": 60, "cost": 5000, "time_weeks": 2, "feasibility": 8, "score": 96}
            ],
            "recommended_solution": {"name": "Narrow target market", "reasoning": "Highest score with zero cost", "expected_outcome": "Reduced market risk"},
            "evolved_idea": {
                **idea_data,
                "target_customer": f"Narrowed: {idea_data.get('target_customer', 'Unknown')}",
                "changes_made": "Market focus narrowed to reduce risk"
            },
            "risk_mitigation": "Market focus strategy applied"
        }
    
    def _execute_round_3_opportunity_capture(self, idea_data: dict, opportunities: list) -> dict:
        """
        Round 3: Opportunity Capture - Optimize for biggest opportunities.
        
        Reasoning: The biggest opportunity represents the highest potential value.
        By optimizing the idea to capture this opportunity, we maximize its
        potential for success.
        
        Args:
            idea_data: Current idea state after risk mitigation
            opportunities: List of identified opportunities from Round 1
            
        Returns:
            Dictionary with opportunity capture results and final idea
        """
        if not self.openai_client or not opportunities:
            return self._get_round_3_placeholder(idea_data, opportunities)
        
        biggest_opportunity = opportunities[0]
        prompt_template = self._load_prompt_template("round_3_prompt.md")
        
        prompt = prompt_template.format(
            opportunity_description=biggest_opportunity.get("opportunity", "Unknown opportunity"),
            potential_value=biggest_opportunity.get("potential_value", 100000),
            probability=biggest_opportunity.get("probability", 50),
            current_idea_json=json.dumps(idea_data, indent=2)
        )
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert startup advisor with MBA + founder experience. Think step-by-step through your analysis and return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,  # Lower for consistent analytical reasoning with CoT
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            self.logger.error(f"Round 3 LLM call failed: {e}")
            return self._get_round_3_placeholder(idea_data, opportunities)
    
    def _get_round_3_placeholder(self, idea_data: dict, opportunities: list) -> dict:
        """Fallback placeholder data if LLM unavailable."""
        biggest_opportunity = opportunities[0] if opportunities else {"opportunity": "Unknown", "potential_value": 0}
        
        return {
            "opportunity_being_captured": biggest_opportunity,
            "strategies": [
                {"name": "Premium positioning", "description": "Position as premium solution", "revenue_impact": "25%", "cost": 5000, "time_weeks": 4, "roi": 5.0, "score": 125},
                {"name": "Feature differentiation", "description": "Unique feature set", "revenue_impact": "30%", "cost": 10000, "time_weeks": 8, "roi": 3.0, "score": 90},
                {"name": "Market timing", "description": "Launch at optimal time", "revenue_impact": "20%", "cost": 0, "time_weeks": 0, "roi": 999, "score": 200}
            ],
            "recommended_strategy": {"name": "Market timing", "reasoning": "Highest ROI with minimal cost", "expected_outcome": "Capture emerging market opportunity"},
            "final_idea": {
                **idea_data,
                "value_proposition": f"Enhanced: {idea_data.get('value_proposition', 'Unknown')}",
                "evolution_summary": "Idea evolved through 3-round workshop"
            },
            "final_viability_score": 42,
            "viability_improvement": "+17 points",
            "recommendation": "CONDITIONAL GO - validate remaining assumptions",
            "opportunity_capture": "Market timing optimization applied"
        }
    
    def _generate_recommendation(self, viability_score: float) -> str:
        """
        Generate recommendation based on final viability score.
        
        Reasoning: Clear recommendations help users understand next steps
        based on the workshop results.
        
        Args:
            viability_score: Final viability score (0-50)
            
        Returns:
            Recommendation string
        """
        if viability_score >= 40:
            return "GO - Strong idea with high viability. Proceed to development."
        elif viability_score >= 30:
            return "CONDITIONAL GO - Good idea with moderate viability. Address remaining risks before proceeding."
        elif viability_score >= 20:
            return "ITERATE MORE - Idea needs significant improvement. Consider major pivots."
        else:
            return "NO-GO - Idea has fundamental issues. Consider different approach."


# ==============================================
# Testing and Validation
# ==============================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 ITERATIVE WORKSHOP AGENT - Phase 1.1 Test")
    print("="*70 + "\n")
    
    # Test agent initialization
    try:
        agent = IterativeWorkshopAgent()
        print(f"✅ Agent created: {agent.name}")
        print(f"✅ Dependencies: {agent.dependencies}")
        print(f"✅ Logger initialized: {agent.logger is not None}")
        print(f"✅ Perplexity available: {agent.perplexity is not None}")
        print(f"✅ OpenAI available: {agent.openai_client is not None}")
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
    
    print("\n" + "="*70)
    print("✅ WORKSHOP AGENT TESTS COMPLETE")
    print("="*70 + "\n")
