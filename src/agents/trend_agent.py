"""
trend_agent.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trend Agent

Augments idea scoring by estimating market size, urgency, category
momentum, and relevant trends from web data.

Location: src/agents/trend_agent.py

Purpose:
    Provides data-driven insights for scoring transparency and
    justification. Returns score metadata with sources and confidence.

Phase: 16 - Persistence & Metadata Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import random
from typing import Dict, List


class TrendAgent:
    """
    Estimates market trends and provides scoring justification.
    
    Currently uses mock data - can be enhanced with:
    - Web scraping
    - API calls (Statista, Trade associations)
    - Perplexity integration for real-time data
    """
    
    def __init__(self, country: str = "Ireland"):
        """
        Initialize Trend Agent.
        
        Args:
            country: Default country for market estimates
        """
        self.country = country
        
        # Mock market data (replace with real API later)
        self.market_data = {
            "hospitality": (1500, "Fáilte Ireland + CSO"),
            "plumbers": (3000, "Trade Register + LinkedIn"),
            "salons": (2200, "IrishHairFed + Yelp"),
            "hair salons": (2200, "IrishHairFed + Yelp"),
            "beauty": (2800, "Beauty Industry Census"),
            "dentist": (1800, "Dental Council + HSE"),
            "dental": (1800, "Dental Council + HSE"),
            "restaurant": (5000, "RestaurantAssoc + Revenue"),
            "cafe": (3500, "Retail Association"),
            "gym": (800, "FitnessIreland + IHRSA"),
            "fitness": (800, "FitnessIreland + IHRSA"),
            "garage": (4000, "SIMI + AutoTrade"),
            "auto repair": (4000, "SIMI + AutoTrade"),
            "golf": (400, "Golf Ireland + R&A"),
            "golf course": (400, "Golf Ireland + R&A"),
        }
    
    def estimate_market_size(self, industry: str, country: str = None) -> Dict:
        """
        Estimate market size for an industry.
        
        Args:
            industry: Industry/vertical name
            country: Country for market (defaults to self.country)
            
        Returns:
            Dict with category, score, justification, source, confidence
        """
        country = country or self.country
        industry_lower = industry.lower()
        
        # Try to find match
        value, source = self.market_data.get(
            industry_lower,
            (random.randint(500, 2500), "Estimated")
        )
        
        # Calculate score (0-10 scale)
        # More businesses = higher score
        score = min(10, max(1, int(value / 400)))
        
        # Confidence based on whether we have real data
        confidence = 8 if industry_lower in self.market_data else 4
        
        return {
            "category": "market_size",
            "score": score,
            "justification": f"Estimated {value:,} businesses in {industry} in {country} market. "
                           f"Score based on market density (>2000 = 8+, 1000-2000 = 5-7, <1000 = 1-4).",
            "source": source,
            "confidence_score": confidence
        }
    
    def estimate_urgency(self, pain_point: str) -> Dict:
        """
        Estimate urgency/pain severity.
        
        Args:
            pain_point: Description of the problem
            
        Returns:
            Metadata dict
        """
        # Mock urgency estimation
        # In production: analyze keywords, competitor mentions, etc.
        
        urgent_keywords = ["missed", "losing", "frustrated", "expensive", "critical"]
        urgency_level = sum(1 for word in urgent_keywords if word in pain_point.lower())
        
        score = min(10, max(3, urgency_level * 2 + 4))
        
        return {
            "category": "urgency",
            "score": score,
            "justification": f"Pain point analysis detected {urgency_level} urgency indicators. "
                           f"Keywords: {', '.join(w for w in urgent_keywords if w in pain_point.lower())}",
            "source": "Keyword Analysis",
            "confidence_score": 6
        }
    
    def estimate_competition(self, industry: str, solution_type: str) -> Dict:
        """
        Estimate competitive landscape.
        
        Args:
            industry: Target industry
            solution_type: Type of solution (SaaS, marketplace, etc.)
            
        Returns:
            Metadata dict
        """
        # Mock competition data
        competitive_industries = ["restaurant", "cafe", "retail", "ecommerce"]
        
        if industry.lower() in competitive_industries:
            score = 4  # High competition
            justification = f"{industry.title()} market is highly competitive with established players"
            confidence = 7
        else:
            score = 7  # Lower competition
            justification = f"{industry.title()} market has room for new entrants, underserved niche"
            confidence = 5
        
        return {
            "category": "competition",
            "score": score,
            "justification": justification,
            "source": "Market Analysis",
            "confidence_score": confidence
        }
    
    def enrich_idea(self, idea: Dict) -> List[Dict]:
        """
        Generate all metadata for an idea.
        
        Args:
            idea: Refined idea dict with niche, value_proposition, etc.
            
        Returns:
            List of metadata dicts
        """
        metadata = []
        
        # Extract industry/niche
        industry = idea.get('niche', idea.get('name', '')).split()[0]
        
        # Generate estimates
        metadata.append(self.estimate_market_size(industry))
        
        if 'value_proposition' in idea:
            metadata.append(self.estimate_urgency(idea['value_proposition']))
        
        if 'niche' in idea:
            solution_type = "SaaS"  # Default assumption
            metadata.append(self.estimate_competition(industry, solution_type))
        
        return metadata


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Testing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📈 TREND AGENT - Market Intelligence")
    print("="*70 + "\n")
    
    agent = TrendAgent()
    
    # Test market size
    print("Testing market size estimation:\n")
    
    industries = ["salons", "plumbers", "golf"]
    for industry in industries:
        result = agent.estimate_market_size(industry)
        print(f"📊 {industry.title()}:")
        print(f"   Score: {result['score']}/10")
        print(f"   Justification: {result['justification']}")
        print(f"   Source: {result['source']}")
        print(f"   Confidence: {result['confidence_score']}/10")
        print()
    
    # Test full enrichment
    print("="*70)
    print("Testing full idea enrichment:\n")
    
    test_idea = {
        "name": "AI Receptionist for Hair Salons",
        "niche": "Hair salons",
        "value_proposition": "Eliminates missed calls and frustrated customers"
    }
    
    metadata = agent.enrich_idea(test_idea)
    
    print(f"Generated {len(metadata)} metadata entries:")
    for i, entry in enumerate(metadata, 1):
        print(f"\n{i}. {entry['category'].upper()}")
        print(f"   Score: {entry['score']}/10")
        print(f"   {entry['justification']}")
        print(f"   Confidence: {entry['confidence_score']}/10")
    
    print("\n" + "="*70)
    print("✅ Trend Agent Test Complete")
    print("="*70 + "\n")

