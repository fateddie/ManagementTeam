#!/usr/bin/env python3
"""
Unified Evidence Collector
Aggregates data from Reddit, Google Trends, and X (Twitter) for comprehensive
market validation and pain point discovery.

Features:
- Parallel data collection from all sources
- Unified evidence scoring
- Cross-platform sentiment analysis
- Automated insight generation
- Evidence ranking and prioritization

Usage:
    from src.integrations.evidence_collector import EvidenceCollector

    collector = EvidenceCollector()
    evidence = collector.collect_all_evidence(
        idea="productivity app",
        keywords=["task management", "todo list"]
    )
"""

import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from .reddit_connector import RedditConnector
from .google_trends_connector import GoogleTrendsConnector
from .x_connector import XConnector


class EvidenceCollector:
    """Unified evidence collector from multiple sources"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize evidence collector with all connectors

        Args:
            config_path: Path to configuration file
        """
        print("\n🔧 Initializing Evidence Collector...")

        self.reddit = RedditConnector(config_path)
        self.google_trends = GoogleTrendsConnector()
        self.x_api = XConnector(config_path)

        self.config_path = config_path

    def collect_all_evidence(
        self,
        idea: str,
        keywords: List[str] = None,
        subreddits: List[str] = None,
        parallel: bool = True
    ) -> Dict:
        """
        Collect evidence from all sources

        Args:
            idea: Main idea/topic to research
            keywords: Additional keywords to search
            subreddits: Specific subreddits to search
            parallel: Run collectors in parallel

        Returns:
            Unified evidence report with cross-platform insights
        """
        print(f"\n📊 Collecting Evidence for: '{idea}'")
        print("=" * 70)

        start_time = time.time()

        if keywords is None:
            keywords = [idea]
        else:
            keywords = [idea] + keywords

        if parallel:
            evidence = self._collect_parallel(idea, keywords, subreddits)
        else:
            evidence = self._collect_sequential(idea, keywords, subreddits)

        # Generate unified insights
        evidence['unified_insights'] = self._generate_unified_insights(evidence)
        evidence['evidence_score'] = self._calculate_evidence_score(evidence)
        evidence['collection_time_seconds'] = round(time.time() - start_time, 2)

        print(f"\n✅ Evidence Collection Complete ({evidence['collection_time_seconds']}s)")
        print(f"📈 Evidence Score: {evidence['evidence_score']}/100")

        return evidence

    def _collect_parallel(self, idea: str, keywords: List[str], subreddits: List[str]) -> Dict:
        """Collect evidence in parallel for speed"""
        evidence = {
            "idea": idea,
            "keywords": keywords,
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "sources": {}
        }

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                "reddit": executor.submit(
                    self._collect_reddit_evidence,
                    idea, keywords, subreddits
                ),
                "google_trends": executor.submit(
                    self._collect_trends_evidence,
                    keywords
                ),
                "x": executor.submit(
                    self._collect_x_evidence,
                    idea, keywords
                )
            }

            for source, future in futures.items():
                try:
                    evidence['sources'][source] = future.result(timeout=60)
                    print(f"  ✅ {source.capitalize()} data collected")
                except Exception as e:
                    print(f"  ⚠️  {source.capitalize()} failed: {e}")
                    evidence['sources'][source] = {"error": str(e)}

        return evidence

    def _collect_sequential(self, idea: str, keywords: List[str], subreddits: List[str]) -> Dict:
        """Collect evidence sequentially"""
        evidence = {
            "idea": idea,
            "keywords": keywords,
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "sources": {}
        }

        # Reddit
        try:
            evidence['sources']['reddit'] = self._collect_reddit_evidence(
                idea, keywords, subreddits
            )
            print(f"  ✅ Reddit data collected")
        except Exception as e:
            print(f"  ⚠️  Reddit failed: {e}")
            evidence['sources']['reddit'] = {"error": str(e)}

        # Google Trends
        try:
            evidence['sources']['google_trends'] = self._collect_trends_evidence(keywords)
            print(f"  ✅ Google Trends data collected")
        except Exception as e:
            print(f"  ⚠️  Google Trends failed: {e}")
            evidence['sources']['google_trends'] = {"error": str(e)}

        # X
        try:
            evidence['sources']['x'] = self._collect_x_evidence(idea, keywords)
            print(f"  ✅ X data collected")
        except Exception as e:
            print(f"  ⚠️  X failed: {e}")
            evidence['sources']['x'] = {"error": str(e)}

        return evidence

    def _collect_reddit_evidence(
        self,
        idea: str,
        keywords: List[str],
        subreddits: Optional[List[str]]
    ) -> Dict:
        """Collect evidence from Reddit"""
        results = self.reddit.search_pain_points(
            query=idea,
            subreddits=subreddits,
            time_filter="month",
            limit=100
        )

        return {
            "total_posts": results.get("total_posts", 0),
            "pain_points": results.get("pain_points", []),
            "sentiment": results.get("sentiment_summary", {}),
            "top_posts": results.get("posts", [])[:5]
        }

    def _collect_trends_evidence(self, keywords: List[str]) -> Dict:
        """Collect evidence from Google Trends"""
        # Analyze primary keyword
        primary = keywords[0] if keywords else ""
        results = self.google_trends.analyze_interest(
            keyword=primary,
            timeframe="today 12-m"
        )

        # Compare if multiple keywords
        comparison = None
        if len(keywords) > 1:
            comparison = self.google_trends.compare_keywords(
                keywords=keywords[:5],  # Max 5
                timeframe="today 12-m"
            )

        return {
            "primary_keyword": primary,
            "interest_summary": results.get("interest_over_time", {}).get("summary", {}),
            "insights": results.get("insights", {}),
            "related_queries": results.get("related_queries", {}),
            "comparison": comparison
        }

    def _collect_x_evidence(self, idea: str, keywords: List[str]) -> Dict:
        """Collect evidence from X (Twitter)"""
        results = self.x_api.search_sentiment(
            query=idea,
            limit=100
        )

        return {
            "total_tweets": results.get("total_tweets", 0),
            "sentiment": results.get("sentiment_summary", {}),
            "insights": results.get("insights", {}),
            "top_tweets": results.get("top_influential_tweets", [])[:5]
        }

    def _generate_unified_insights(self, evidence: Dict) -> Dict:
        """Generate unified insights across all sources"""
        sources = evidence.get("sources", {})

        # Aggregate sentiment
        sentiments = []
        if "reddit" in sources and "sentiment" in sources["reddit"]:
            sentiments.append(("reddit", sources["reddit"]["sentiment"].get("avg_polarity", 0)))
        if "x" in sources and "sentiment" in sources["x"]:
            sentiments.append(("x", sources["x"]["sentiment"].get("avg_polarity", 0)))

        avg_sentiment = sum(s[1] for s in sentiments) / len(sentiments) if sentiments else 0

        # Aggregate market signals
        market_signals = []

        # Reddit signal
        if "reddit" in sources:
            reddit_posts = sources["reddit"].get("total_posts", 0)
            reddit_signal = "strong" if reddit_posts > 50 else "moderate" if reddit_posts > 20 else "weak"
            market_signals.append(("reddit", reddit_signal))

        # Google Trends signal
        if "google_trends" in sources:
            trends_insights = sources["google_trends"].get("insights", {})
            trends_signal = trends_insights.get("interest_level", "low")
            market_signals.append(("google_trends", trends_signal))

        # X signal
        if "x" in sources:
            x_insights = sources["x"].get("insights", {})
            x_signal = x_insights.get("social_proof", "weak")
            market_signals.append(("x", x_signal))

        # Aggregate pain points
        pain_count = 0
        if "reddit" in sources:
            pain_count = len(sources["reddit"].get("pain_points", []))

        insights = {
            "overall_sentiment": {
                "score": round(avg_sentiment, 2),
                "label": "negative" if avg_sentiment < -0.1 else "neutral" if avg_sentiment < 0.1 else "positive",
                "sources": len(sentiments)
            },
            "market_validation": {
                "signals": market_signals,
                "strength": self._calculate_market_strength(market_signals)
            },
            "pain_points_discovered": pain_count,
            "data_sources": len([s for s in sources.values() if "error" not in s]),
            "recommendation": self._generate_recommendation(avg_sentiment, market_signals, pain_count)
        }

        return insights

    def _calculate_market_strength(self, signals: List[tuple]) -> str:
        """Calculate overall market strength from signals"""
        if not signals:
            return "unknown"

        strength_map = {"weak": 1, "low": 1, "moderate": 2, "medium": 2, "strong": 3, "high": 3}
        scores = [strength_map.get(signal[1], 1) for signal in signals]
        avg_score = sum(scores) / len(scores)

        if avg_score >= 2.5:
            return "strong"
        elif avg_score >= 1.5:
            return "moderate"
        else:
            return "weak"

    def _calculate_evidence_score(self, evidence: Dict) -> int:
        """Calculate overall evidence score (0-100)"""
        score = 0
        sources = evidence.get("sources", {})

        # Reddit contribution (40 points)
        if "reddit" in sources and "error" not in sources["reddit"]:
            reddit = sources["reddit"]
            posts = min(reddit.get("total_posts", 0), 100)
            pain_points = min(len(reddit.get("pain_points", [])), 20)
            score += (posts / 100) * 25  # 25 points for post volume
            score += (pain_points / 20) * 15  # 15 points for pain points

        # Google Trends contribution (30 points)
        if "google_trends" in sources and "error" not in sources["google_trends"]:
            trends = sources["google_trends"]
            interest = trends.get("interest_summary", {}).get("avg", 0)
            score += (interest / 100) * 30

        # X contribution (30 points)
        if "x" in sources and "error" not in sources["x"]:
            x_data = sources["x"]
            tweets = min(x_data.get("total_tweets", 0), 100)
            sentiment = x_data.get("sentiment", {}).get("avg_polarity", 0)
            score += (tweets / 100) * 20  # 20 points for tweet volume
            score += ((sentiment + 1) / 2) * 10  # 10 points for sentiment

        return min(int(score), 100)

    def _generate_recommendation(
        self,
        avg_sentiment: float,
        market_signals: List[tuple],
        pain_count: int
    ) -> str:
        """Generate overall recommendation"""
        strength = self._calculate_market_strength(market_signals)

        if strength == "strong" and pain_count > 10:
            return "✅ STRONG GO - Clear market demand with validated pain points"
        elif strength == "strong" and avg_sentiment > 0:
            return "✅ GO - Strong positive market signals"
        elif strength == "moderate" and pain_count > 5:
            return "🟡 CONDITIONAL GO - Moderate signals, validate pain points further"
        elif strength == "weak" or pain_count < 3:
            return "⚠️ CAUTION - Weak market signals, significant validation needed"
        elif avg_sentiment < -0.2:
            return "❌ NO GO - Negative sentiment dominates, pivot recommended"
        else:
            return "🟡 CONDITIONAL - Mixed signals, deeper analysis required"

    def save_evidence_report(self, evidence: Dict, output_path: str):
        """Save evidence report to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(evidence, f, indent=2)

        print(f"\n💾 Evidence report saved to: {output_file}")

        # Also save a markdown summary
        md_file = output_file.with_suffix('.md')
        self._save_markdown_summary(evidence, md_file)
        print(f"📄 Markdown summary saved to: {md_file}")

    def _save_markdown_summary(self, evidence: Dict, md_file: Path):
        """Save a human-readable markdown summary"""
        unified = evidence.get('unified_insights', {})

        md = f"""# Evidence Collection Report

