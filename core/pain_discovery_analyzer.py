"""
Pain Discovery Analyzer - Enhanced pain validation with rich signals

Analyzes pain discovery research to extract:
- Conversation volume and frequency
- Sentiment analysis (pain vs. seeking solutions)
- Willingness-to-pay signals (pricing mentions, budget discussions)
- Urgency indicators ("need NOW" vs "would be nice")
- Top pain quotes with context
- Validation confidence scoring

Integrates with:
- EvidenceCollector (Reddit, Twitter/X, Google Trends)
- PainPointExtractor (NER + sentiment)
- KeywordGenerator (contextual keywords)

Created: 2025-10-24 (Pain Discovery Enhancement)
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from collections import Counter

logger = logging.getLogger(__name__)

try:
    from src.integrations.evidence_collector import EvidenceCollector
    from src.ml.pain_point_extractor import PainPointExtractor
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    logger.warning("Evidence collector or pain point extractor not available")

# Try to import v4 enhanced collector
try:
    import sys
    from pathlib import Path
    # Add parent directory to path if not already there
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from src.integrations.message_collector_v4_enhanced import (
        collect_reddit_enhanced,
        collect_trends_enhanced,
        KEYWORDS as FALLBACK_KEYWORDS_V4
    )
    from src.analysis.demand_validator import DemandValidator
    V4_COLLECTOR_AVAILABLE = True
    logger.info("✅ V4 enhanced collector available")
except ImportError as e:
    V4_COLLECTOR_AVAILABLE = False
    logger.warning(f"V4 enhanced collector not available: {e}")


class PainDiscoveryAnalyzer:
    """
    Analyzes pain discovery research with rich signal extraction.

    Provides:
    - Demand signal strength (0-10)
    - Conversation volume across platforms
    - Top pain quotes with metadata
    - Willingness-to-pay indicators
    - Urgency scoring
    - Validation confidence (0-100%)
    """

    # Pricing pattern regex
    PRICING_PATTERNS = [
        r'[$£€][\d,]+(?:\.\d{2})?(?:/mo|/month|/yr|/year)?',  # $500/month, £1,200
        r'\d+\s*(?:dollars?|pounds?|euros?)\s*(?:per|a|/)\s*(?:month|year)',  # 500 dollars per month
        r'costs?\s*[$£€]?[\d,]+',  # costs $500
        r'pay(?:ing)?\s*[$£€]?[\d,]+',  # paying $1000
        r'budget\s*(?:of|is)?\s*[$£€]?[\d,]+',  # budget of $2000
    ]

    # Urgency indicators (ranked by intensity)
    URGENCY_KEYWORDS = {
        "critical": [
            "urgently need", "immediately", "ASAP", "critical", "emergency",
            "losing money", "losing customers", "can't afford to wait"
        ],
        "high": [
            "need now", "need this", "must have", "essential", "required",
            "as soon as possible", "right away", "quickly"
        ],
        "medium": [
            "looking for", "need to find", "searching for", "trying to",
            "want to buy", "in the market", "considering"
        ],
        "low": [
            "would be nice", "wish", "hope", "maybe", "someday",
            "eventually", "when i get time", "nice to have"
        ]
    }

    # Pay willingness indicators
    PAY_WILLINGNESS_PATTERNS = [
        r'(?:would|will)\s+pay',
        r'willing\s+to\s+pay',
        r'budget\s+for',
        r'affordable\s+(?:at|if|for)',
        r'worth\s+[$£€]',
        r'happy\s+to\s+pay',
    ]

    def __init__(self):
        """Initialize pain discovery analyzer."""
        self.evidence_collector = None
        self.pain_extractor = None

        if DEPENDENCIES_AVAILABLE:
            try:
                self.evidence_collector = EvidenceCollector()
                self.pain_extractor = PainPointExtractor()
                logger.info("✅ Pain Discovery Analyzer initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize dependencies: {e}")

    def use_v4_enhanced_collector(
        self,
        keywords: List[str],
        output_path: str = "data/raw/social_posts_enriched.csv"
    ) -> bool:
        """
        Use the enhanced v4 collector for enriched data gathering.

        Args:
            keywords: List of keywords to search
            output_path: Path to save CSV output

        Returns:
            True if collection succeeded with sufficient data
        """
        if not V4_COLLECTOR_AVAILABLE:
            logger.warning("V4 enhanced collector not available, falling back to old collector")
            return False

        try:
            logger.info("Running V4 enhanced collector (ICP, urgency, competitors, pricing)...")

            # Import necessary components
            import pandas as pd
            import csv
            from tqdm import tqdm
            from src.integrations import message_collector_v4_enhanced

            # Override keywords temporarily
            original_keywords = message_collector_v4_enhanced.KEYWORDS
            message_collector_v4_enhanced.KEYWORDS = keywords
            message_collector_v4_enhanced.OUTPUT_FILE = output_path

            # Run enhanced collection
            all_records = []
            for kw in tqdm(keywords, desc="Collecting"):
                reddit_data = message_collector_v4_enhanced.collect_reddit_enhanced(kw)
                trends_data = message_collector_v4_enhanced.collect_trends_enhanced(kw)

                # Add trend data to posts
                for record in reddit_data:
                    record["trend_avg"] = trends_data["avg_interest"]
                    all_records.append(record)

            # Restore original keywords
            message_collector_v4_enhanced.KEYWORDS = original_keywords

            if not all_records:
                logger.warning("V4 collector returned no data")
                return False

            # Save enriched data
            df = pd.DataFrame(all_records)
            df.drop_duplicates(subset=["text_excerpt"], inplace=True)
            df.to_csv(output_path, index=False, quoting=csv.QUOTE_MINIMAL)

            if len(df) < 10:
                logger.warning(f"V4 collector returned insufficient data (< 10 posts): {len(df)}")
                return False

            logger.info(f"✅ V4 enhanced collector succeeded: {len(df)} posts collected")
            logger.info(f"   Industries identified: {df['industry'].notna().sum()}")
            logger.info(f"   Critical urgency: {(df['urgency'] == 'critical').sum()}")
            logger.info(f"   Budget concerns: {df['has_budget_concern'].sum()}")
            return True

        except Exception as e:
            logger.error(f"V4 enhanced collector failed: {e}", exc_info=True)
            return False

    def analyze_pain_discovery(
        self,
        keywords: List[str],
        refinement_data: Dict[str, Any],
        platforms: List[str] = None,
        geography: str = "Ireland/UK",
        use_v2: bool = True
    ) -> Dict[str, Any]:
        """
        Perform comprehensive pain discovery analysis.

        Args:
            keywords: Search keywords (from KeywordGenerator)
            refinement_data: Idea context from Step 1
            platforms: Platforms to search (default: all)
            geography: Geographic focus

        Returns:
            {
                "demand_signal_strength": 8.2,  # 0-10
                "conversation_volume": {
                    "reddit": 247,
                    "twitter": 89,
                    "google_trends": "↗️ +34%"
                },
                "top_pain_quotes": [
                    {
                        "quote": "We lose 10+ leads per week...",
                        "source": "r/smallbusiness",
                        "metadata": {"upvotes": 84, "author_type": "Business owner"}
                    }
                ],
                "willingness_to_pay": {
                    "mentions_count": 34,
                    "price_range": "£500-£2,000/month",
                    "signals": ["would pay", "budget for", ...]
                },
                "urgency_analysis": {
                    "critical": 5,
                    "high": 12,
                    "medium": 34,
                    "low": 8
                },
                "key_concerns": [
                    {"concern": "AI sounds robotic", "count": 23}
                ],
                "validation_decision": {
                    "confidence": 82,  # 0-100%
                    "recommendation": "PROCEED",  # PROCEED | REFINE | STOP
                    "reasoning": "Pain is real and widespread..."
                }
            }
        """
        logger.info(f"Starting pain discovery analysis with {len(keywords)} keywords")

        # Try V4 enhanced collector first (if enabled)
        v4_success = False
        demand_report = None

        if use_v2:  # Reusing use_v2 parameter for v4 for backwards compatibility
            v4_success = self.use_v4_enhanced_collector(keywords)

            # Generate demand validation report
            if v4_success:
                try:
                    logger.info("Generating demand validation report...")
                    validator = DemandValidator("data/raw/social_posts_enriched.csv")
                    demand_report = validator.generate_full_report()
                    logger.info("✅ Demand validation report generated")
                except Exception as e:
                    logger.warning(f"Failed to generate demand report: {e}")

        # Collect evidence (use old method if v4 failed)
        if v4_success and demand_report:
            # Use demand report data
            logger.info("Using V4 enhanced collector data for analysis")
            evidence = {"enriched": True, "demand_report": demand_report}
        else:
            evidence = self._collect_evidence(keywords, platforms)

        # Extract pain points
        pain_points = self._extract_pain_points(evidence)

        # Analyze willingness to pay
        pay_signals = self._analyze_willingness_to_pay(evidence)

        # Analyze urgency
        urgency = self._analyze_urgency(evidence)

        # Extract top quotes
        top_quotes = self._extract_top_quotes(evidence, pain_points)

        # Identify concerns
        concerns = self._identify_concerns(pain_points)

        # Calculate demand signal
        demand_signal = self._calculate_demand_signal(
            evidence, pain_points, pay_signals, urgency
        )

        # Make validation decision
        validation = self._make_validation_decision(
            demand_signal, pay_signals, urgency, concerns
        )

        # Build base result
        result = {
            "demand_signal_strength": demand_signal,
            "conversation_volume": self._format_conversation_volume(evidence),
            "top_pain_quotes": top_quotes[:5],  # Top 5
            "willingness_to_pay": pay_signals,
            "urgency_analysis": urgency,
            "key_concerns": concerns[:5],  # Top 5
            "validation_decision": validation,
            "analyzed_at": datetime.now().isoformat(),
            "keywords_analyzed": keywords,
            "geography": geography
        }

        # Add enriched data if available
        if demand_report:
            result["enriched_analysis"] = {
                "icp": demand_report.get("icp"),
                "feature_priorities": demand_report.get("feature_priorities"),
                "competitor_intelligence": demand_report.get("competitor_intelligence"),
                "pricing_signals": demand_report.get("pricing_signals"),
                "sales_talk_track": demand_report.get("sales_talk_track"),
                "top_pain_quotes_ranked": demand_report.get("top_pain_quotes", [])[:10],
                "total_posts_analyzed": demand_report.get("summary", {}).get("total_posts_analyzed", 0)
            }
            logger.info("✅ Added enriched analysis to results")

        return result

    def _convert_v2_to_evidence(self, df) -> Dict[str, Any]:
        """
        Convert v2 collector CSV DataFrame to evidence format.

        Args:
            df: DataFrame from social_posts.csv

        Returns:
            Evidence dictionary compatible with pain analysis
        """
        import pandas as pd

        evidence = {"sources": {}}

        # Separate by platform
        if 'platform' in df.columns:
            for platform in df['platform'].unique():
                platform_df = df[df['platform'] == platform]

                if platform == 'Twitter':
                    evidence['sources']['x'] = {
                        'tweets': platform_df.to_dict('records'),
                        'total_tweets': len(platform_df)
                    }
                elif platform == 'Reddit':
                    evidence['sources']['reddit'] = {
                        'posts': platform_df.to_dict('records'),
                        'total_posts': len(platform_df)
                    }

        # Add Google Trends data if present
        if 'trend_avg' in df.columns:
            avg_trend = df['trend_avg'].mean()
            evidence['sources']['google_trends'] = {
                'trend_direction': f"Avg: {avg_trend:.1f}",
                'interest_level': 'high' if avg_trend > 60 else 'medium' if avg_trend > 30 else 'low'
            }

        return evidence

    def _collect_evidence(
        self,
        keywords: List[str],
        platforms: Optional[List[str]]
    ) -> Dict[str, Any]:
        """Collect evidence from all platforms."""
        if not self.evidence_collector:
            return {"sources": {}, "fallback": True}

        try:
            # Use first keyword as main idea, rest as additional
            main_keyword = keywords[0] if keywords else "business idea"
            additional_keywords = keywords[1:] if len(keywords) > 1 else []

            evidence = self.evidence_collector.collect_all_evidence(
                idea=main_keyword,
                keywords=additional_keywords,
                parallel=True
            )

            return evidence

        except Exception as e:
            logger.error(f"Evidence collection failed: {e}", exc_info=True)
            return {"sources": {}, "error": str(e)}

    def _extract_pain_points(self, evidence: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and categorize pain points from evidence."""
        if not self.pain_extractor:
            return []

        pain_points = []

        # Extract from each source
        sources = evidence.get('sources', {})

        for source_name, source_data in sources.items():
            if isinstance(source_data, dict) and 'error' in source_data:
                continue

            # Get text content from source
            texts = self._extract_text_from_source(source_data)

            for text in texts:
                try:
                    extracted = self.pain_extractor.extract_pain_points(text)
                    if extracted:
                        extracted['source'] = source_name
                        pain_points.append(extracted)
                except Exception as e:
                    logger.warning(f"Pain extraction failed for text: {e}")
                    continue

        return pain_points

    def _extract_text_from_source(self, source_data: Dict[str, Any]) -> List[str]:
        """Extract text content from source data."""
        texts = []

        # V2 format (from message_collector_v2)
        if 'posts' in source_data:
            for post in source_data['posts']:
                if isinstance(post, dict):
                    # V2 format has 'text_excerpt'
                    if 'text_excerpt' in post:
                        texts.append(post['text_excerpt'])
                    # Old format has 'title' and 'selftext'
                    else:
                        texts.append(post.get('title', '') + ' ' + post.get('selftext', ''))
                        for comment in post.get('top_comments', []):
                            if isinstance(comment, dict):
                                texts.append(comment.get('body', ''))

        # Twitter/X tweets
        if 'tweets' in source_data:
            for tweet in source_data['tweets']:
                if isinstance(tweet, dict):
                    # V2 format has 'text_excerpt'
                    if 'text_excerpt' in tweet:
                        texts.append(tweet['text_excerpt'])
                    # Old format has 'text'
                    else:
                        texts.append(tweet.get('text', ''))

        return [t for t in texts if t and len(t) > 10]

    def _analyze_willingness_to_pay(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Extract willingness-to-pay signals."""
        pay_mentions = []
        price_mentions = []

        sources = evidence.get('sources', {})

        for source_name, source_data in sources.items():
            texts = self._extract_text_from_source(source_data)

            for text in texts:
                # Find pricing mentions
                for pattern in self.PRICING_PATTERNS:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    price_mentions.extend(matches)

                # Find willingness-to-pay signals
                for pattern in self.PAY_WILLINGNESS_PATTERNS:
                    if re.search(pattern, text, re.IGNORECASE):
                        # Extract context around the signal
                        context = self._extract_context(text, pattern, window=50)
                        pay_mentions.append({
                            "signal": pattern.replace(r'\s+', ' '),
                            "context": context,
                            "source": source_name
                        })

        # Calculate price range
        price_range = self._calculate_price_range(price_mentions)

        return {
            "mentions_count": len(pay_mentions),
            "price_range": price_range,
            "signals": [m['signal'] for m in pay_mentions[:10]],  # Top 10
            "sample_contexts": [m['context'] for m in pay_mentions[:3]]  # Top 3 examples
        }

    def _analyze_urgency(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze urgency indicators in conversations."""
        urgency_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }

        sources = evidence.get('sources', {})

        for source_name, source_data in sources.items():
            texts = self._extract_text_from_source(source_data)

            for text in texts:
                text_lower = text.lower()

                # Check each urgency level
                for level, keywords in self.URGENCY_KEYWORDS.items():
                    for keyword in keywords:
                        if keyword in text_lower:
                            urgency_counts[level] += 1
                            break  # Count once per text per level

        # Calculate urgency score (0-10)
        urgency_score = (
            urgency_counts['critical'] * 3 +
            urgency_counts['high'] * 2 +
            urgency_counts['medium'] * 1 +
            urgency_counts['low'] * 0.5
        ) / max(sum(urgency_counts.values()), 1)

        return {
            **urgency_counts,
            "urgency_score": min(urgency_score, 10.0),  # Cap at 10
            "total_mentions": sum(urgency_counts.values())
        }

    def _extract_top_quotes(
        self,
        evidence: Dict[str, Any],
        pain_points: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract most impactful pain quotes."""
        quotes = []

        sources = evidence.get('sources', {})

        # Extract from Reddit (prioritize upvoted posts)
        reddit_data = sources.get('reddit', {})
        if 'posts' in reddit_data:
            for post in reddit_data['posts'][:10]:  # Top 10 posts
                if isinstance(post, dict):
                    quote_text = (post.get('title', '') + ' ' + post.get('selftext', ''))[:300]
                    if len(quote_text) > 50:
                        quotes.append({
                            "quote": quote_text,
                            "source": f"r/{post.get('subreddit', 'unknown')}",
                            "metadata": {
                                "upvotes": post.get('score', 0),
                                "author_type": "Reddit user"
                            }
                        })

        # Extract from Twitter/X
        x_data = sources.get('x', {})
        if 'tweets' in x_data:
            for tweet in x_data['tweets'][:5]:
                if isinstance(tweet, dict):
                    quote_text = tweet.get('text', '')[:300]
                    if len(quote_text) > 50:
                        quotes.append({
                            "quote": quote_text,
                            "source": "Twitter/X",
                            "metadata": {
                                "likes": tweet.get('likes', 0),
                                "retweets": tweet.get('retweets', 0)
                            }
                        })

        # Sort by engagement (upvotes, likes, retweets)
        quotes.sort(key=lambda q: q['metadata'].get('upvotes', 0) + q['metadata'].get('likes', 0), reverse=True)

        return quotes

    def _identify_concerns(self, pain_points: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Identify key concerns from pain points."""
        concern_counter = Counter()

        for pain_point in pain_points:
            # Extract concerns from pain point categories
            if isinstance(pain_point, dict):
                pain_text = pain_point.get('pain_text', '')
                if pain_text:
                    # Simple keyword extraction
                    concern_counter[pain_text] += 1

        # Return top concerns
        return [
            {"concern": concern, "count": count}
            for concern, count in concern_counter.most_common(10)
        ]

    def _calculate_demand_signal(
        self,
        evidence: Dict[str, Any],
        pain_points: List[Dict[str, Any]],
        pay_signals: Dict[str, Any],
        urgency: Dict[str, Any]
    ) -> float:
        """
        Calculate demand signal strength (0-10).

        Factors:
        - Conversation volume (30%)
        - Pain point intensity (25%)
        - Willingness to pay (25%)
        - Urgency (20%)
        """
        # Conversation volume score (0-3)
        total_conversations = 0
        sources = evidence.get('sources', {})
        for source_data in sources.values():
            if isinstance(source_data, dict):
                total_conversations += len(source_data.get('posts', []))
                total_conversations += len(source_data.get('tweets', []))

        volume_score = min(total_conversations / 50, 3.0)  # Cap at 3

        # Pain intensity score (0-2.5)
        pain_score = min(len(pain_points) / 20, 2.5)  # Cap at 2.5

        # Pay willingness score (0-2.5)
        pay_score = min(pay_signals.get('mentions_count', 0) / 10, 2.5)  # Cap at 2.5

        # Urgency score (0-2)
        urgency_score = min(urgency.get('urgency_score', 0) / 5, 2.0)  # Cap at 2

        total_signal = volume_score + pain_score + pay_score + urgency_score

        return round(total_signal, 1)

    def _make_validation_decision(
        self,
        demand_signal: float,
        pay_signals: Dict[str, Any],
        urgency: Dict[str, Any],
        concerns: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Make validation decision based on all signals.

        Returns recommendation: PROCEED, REFINE, or STOP
        """
        # Calculate confidence (0-100%)
        confidence = int(demand_signal * 10)  # 0-10 → 0-100

        # Determine recommendation
        if confidence >= 75:
            recommendation = "PROCEED"
            reasoning = "Pain is real and widespread. Strong demand signals across multiple platforms."
        elif confidence >= 50:
            recommendation = "REFINE"
            reasoning = "Moderate signals. Consider refining positioning or target market."
        else:
            recommendation = "STOP"
            reasoning = "Weak demand signals. May need to pivot or reconsider idea."

        # Adjust based on pay signals
        if pay_signals.get('mentions_count', 0) > 20:
            confidence = min(confidence + 10, 100)
            reasoning += " Strong willingness-to-pay indicators."

        # Adjust based on urgency
        if urgency.get('critical', 0) + urgency.get('high', 0) > 10:
            confidence = min(confidence + 5, 100)
            reasoning += " High urgency detected."

        return {
            "confidence": confidence,
            "recommendation": recommendation,
            "reasoning": reasoning
        }

    def _format_conversation_volume(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Format conversation volume for display."""
        sources = evidence.get('sources', {})

        volume = {}

        # Reddit
        reddit_data = sources.get('reddit', {})
        if isinstance(reddit_data, dict) and 'posts' in reddit_data:
            volume['reddit'] = len(reddit_data['posts'])

        # Twitter/X
        x_data = sources.get('x', {})
        if isinstance(x_data, dict) and 'tweets' in x_data:
            volume['twitter'] = len(x_data['tweets'])

        # Google Trends
        trends_data = sources.get('google_trends', {})
        if isinstance(trends_data, dict) and 'trend_direction' in trends_data:
            volume['google_trends'] = trends_data.get('trend_direction', 'unknown')

        return volume

    def _calculate_price_range(self, price_mentions: List[str]) -> str:
        """Calculate price range from mentions."""
        if not price_mentions:
            return "No pricing data"

        # Extract numeric values
        values = []
        for mention in price_mentions:
            # Extract numbers
            numbers = re.findall(r'[\d,]+(?:\.\d{2})?', mention)
            for num_str in numbers:
                try:
                    value = float(num_str.replace(',', ''))
                    values.append(value)
                except ValueError:
                    continue

        if not values:
            return "Unable to determine"

        min_val = int(min(values))
        max_val = int(max(values))

        # Determine currency (heuristic - check first mention)
        currency = "£"  # Default to pounds for UK/Ireland
        if any('$' in m for m in price_mentions):
            currency = "$"
        elif any('€' in m for m in price_mentions):
            currency = "€"

        return f"{currency}{min_val:,}-{currency}{max_val:,}/month"

    def _extract_context(self, text: str, pattern: str, window: int = 50) -> str:
        """Extract context around a regex pattern match."""
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return text[:window]

        start = max(0, match.start() - window)
        end = min(len(text), match.end() + window)

        return "..." + text[start:end] + "..."

    def format_for_display(self, analysis_data: Dict[str, Any]) -> str:
        """
        Format analysis results for console display.

        Args:
            analysis_data: Output from analyze_pain_discovery()

        Returns:
            Formatted string for printing
        """
        lines = []
        lines.append("\n" + "="*70)
        lines.append("🔍 PAIN DISCOVERY RESULTS")
        lines.append("="*70)

        # Demand signal
        signal = analysis_data.get('demand_signal_strength', 0)
        signal_bar = "█" * int(signal) + "░" * (10 - int(signal))
        lines.append(f"\n📊 Demand Signal Strength: {signal_bar} {signal}/10")

        # Conversation volume
        volume = analysis_data.get('conversation_volume', {})
        lines.append(f"\n🔢 Conversation Volume:")
        for platform, count in volume.items():
            lines.append(f"   • {platform.title()}: {count}")

        # Top quotes
        quotes = analysis_data.get('top_pain_quotes', [])
        if quotes:
            lines.append(f"\n💬 Top Pain Quotes:")
            for i, quote_data in enumerate(quotes[:3], 1):
                quote = quote_data.get('quote', '')[:150]
                source = quote_data.get('source', 'Unknown')
                metadata = quote_data.get('metadata', {})
                lines.append(f"\n{i}. \"{quote}...\"")
                lines.append(f"   → {source} | {metadata}")

        # Willingness to pay
        pay_signals = analysis_data.get('willingness_to_pay', {})
        lines.append(f"\n💰 Willingness-to-Pay Signals:")
        lines.append(f"   • Mentions: {pay_signals.get('mentions_count', 0)}")
        lines.append(f"   • Price Range: {pay_signals.get('price_range', 'N/A')}")

        # Concerns
        concerns = analysis_data.get('key_concerns', [])
        if concerns:
            lines.append(f"\n⚠️  Key Concerns Found:")
            for concern in concerns[:3]:
                lines.append(f"   • \"{concern.get('concern', '')}\" ({concern.get('count', 0)} mentions)")

        # Validation decision
        validation = analysis_data.get('validation_decision', {})
        confidence = validation.get('confidence', 0)
        recommendation = validation.get('recommendation', 'UNKNOWN')
        reasoning = validation.get('reasoning', '')

        lines.append(f"\n✅ Validation Decision:")
        lines.append(f"   Confidence Score: {confidence}% - {recommendation}")
        lines.append(f"   {reasoning}")

        lines.append("\n" + "="*70)

        return "\n".join(lines)
