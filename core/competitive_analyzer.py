"""
Competitive Analyzer - Competitive intelligence for Step 4

Analyzes competitive landscape to extract:
- Direct and indirect competitors
- Feature sets and capabilities
- Pricing tiers and models
- Customer complaints and pain points
- Market gaps and opportunities
- Positioning recommendations

Uses AI + research to provide actionable competitive intelligence.

Created: 2025-10-24 (Pain Discovery Enhancement)
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    from src.utils.config_loader import get_env, load_env
    from src.integrations.evidence_collector import EvidenceCollector
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI or dependencies not available")


class CompetitiveAnalyzer:
    """
    Analyzes competitive landscape for idea validation.

    Provides:
    - Competitor identification (direct + indirect)
    - Feature extraction
    - Pricing analysis
    - Customer complaint mining
    - Gap analysis
    - Positioning recommendations
    """

    # Pricing extraction patterns
    PRICING_PATTERNS = [
        r'[$£€]\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:per|/|a)?\s*(?:mo|month|yr|year)?',
        r'(\d+)\s*(?:dollars?|pounds?|euros?)\s*(?:per|a|/)\s*(?:month|year)',
        r'pricing:\s*[$£€]?\s*(\d+(?:,\d{3})*)',
        r'costs?\s*[$£€]?\s*(\d+(?:,\d{3})*)',
        r'starts?\s+at\s*[$£€]?\s*(\d+(?:,\d{3})*)',
    ]

    # Feature indicators
    FEATURE_KEYWORDS = [
        "feature", "capability", "offers", "includes", "supports",
        "integration", "API", "dashboard", "analytics", "automation"
    ]

    # Complaint indicators
    COMPLAINT_KEYWORDS = {
        "critical": [
            "terrible", "awful", "worst", "horrible", "useless",
            "broken", "doesn't work", "scam", "waste of money"
        ],
        "major": [
            "frustrating", "annoying", "disappointed", "poor", "bad",
            "lacking", "missing", "limited", "expensive"
        ],
        "minor": [
            "wish", "would be nice", "could improve", "needs",
            "should have", "missing feature"
        ]
    }

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """Initialize competitive analyzer."""
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None
        self.available = False
        self.evidence_collector = None

        if OPENAI_AVAILABLE:
            load_env()
            api_key = get_env("OPENAI_API_KEY")
            if api_key:
                try:
                    self.client = OpenAI(api_key=api_key)
                    self.evidence_collector = EvidenceCollector()
                    self.available = True
                    logger.info("✅ Competitive Analyzer initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize CompetitiveAnalyzer: {e}")

    def is_available(self) -> bool:
        """Check if analyzer is available."""
        return self.available and self.client is not None

    def analyze_competitors(
        self,
        refinement_data: Dict[str, Any],
        known_competitors: Optional[List[str]] = None,
        geography: str = "Ireland/UK"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive competitive analysis.

        Args:
            refinement_data: Idea context from Step 1
            known_competitors: User-provided competitor names
            geography: Geographic focus

        Returns:
            {
                "competitors": [
                    {
                        "name": "CallJoy",
                        "type": "direct",  # direct | indirect
                        "pricing": {
                            "model": "subscription",
                            "tiers": ["$89/month"],
                            "target": "small business"
                        },
                        "features": [
                            "Call routing",
                            "Voicemail transcription",
                            ...
                        ],
                        "customer_complaints": [
                            {
                                "complaint": "Limited customization",
                                "severity": "major",
                                "count": 12
                            }
                        ],
                        "positioning": "Google-backed, SMB focus"
                    }
                ],
                "market_gaps": [
                    {
                        "gap": "Affordable AI receptionist for SMBs",
                        "opportunity": "£50-£200/month price point",
                        "reasoning": "Competitors too expensive or too basic"
                    }
                ],
                "positioning_recommendations": [
                    "Focus on UK/Ireland market",
                    "Industry-specific templates",
                    "Affordable pricing for SMBs"
                ]
            }
        """
        logger.info("Starting competitive analysis")

        if not self.is_available():
            return self._fallback_analysis(refinement_data, known_competitors)

        # Step 1: Identify competitors
        competitors = self._identify_competitors(refinement_data, known_competitors)

        # Step 2: Research each competitor
        competitor_profiles = []
        for comp_name in competitors[:10]:  # Limit to top 10
            profile = self._research_competitor(comp_name, refinement_data, geography)
            if profile:
                competitor_profiles.append(profile)

        # Step 3: Analyze market gaps
        gaps = self._identify_market_gaps(competitor_profiles, refinement_data)

        # Step 4: Generate positioning recommendations
        positioning = self._generate_positioning_recommendations(
            competitor_profiles,
            gaps,
            refinement_data,
            geography
        )

        return {
            "competitors": competitor_profiles,
            "total_competitors_found": len(competitor_profiles),
            "market_gaps": gaps,
            "positioning_recommendations": positioning,
            "analyzed_at": datetime.now().isoformat(),
            "geography": geography
        }

    def _identify_competitors(
        self,
        refinement_data: Dict[str, Any],
        known_competitors: Optional[List[str]]
    ) -> List[str]:
        """
        Identify competitors using AI.

        Args:
            refinement_data: Idea context
            known_competitors: User-provided competitors

        Returns:
            List of competitor names
        """
        try:
            prompt = self._build_competitor_identification_prompt(refinement_data)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_competitor_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=500,
                timeout=15,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            ai_competitors = result.get('competitors', [])

            # Combine AI-found + user-provided
            all_competitors = list(set(
                (known_competitors or []) + ai_competitors
            ))

            logger.info(f"Identified {len(all_competitors)} competitors")
            return all_competitors

        except Exception as e:
            logger.error(f"Competitor identification failed: {e}", exc_info=True)
            return known_competitors or []

    def _research_competitor(
        self,
        competitor_name: str,
        refinement_data: Dict[str, Any],
        geography: str
    ) -> Optional[Dict[str, Any]]:
        """
        Research a specific competitor.

        Extracts:
        - Pricing
        - Features
        - Customer complaints
        - Positioning
        """
        try:
            # Search for competitor information
            search_keywords = [
                f"{competitor_name} pricing",
                f"{competitor_name} features",
                f"{competitor_name} review",
                f"{competitor_name} alternative"
            ]

            evidence = self.evidence_collector.collect_all_evidence(
                idea=competitor_name,
                keywords=search_keywords,
                parallel=False  # Sequential for reliability
            )

            # Extract pricing
            pricing = self._extract_pricing(evidence, competitor_name)

            # Extract features
            features = self._extract_features(evidence, competitor_name)

            # Extract complaints
            complaints = self._extract_complaints(evidence, competitor_name)

            # Determine type (direct vs indirect)
            comp_type = self._classify_competitor_type(
                competitor_name,
                features,
                refinement_data
            )

            return {
                "name": competitor_name,
                "type": comp_type,
                "pricing": pricing,
                "features": features,
                "customer_complaints": complaints,
                "positioning": self._extract_positioning(evidence, competitor_name)
            }

        except Exception as e:
            logger.warning(f"Failed to research {competitor_name}: {e}")
            return None

    def _extract_pricing(
        self,
        evidence: Dict[str, Any],
        competitor_name: str
    ) -> Dict[str, Any]:
        """Extract pricing information from evidence."""
        prices = []
        pricing_context = []

        sources = evidence.get('sources', {})

        for source_name, source_data in sources.items():
            if isinstance(source_data, dict) and 'error' not in source_data:
                # Get text content
                texts = self._extract_text_from_source(source_data)

                for text in texts:
                    # Find pricing mentions
                    for pattern in self.PRICING_PATTERNS:
                        matches = re.findall(pattern, text, re.IGNORECASE)
                        if matches:
                            prices.extend(matches)
                            # Extract context
                            context = text[max(0, text.find(matches[0])-100):
                                         min(len(text), text.find(matches[0])+100)]
                            pricing_context.append(context)

        if not prices:
            return {
                "model": "unknown",
                "tiers": [],
                "target": "unknown"
            }

        # Parse pricing
        parsed_prices = []
        for price in prices:
            try:
                clean_price = price.replace(',', '')
                parsed_prices.append(float(clean_price))
            except (ValueError, AttributeError):
                continue

        if parsed_prices:
            avg_price = sum(parsed_prices) / len(parsed_prices)
            return {
                "model": "subscription" if any("month" in ctx.lower() for ctx in pricing_context) else "unknown",
                "tiers": [f"${int(p)}/month" for p in sorted(set(parsed_prices))[:3]],  # Top 3 tiers
                "target": "enterprise" if avg_price > 500 else "small business"
            }
        else:
            return {
                "model": "subscription",
                "tiers": [],
                "target": "unknown"
            }

    def _extract_features(
        self,
        evidence: Dict[str, Any],
        competitor_name: str
    ) -> List[str]:
        """Extract feature list from evidence."""
        features = []

        sources = evidence.get('sources', {})

        for source_name, source_data in sources.items():
            if isinstance(source_data, dict) and 'error' not in source_data:
                texts = self._extract_text_from_source(source_data)

                for text in texts:
                    # Look for feature-related sentences
                    sentences = text.split('.')
                    for sentence in sentences:
                        sentence_lower = sentence.lower()
                        if any(keyword in sentence_lower for keyword in self.FEATURE_KEYWORDS):
                            # Extract potential feature
                            feature = sentence.strip()
                            if 10 < len(feature) < 100:
                                features.append(feature)

        # Deduplicate and return top features
        return list(set(features))[:10]

    def _extract_complaints(
        self,
        evidence: Dict[str, Any],
        competitor_name: str
    ) -> List[Dict[str, Any]]:
        """Extract customer complaints from evidence."""
        complaints = defaultdict(int)
        complaint_severity = {}

        sources = evidence.get('sources', {})

        for source_name, source_data in sources.items():
            if isinstance(source_data, dict) and 'error' not in source_data:
                texts = self._extract_text_from_source(source_data)

                for text in texts:
                    text_lower = text.lower()

                    # Check for complaints by severity
                    for severity, keywords in self.COMPLAINT_KEYWORDS.items():
                        for keyword in keywords:
                            if keyword in text_lower:
                                # Extract complaint context
                                sentences = text.split('.')
                                for sentence in sentences:
                                    if keyword in sentence.lower() and len(sentence) > 20:
                                        complaint = sentence.strip()
                                        complaints[complaint] += 1
                                        if complaint not in complaint_severity:
                                            complaint_severity[complaint] = severity

        # Format complaints
        return [
            {
                "complaint": complaint[:150],  # Truncate
                "severity": complaint_severity.get(complaint, "minor"),
                "count": count
            }
            for complaint, count in complaints.most_common(10)
        ]

    def _extract_positioning(
        self,
        evidence: Dict[str, Any],
        competitor_name: str
    ) -> str:
        """Extract competitive positioning."""
        # Simple heuristic - could be enhanced with AI
        sources = evidence.get('sources', {})

        descriptions = []

        for source_name, source_data in sources.items():
            if isinstance(source_data, dict) and 'error' not in source_data:
                texts = self._extract_text_from_source(source_data)

                for text in texts[:3]:  # First 3 texts
                    # Extract first sentence mentioning competitor
                    if competitor_name.lower() in text.lower():
                        sentences = text.split('.')
                        for sentence in sentences:
                            if competitor_name.lower() in sentence.lower():
                                descriptions.append(sentence.strip())
                                break

        if descriptions:
            return descriptions[0][:200]  # Return first description
        else:
            return "Unknown positioning"

    def _classify_competitor_type(
        self,
        competitor_name: str,
        features: List[str],
        refinement_data: Dict[str, Any]
    ) -> str:
        """Classify as direct or indirect competitor."""
        # Simple heuristic based on feature overlap
        core_idea = refinement_data.get('core_idea', '').lower()
        value_prop = refinement_data.get('value_proposition', '').lower()

        # Check if competitor features match core idea
        feature_text = ' '.join(features).lower()

        core_terms = set(core_idea.split())
        value_terms = set(value_prop.split())

        # Calculate overlap
        feature_terms = set(feature_text.split())
        overlap = len((core_terms | value_terms) & feature_terms)

        return "direct" if overlap > 3 else "indirect"

    def _identify_market_gaps(
        self,
        competitors: List[Dict[str, Any]],
        refinement_data: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Identify market gaps based on competitive analysis."""
        gaps = []

        # Gap 1: Pricing gaps
        prices = []
        for comp in competitors:
            pricing = comp.get('pricing', {})
            for tier in pricing.get('tiers', []):
                # Extract numeric price
                match = re.search(r'(\d+)', tier)
                if match:
                    prices.append(int(match.group(1)))

        if prices:
            avg_price = sum(prices) / len(prices)
            if avg_price > 200:
                gaps.append({
                    "gap": "Affordable pricing for SMBs",
                    "opportunity": f"£50-£200/month price point",
                    "reasoning": f"Competitors averaging ${int(avg_price)}/month - too expensive for small businesses"
                })

        # Gap 2: Feature gaps (based on complaints)
        all_complaints = []
        for comp in competitors:
            all_complaints.extend([c['complaint'] for c in comp.get('customer_complaints', [])])

        complaint_themes = Counter(all_complaints).most_common(5)
        for theme, count in complaint_themes:
            if count > 2:  # Multiple mentions
                gaps.append({
                    "gap": f"Address: {theme[:100]}",
                    "opportunity": "Feature differentiation",
                    "reasoning": f"Mentioned {count} times across competitors"
                })

        # Gap 3: Geographic gaps
        target_geo = refinement_data.get('geography', 'Ireland/UK')
        if "UK" in target_geo or "Ireland" in target_geo:
            gaps.append({
                "gap": "UK/Ireland market focus",
                "opportunity": "Regional expertise and support",
                "reasoning": "Most competitors US-focused"
            })

        return gaps[:5]  # Top 5 gaps

    def _generate_positioning_recommendations(
        self,
        competitors: List[Dict[str, Any]],
        gaps: List[Dict[str, str]],
        refinement_data: Dict[str, Any],
        geography: str
    ) -> List[str]:
        """Generate positioning recommendations."""
        recommendations = []

        # Based on gaps
        for gap in gaps:
            recommendations.append(gap['opportunity'])

        # Based on competitor weaknesses
        complaint_counts = defaultdict(int)
        for comp in competitors:
            for complaint in comp.get('customer_complaints', []):
                if complaint['severity'] in ['critical', 'major']:
                    complaint_counts[complaint['complaint'][:50]] += 1

        for complaint, count in sorted(complaint_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            recommendations.append(f"Address competitor weakness: {complaint}")

        # Geographic recommendation
        if geography:
            recommendations.append(f"Emphasize {geography} market expertise")

        return recommendations[:5]  # Top 5

    def _extract_text_from_source(self, source_data: Dict[str, Any]) -> List[str]:
        """Extract text content from source data."""
        texts = []

        # Reddit
        if 'posts' in source_data:
            for post in source_data['posts']:
                if isinstance(post, dict):
                    texts.append(post.get('title', '') + ' ' + post.get('selftext', ''))
                    for comment in post.get('top_comments', []):
                        if isinstance(comment, dict):
                            texts.append(comment.get('body', ''))

        # Twitter/X
        if 'tweets' in source_data:
            for tweet in source_data['tweets']:
                if isinstance(tweet, dict):
                    texts.append(tweet.get('text', ''))

        return [t for t in texts if t and len(t) > 20]

    def _build_competitor_identification_prompt(
        self,
        refinement_data: Dict[str, Any]
    ) -> str:
        """Build prompt for competitor identification."""
        core_idea = refinement_data.get('core_idea', '')
        target_customer = refinement_data.get('target_customer', '')
        industry = refinement_data.get('industry', '')
        value_prop = refinement_data.get('value_proposition', '')

        return f"""Identify direct and indirect competitors for this business idea:

**Idea:** {core_idea}
**Target Customer:** {target_customer}
**Industry:** {industry}
**Value Proposition:** {value_prop}

Return a JSON object with competitor names:
{{
  "competitors": ["Competitor 1", "Competitor 2", ...]
}}

Include:
- Direct competitors (same solution for same problem)
- Indirect competitors (different solution for same problem)
- Adjacent solutions (related tools customers might use)

Limit to 10-15 most relevant competitors."""

    def _get_competitor_system_prompt(self) -> str:
        """System prompt for competitor identification."""
        return """You are a competitive intelligence analyst.

Your task is to identify relevant competitors for a business idea.

Return only JSON with competitor names. No additional commentary."""

    def _fallback_analysis(
        self,
        refinement_data: Dict[str, Any],
        known_competitors: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Fallback when AI unavailable."""
        logger.info("Using fallback competitive analysis")

        competitors = []
        if known_competitors:
            for comp in known_competitors:
                competitors.append({
                    "name": comp,
                    "type": "unknown",
                    "pricing": {"model": "unknown", "tiers": [], "target": "unknown"},
                    "features": [],
                    "customer_complaints": [],
                    "positioning": "Unknown positioning"
                })

        return {
            "competitors": competitors,
            "total_competitors_found": len(competitors),
            "market_gaps": [],
            "positioning_recommendations": [],
            "analyzed_at": datetime.now().isoformat(),
            "fallback_mode": True
        }

    def format_for_display(self, analysis_data: Dict[str, Any]) -> str:
        """Format competitive analysis for console display."""
        lines = []
        lines.append("\n" + "="*70)
        lines.append("⚔️  COMPETITIVE ANALYSIS")
        lines.append("="*70)

        # Competitors found
        competitors = analysis_data.get('competitors', [])
        lines.append(f"\n🏢 Competitors Found: {len(competitors)}")

        for i, comp in enumerate(competitors[:5], 1):  # Top 5
            lines.append(f"\n{i}. {comp.get('name', 'Unknown')} ({comp.get('type', 'unknown')})")

            pricing = comp.get('pricing', {})
            tiers = pricing.get('tiers', [])
            if tiers:
                lines.append(f"   💰 Pricing: {', '.join(tiers)}")

            features = comp.get('features', [])
            if features:
                lines.append(f"   ✓ Features: {len(features)} found")
                for feat in features[:3]:
                    lines.append(f"      • {feat[:80]}")

            complaints = comp.get('customer_complaints', [])
            if complaints:
                lines.append(f"   ⚠️  Top Complaints:")
                for complaint in complaints[:2]:
                    lines.append(f"      • \"{complaint['complaint'][:80]}\" ({complaint['count']} mentions)")

        # Market gaps
        gaps = analysis_data.get('market_gaps', [])
        if gaps:
            lines.append(f"\n📊 Market Gaps Identified:")
            for gap in gaps:
                lines.append(f"\n   ✓ {gap.get('gap', '')}")
                lines.append(f"     → Opportunity: {gap.get('opportunity', '')}")
                lines.append(f"     → Why: {gap.get('reasoning', '')}")

        # Positioning recommendations
        recommendations = analysis_data.get('positioning_recommendations', [])
        if recommendations:
            lines.append(f"\n🎯 Positioning Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"   {i}. {rec}")

        lines.append("\n" + "="*70)

        return "\n".join(lines)