**Idea:** {evidence['idea']}
**Collected:** {evidence['collected_at']}
**Evidence Score:** {evidence.get('evidence_score', 0)}/100

---

## Overall Assessment

**Recommendation:** {unified.get('recommendation', 'N/A')}

### Market Validation

**Overall Sentiment:** {unified.get('overall_sentiment', {}).get('label', 'N/A')} ({unified.get('overall_sentiment', {}).get('score', 0)})

**Market Strength:** {unified.get('market_validation', {}).get('strength', 'N/A')}

**Pain Points Discovered:** {unified.get('pain_points_discovered', 0)}

---

## Data Sources

"""

        sources = evidence.get('sources', {})

        # Reddit section
        if 'reddit' in sources and 'error' not in sources['reddit']:
            reddit = sources['reddit']
            md += f"""### Reddit
- **Posts Analyzed:** {reddit.get('total_posts', 0)}
- **Pain Points:** {len(reddit.get('pain_points', []))}
- **Top Pain Keywords:** {', '.join([p['keyword'] for p in reddit.get('pain_points', [])[:5]])}

"""

        # Google Trends section
        if 'google_trends' in sources and 'error' not in sources['google_trends']:
            trends = sources['google_trends']
            interest = trends.get('interest_summary', {})
            md += f"""### Google Trends
