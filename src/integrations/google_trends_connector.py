#!/usr/bin/env python3
"""
Google Trends API Connector
Analyzes search trends and market interest for idea validation.

Features:
- Track search interest over time
- Compare multiple keywords
- Geographic interest analysis
- Related queries and topics
- Rising vs declining trends

Usage:
    from src.integrations.google_trends_connector import GoogleTrendsConnector

    trends = GoogleTrendsConnector()
    results = trends.analyze_interest("productivity app", timeframe="today 12-m")
"""

import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("⚠️  Warning: pytrends not installed. Install with: pip install pytrends")


class GoogleTrendsConnector:
    """Connect to Google Trends for market interest analysis"""

    def __init__(self):
        """Initialize Google Trends connector"""
        self.pytrends = None
        self.cache = {}

        if PYTRENDS_AVAILABLE:
            self._init_trends_client()
        else:
            print("⚠️  Google Trends not configured. Using mock mode.")

    def _init_trends_client(self):
        """Initialize pytrends client"""
        try:
            self.pytrends = TrendReq(hl='en-US', tz=360)
            print("✅ Google Trends API connected")
        except Exception as e:
            print(f"❌ Failed to connect to Google Trends: {e}")
            self.pytrends = None

    def analyze_interest(
        self,
        keyword: str,
        timeframe: str = "today 12-m",
        geo: str = ""
    ) -> Dict:
        """
        Analyze search interest for a keyword

        Args:
            keyword: Search keyword to analyze
            timeframe: Time period (today 12-m, today 3-m, today 5-y, all)
            geo: Geographic location (empty = worldwide, US, GB, etc.)

        Returns:
            Dict with interest over time, related queries, and insights
        """
        if not self.pytrends:
            return self._mock_interest_results(keyword)

        print(f"\n📊 Analyzing Google Trends for: '{keyword}'")

        try:
            # Build payload
            self.pytrends.build_payload(
                [keyword],
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )

            # Get interest over time
            interest_over_time = self.pytrends.interest_over_time()

            # Get related queries
            related_queries = self.pytrends.related_queries()

            # Get interest by region
            interest_by_region = self.pytrends.interest_by_region(
                resolution='COUNTRY',
                inc_low_vol=True,
                inc_geo_code=False
            )

            # Process results
            results = {
                "keyword": keyword,
                "timeframe": timeframe,
                "geo": geo or "worldwide",
                "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "interest_over_time": self._process_interest_over_time(interest_over_time, keyword),
                "related_queries": self._process_related_queries(related_queries, keyword),
                "interest_by_region": self._process_interest_by_region(interest_by_region, keyword),
                "insights": self._generate_insights(interest_over_time, keyword)
            }

            print(f"✅ Analysis complete")
            return results

        except Exception as e:
            print(f"❌ Error analyzing trends: {e}")
            return self._mock_interest_results(keyword)

    def _process_interest_over_time(self, df, keyword: str) -> Dict:
        """Process interest over time data"""
        if df is None or df.empty:
            return {"data": [], "summary": {}}

        # Convert to list of dicts
        data = []
        for index, row in df.iterrows():
            data.append({
                "date": index.strftime("%Y-%m-%d"),
                "value": int(row[keyword]) if keyword in row else 0
            })

        # Calculate summary statistics
        values = [d["value"] for d in data]
        summary = {
            "avg": round(sum(values) / len(values), 1) if values else 0,
            "max": max(values) if values else 0,
            "min": min(values) if values else 0,
            "current": values[-1] if values else 0,
            "trend": self._calculate_trend(values)
        }

        return {
            "data": data,
            "summary": summary
        }

    def _calculate_trend(self, values: List[int]) -> str:
        """Calculate overall trend direction"""
        if len(values) < 2:
            return "stable"

        # Compare first half to second half
        mid = len(values) // 2
        first_half_avg = sum(values[:mid]) / mid
        second_half_avg = sum(values[mid:]) / (len(values) - mid)

        if second_half_avg > first_half_avg * 1.1:
            return "rising"
        elif second_half_avg < first_half_avg * 0.9:
            return "declining"
        else:
            return "stable"

    def _process_related_queries(self, related_queries: Dict, keyword: str) -> Dict:
        """Process related queries data"""
        if not related_queries or keyword not in related_queries:
            return {"top": [], "rising": []}

        result = {"top": [], "rising": []}

        # Top queries
        if "top" in related_queries[keyword] and related_queries[keyword]["top"] is not None:
            top_df = related_queries[keyword]["top"]
            result["top"] = [
                {"query": row["query"], "value": int(row["value"])}
                for _, row in top_df.head(10).iterrows()
            ]

        # Rising queries
        if "rising" in related_queries[keyword] and related_queries[keyword]["rising"] is not None:
            rising_df = related_queries[keyword]["rising"]
            result["rising"] = [
                {"query": row["query"], "value": str(row["value"])}
                for _, row in rising_df.head(10).iterrows()
            ]

        return result

    def _process_interest_by_region(self, df, keyword: str) -> List[Dict]:
        """Process interest by region data"""
        if df is None or df.empty:
            return []

        # Get top 20 regions
        regions = []
        for index, row in df.nlargest(20, keyword).iterrows():
            regions.append({
                "region": index,
                "value": int(row[keyword]) if keyword in row else 0
            })

        return regions

    def _generate_insights(self, interest_over_time, keyword: str) -> Dict:
        """Generate insights from the data"""
        if interest_over_time is None or interest_over_time.empty:
            return {}

        values = interest_over_time[keyword].tolist() if keyword in interest_over_time else []

        if not values:
            return {}

        avg_interest = sum(values) / len(values)
        current_interest = values[-1]
        trend = self._calculate_trend(values)

        insights = {
            "market_size_indicator": "large" if avg_interest > 50 else "medium" if avg_interest > 20 else "small",
            "interest_level": "high" if current_interest > 70 else "medium" if current_interest > 30 else "low",
            "trend_direction": trend,
            "recommendation": ""
        }

        # Generate recommendation
        if trend == "rising" and current_interest > 50:
            insights["recommendation"] = "Strong market signal - growing interest"
        elif trend == "declining" and current_interest < 30:
            insights["recommendation"] = "Weak market signal - declining interest"
        elif trend == "stable" and current_interest > 50:
            insights["recommendation"] = "Stable market - consistent interest"
        else:
            insights["recommendation"] = "Moderate market signal - requires validation"

        return insights

    def compare_keywords(
        self,
        keywords: List[str],
        timeframe: str = "today 12-m",
        geo: str = ""
    ) -> Dict:
        """
        Compare search interest for multiple keywords

        Args:
            keywords: List of keywords to compare (max 5)
            timeframe: Time period
            geo: Geographic location

        Returns:
            Dict with comparative analysis
        """
        if not self.pytrends:
            return self._mock_comparison_results(keywords)

        if len(keywords) > 5:
            print("⚠️  Limiting to first 5 keywords")
            keywords = keywords[:5]

        print(f"\n🔄 Comparing keywords: {', '.join(keywords)}")

        try:
            # Build payload
            self.pytrends.build_payload(
                keywords,
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )

            # Get interest over time
            interest_over_time = self.pytrends.interest_over_time()

            # Process comparison
            comparison = {}
            for keyword in keywords:
                if keyword in interest_over_time:
                    values = interest_over_time[keyword].tolist()
                    comparison[keyword] = {
                        "avg_interest": round(sum(values) / len(values), 1),
                        "max_interest": max(values),
                        "current_interest": values[-1],
                        "trend": self._calculate_trend(values)
                    }

            # Rank keywords
            ranked = sorted(
                comparison.items(),
                key=lambda x: x[1]["avg_interest"],
                reverse=True
            )

            results = {
                "keywords": keywords,
                "timeframe": timeframe,
                "geo": geo or "worldwide",
                "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "comparison": comparison,
                "ranked": [{"keyword": k, **v} for k, v in ranked],
                "winner": ranked[0][0] if ranked else None
            }

            print(f"✅ Comparison complete - Winner: {results['winner']}")
            return results

        except Exception as e:
            print(f"❌ Error comparing keywords: {e}")
            return self._mock_comparison_results(keywords)

    def _mock_interest_results(self, keyword: str) -> Dict:
        """Return mock results when API is not configured"""
        return {
            "keyword": keyword,
            "timeframe": "today 12-m",
            "geo": "worldwide",
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "interest_over_time": {
                "data": [],
                "summary": {"avg": 0, "max": 0, "min": 0, "current": 0, "trend": "stable"}
            },
            "related_queries": {"top": [], "rising": []},
            "interest_by_region": [],
            "insights": {},
            "note": "Mock data - Google Trends not configured"
        }

    def _mock_comparison_results(self, keywords: List[str]) -> Dict:
        """Return mock comparison results"""
        return {
            "keywords": keywords,
            "timeframe": "today 12-m",
            "geo": "worldwide",
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "comparison": {},
            "ranked": [],
            "winner": None,
            "note": "Mock data - Google Trends not configured"
        }


if __name__ == "__main__":
    # Test the connector
    trends = GoogleTrendsConnector()

    # Single keyword analysis
    results = trends.analyze_interest("productivity app", timeframe="today 12-m")

    print(f"\n📊 Results for '{results['keyword']}':")
    if results.get("interest_over_time"):
        summary = results["interest_over_time"]["summary"]
        print(f"  Average interest: {summary['avg']}")
        print(f"  Current interest: {summary['current']}")
        print(f"  Trend: {summary['trend']}")

    if results.get("insights"):
        print(f"\n💡 Insights:")
        print(f"  Market size: {results['insights'].get('market_size_indicator')}")
        print(f"  Interest level: {results['insights'].get('interest_level')}")
        print(f"  Recommendation: {results['insights'].get('recommendation')}")

    # Compare multiple keywords
    comparison = trends.compare_keywords([
        "productivity app",
        "task manager",
        "todo list"
    ])

    if comparison.get("winner"):
        print(f"\n🏆 Winner: {comparison['winner']}")