- **Primary Keyword:** {trends.get('primary_keyword', 'N/A')}
- **Average Interest:** {interest.get('avg', 0)}
- **Trend:** {interest.get('trend', 'N/A')}
- **Market Size:** {trends.get('insights', {}).get('market_size_indicator', 'N/A')}

"""

        # X section
        if 'x' in sources and 'error' not in sources['x']:
            x_data = sources['x']
            md += f"""### X (Twitter)
- **Tweets Analyzed:** {x_data.get('total_tweets', 0)}
- **Sentiment:** {x_data.get('sentiment', {}).get('sentiment_label', 'N/A')}
- **Social Proof:** {x_data.get('insights', {}).get('social_proof', 'N/A')}

"""

        md += f"""---

**Report generated by Evidence Collector v1.0**
"""

        with open(md_file, 'w') as f:
            f.write(md)


if __name__ == "__main__":
    # Test the collector
    collector = EvidenceCollector()

    evidence = collector.collect_all_evidence(
        idea="productivity app for developers",
        keywords=["task management", "code tracking"],
        subreddits=["programming", "productivity"]
    )

    print(f"\n📊 Final Evidence Score: {evidence['evidence_score']}/100")
    print(f"💡 Recommendation: {evidence['unified_insights']['recommendation']}")

    # Save report
    collector.save_evidence_report(evidence, "outputs/evidence/test_report.json")
