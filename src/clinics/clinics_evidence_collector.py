#!/usr/bin/env python3
"""
Clinics Evidence Collector
Extends the base EvidenceCollector to include clinic-specific data sources:
Google Reviews and industry publications.

Features:
- Inherits Reddit, Google Trends, X (Twitter) collection
- Adds Google Reviews from individual clinics
- Adds industry publication analysis
- Cross-validates clinic feedback with social data
- Unified pain point analysis across all sources

Usage:
    from src.clinics.clinics_evidence_collector import ClinicsEvidenceCollector

    collector = ClinicsEvidenceCollector()
    evidence = collector.collect_clinic_evidence(
        clinic_name="London Physiotherapy Clinic",
        clinic_type="physiotherapy"
    )
"""

import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import base class
import sys
sys.path.append(str(Path(__file__).parent.parent))
from integrations.evidence_collector import EvidenceCollector

# Import new connectors
from integrations.google_reviews_connector import GoogleReviewsConnector
from integrations.publication_connector import PublicationConnector


class ClinicsEvidenceCollector(EvidenceCollector):
    """
    Extended evidence collector for clinic-specific research

    Inherits:
        - Reddit, Google Trends, X collection (from EvidenceCollector)

    Adds:
        - Google Reviews collection
        - Industry publications analysis
        - Cross-validation of clinic + social data
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize clinics evidence collector

        Args:
            config_path: Path to configuration file
        """
        # Initialize parent (Reddit, Trends, X)
        super().__init__(config_path)

        # Add clinic-specific connectors
        self.google_reviews = GoogleReviewsConnector(config_path)
        self.publications = PublicationConnector(config_path)

        print("✅ Clinics Evidence Collector initialized (5 sources: Reddit, X, Trends, Reviews, Publications)")

    def collect_clinic_evidence(
        self,
        clinic_name: str,
        clinic_type: str,
        location: str = "UK",
        include_social: bool = True,
        parallel: bool = True
    ) -> Dict:
        """
        Collect comprehensive evidence about a clinic

        Args:
            clinic_name: Name of the clinic
            clinic_type: Type (physiotherapy, counselling, chiropody)
            location: Location filter
            include_social: Include social media validation (Reddit, X)
            parallel: Run collectors in parallel

        Returns:
            Unified evidence report with clinic + social insights
        """
        print(f"\n📊 Collecting Clinic Evidence")
        print(f"🏥 Clinic: {clinic_name}")
        print(f"📍 Type: {clinic_type}")
        print("=" * 70)

        start_time = time.time()

        if parallel:
            evidence = self._collect_parallel_clinic(
                clinic_name, clinic_type, location, include_social
            )
        else:
            evidence = self._collect_sequential_clinic(
                clinic_name, clinic_type, location, include_social
            )

        # Generate unified insights (extends base method)
        evidence['unified_insights'] = self._generate_clinic_insights(evidence)
        evidence['evidence_score'] = self._calculate_clinic_evidence_score(evidence)
        evidence['collection_time_seconds'] = round(time.time() - start_time, 2)

        print(f"\n✅ Clinic Evidence Collection Complete ({evidence['collection_time_seconds']}s)")
        print(f"📈 Evidence Score: {evidence['evidence_score']}/100")

        return evidence

    def _collect_parallel_clinic(
        self,
        clinic_name: str,
        clinic_type: str,
        location: str,
        include_social: bool
    ) -> Dict:
        """Collect clinic evidence in parallel for speed"""
        evidence = {
            "clinic_name": clinic_name,
            "clinic_type": clinic_type,
            "location": location,
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "sources": {}
        }

        # Build futures dict
        futures_dict = {}

        with ThreadPoolExecutor(max_workers=5) as executor:
            # Always collect clinic-specific sources
            futures_dict["google_reviews"] = executor.submit(
                self._collect_google_reviews_evidence,
                clinic_name, location
            )

            futures_dict["publications"] = executor.submit(
                self._collect_publications_evidence,
                clinic_type
            )

            # Optionally include social validation
            if include_social:
                # Search Reddit for clinic type problems
                futures_dict["reddit"] = executor.submit(
                    self._collect_reddit_evidence,
                    f"{clinic_type} UK problems",
                    keywords=[clinic_type, "pain points", "issues"],
                    subreddits=self._get_subreddits_for_type(clinic_type)
                )

                # Search X for clinic mentions
                futures_dict["x"] = executor.submit(
                    self._collect_x_evidence,
                    clinic_name,
                    keywords=[clinic_type, location]
                )

                # Google Trends for clinic type
                futures_dict["google_trends"] = executor.submit(
                    self._collect_trends_evidence,
                    keywords=[clinic_type, f"{clinic_type} {location}"]
                )

            # Collect results
            for source, future in futures_dict.items():
                try:
                    evidence['sources'][source] = future.result(timeout=120)
                    print(f"  ✅ {source.capitalize().replace('_', ' ')} data collected")
                except Exception as e:
                    print(f"  ⚠️  {source.capitalize()} failed: {e}")
                    evidence['sources'][source] = {"error": str(e)}

        return evidence

    def _collect_sequential_clinic(
        self,
        clinic_name: str,
        clinic_type: str,
        location: str,
        include_social: bool
    ) -> Dict:
        """Collect clinic evidence sequentially"""
        evidence = {
            "clinic_name": clinic_name,
            "clinic_type": clinic_type,
            "location": location,
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "sources": {}
        }

        # Google Reviews
        try:
            evidence['sources']['google_reviews'] = self._collect_google_reviews_evidence(
                clinic_name, location
            )
            print(f"  ✅ Google Reviews data collected")
        except Exception as e:
            print(f"  ⚠️  Google Reviews failed: {e}")
            evidence['sources']['google_reviews'] = {"error": str(e)}

        # Publications
        try:
            evidence['sources']['publications'] = self._collect_publications_evidence(
                clinic_type
            )
            print(f"  ✅ Publications data collected")
        except Exception as e:
            print(f"  ⚠️  Publications failed: {e}")
            evidence['sources']['publications'] = {"error": str(e)}

        # Social validation (optional)
        if include_social:
            # Reddit
            try:
                evidence['sources']['reddit'] = self._collect_reddit_evidence(
                    idea=f"{clinic_type} UK problems",
                    keywords=[clinic_type, "pain points"],
                    subreddits=self._get_subreddits_for_type(clinic_type)
                )
                print(f"  ✅ Reddit data collected")
            except Exception as e:
                print(f"  ⚠️  Reddit failed: {e}")
                evidence['sources']['reddit'] = {"error": str(e)}

            # X
            try:
                evidence['sources']['x'] = self._collect_x_evidence(
                    clinic_name,
                    keywords=[clinic_type, location]
                )
                print(f"  ✅ X data collected")
            except Exception as e:
                print(f"  ⚠️  X failed: {e}")
                evidence['sources']['x'] = {"error": str(e)}

            # Google Trends
            try:
                evidence['sources']['google_trends'] = self._collect_trends_evidence(
                    keywords=[clinic_type, f"{clinic_type} {location}"]
                )
                print(f"  ✅ Google Trends data collected")
            except Exception as e:
                print(f"  ⚠️  Google Trends failed: {e}")
                evidence['sources']['google_trends'] = {"error": str(e)}

        return evidence

    def _collect_google_reviews_evidence(
        self,
        clinic_name: str,
        location: str
    ) -> Dict:
        """Collect evidence from Google Reviews"""
        results = self.google_reviews.get_reviews(
            business_name=clinic_name,
            location=location,
            limit=20
        )

        return {
            "business_info": results.get("business_info", {}),
            "total_reviews": results.get("total_reviews_collected", 0),
            "pain_points": results.get("pain_points", []),
            "sentiment": results.get("sentiment_summary", {}),
            "top_reviews": results.get("reviews", [])[:5],
            "_audit_trail": results.get("_audit_trail", {})
        }

    def _collect_publications_evidence(self, clinic_type: str) -> Dict:
        """Collect evidence from industry publications"""
        # Map clinic types to publication types
        publication_map = {
            "physiotherapy": "physio_first",
            "counselling": "bacp",
            "chiropody": "rcpod"
        }

        publication = publication_map.get(clinic_type.lower(), "all")

        results = self.publications.get_recent_articles(
            publication=publication,
            limit=10,
            days_back=90
        )

        return {
            "total_articles": results.get("total_articles_collected", 0),
            "pain_points": results.get("pain_points", []),
            "trends": results.get("trend_summary", {}),
            "top_articles": results.get("articles", [])[:5]
        }

    def _get_subreddits_for_type(self, clinic_type: str) -> List[str]:
        """Get relevant subreddits for clinic type"""
        subreddit_map = {
            "physiotherapy": ["physiotherapy", "UKPhysiotherapy", "physicaltherapy", "AskDocs"],
            "counselling": ["therapists", "psychotherapy", "mentalhealth", "AskTherapists"],
            "chiropody": ["Podiatry", "foothealth", "AskDocs"]
        }

        return subreddit_map.get(clinic_type.lower(), ["AskDocs", "UnitedKingdom"])

    def _generate_clinic_insights(self, evidence: Dict) -> Dict:
        """
        Generate unified insights for clinic evidence

        Extends base method to include clinic-specific analysis
        """
        sources = evidence.get("sources", {})

        # Get base insights (Reddit, X, Trends)
        base_insights = super()._generate_unified_insights(evidence)

        # Add clinic-specific insights

        # 1. Cross-validated pain points (appear in BOTH clinic + social)
        clinic_pain_points = []
        social_pain_points = []

        if "google_reviews" in sources:
            clinic_pain_points = [
                p["keyword"] for p in sources["google_reviews"].get("pain_points", [])
            ]

        if "reddit" in sources:
            social_pain_points = [
                p["keyword"] for p in sources["reddit"].get("pain_points", [])
            ]

        cross_validated = list(set(clinic_pain_points) & set(social_pain_points))

        # 2. Publication trends
        publication_trends = []
        if "publications" in sources:
            publication_trends = sources["publications"].get("trends", {}).get("trending_topics", [])

        # 3. Review sentiment vs social sentiment comparison
        review_sentiment = None
        if "google_reviews" in sources:
            review_sentiment = sources["google_reviews"].get("sentiment", {}).get("avg_rating")

        # Combine insights
        clinic_insights = {
            **base_insights,  # Include base insights
            "clinic_specific": {
                "total_reviews_analyzed": sources.get("google_reviews", {}).get("total_reviews", 0),
                "clinic_pain_points": len(clinic_pain_points),
                "social_pain_points": len(social_pain_points),
                "cross_validated_pain_points": {
                    "count": len(cross_validated),
                    "keywords": cross_validated,
                    "confidence": "high" if len(cross_validated) >= 3 else "medium" if len(cross_validated) >= 1 else "low"
                },
                "publication_trends": publication_trends[:5],
                "review_sentiment": {
                    "avg_rating": review_sentiment,
                    "comparison": self._compare_sentiments(
                        review_sentiment,
                        base_insights.get("overall_sentiment", {}).get("score")
                    )
                }
            },
            "recommendation": self._generate_clinic_recommendation(
                clinic_pain_points,
                social_pain_points,
                cross_validated,
                review_sentiment
            )
        }

        return clinic_insights

    def _compare_sentiments(
        self,
        review_rating: Optional[float],
        social_polarity: Optional[float]
    ) -> str:
        """Compare review sentiment vs social sentiment"""
        if review_rating is None or social_polarity is None:
            return "insufficient_data"

        # Convert rating (1-5) to polarity (-1 to 1)
        # 5 stars = 1.0, 3 stars = 0, 1 star = -1.0
        review_polarity = (review_rating - 3) / 2

        diff = abs(review_polarity - social_polarity)

        if diff < 0.2:
            return "aligned"  # Clinic reviews match social sentiment
        elif review_polarity > social_polarity:
            return "reviews_more_positive"  # Clinic better than social perception
        else:
            return "social_more_positive"  # Social perception better than clinic

    def _generate_clinic_recommendation(
        self,
        clinic_pains: List[str],
        social_pains: List[str],
        cross_validated: List[str],
        review_rating: Optional[float]
    ) -> str:
        """Generate recommendation for clinic pain point analysis"""

        # High confidence: Multiple cross-validated pain points
        if len(cross_validated) >= 3:
            return "✅ HIGH CONFIDENCE - Multiple pain points validated across clinic + social data"

        # Medium confidence: Some cross-validation or strong clinic signal
        elif len(cross_validated) >= 1 or len(clinic_pains) >= 5:
            return "🟡 MEDIUM CONFIDENCE - Pain points identified, recommend more data for validation"

        # Low rating indicates problems
        elif review_rating and review_rating < 3.0:
            return "⚠️ CAUTION - Low clinic ratings indicate issues, but pain points unclear"

        # Insufficient data
        elif len(clinic_pains) == 0 and len(social_pains) == 0:
            return "❌ INSUFFICIENT DATA - Collect more reviews and social data"

        else:
            return "🟡 CONDITIONAL - Mixed signals, deeper analysis required"

    def _calculate_clinic_evidence_score(self, evidence: Dict) -> int:
        """
        Calculate overall evidence score for clinic research (0-100)

        Scoring:
        - Google Reviews: 40 points
        - Publications: 20 points
        - Reddit: 20 points
        - X: 10 points
        - Google Trends: 10 points
        """
        score = 0
        sources = evidence.get("sources", {})

        # Google Reviews (40 points)
        if "google_reviews" in sources and "error" not in sources["google_reviews"]:
            reviews = sources["google_reviews"]
            total_reviews = min(reviews.get("total_reviews", 0), 20)
            pain_points = min(len(reviews.get("pain_points", [])), 10)
            score += (total_reviews / 20) * 25  # 25 points for review volume
            score += (pain_points / 10) * 15  # 15 points for pain points

        # Publications (20 points)
        if "publications" in sources and "error" not in sources["publications"]:
            pubs = sources["publications"]
            articles = min(pubs.get("total_articles", 0), 10)
            trends = len(pubs.get("trends", {}).get("trending_topics", []))
            score += (articles / 10) * 15  # 15 points for article volume
            score += min(trends, 5)  # 5 points for trends

        # Reddit (20 points)
        if "reddit" in sources and "error" not in sources["reddit"]:
            reddit = sources["reddit"]
            posts = min(reddit.get("total_posts", 0), 50)
            pain_points = min(len(reddit.get("pain_points", [])), 10)
            score += (posts / 50) * 10  # 10 points for post volume
            score += (pain_points / 10) * 10  # 10 points for pain points

        # X (10 points)
        if "x" in sources and "error" not in sources["x"]:
            x_data = sources["x"]
            tweets = min(x_data.get("total_tweets", 0), 50)
            score += (tweets / 50) * 10

        # Google Trends (10 points)
        if "google_trends" in sources and "error" not in sources["google_trends"]:
            trends = sources["google_trends"]
            interest = trends.get("interest_summary", {}).get("avg", 0)
            score += (interest / 100) * 10

        return min(int(score), 100)

    def collect_clinic_type_evidence(
        self,
        clinic_type: str,
        location: str = "UK",
        sample_size: int = 10,
        parallel: bool = True
    ) -> Dict:
        """
        Collect aggregated evidence across multiple clinics of same type

        Args:
            clinic_type: Type of clinic (physiotherapy, counselling, chiropody)
            location: Location filter
            sample_size: Number of clinics to sample
            parallel: Run in parallel

        Returns:
            Aggregated evidence report across clinic type
        """
        print(f"\n📊 Collecting Evidence for Clinic Type: {clinic_type}")
        print(f"📍 Location: {location}")
        print(f"🔢 Sample Size: {sample_size}")
        print("=" * 70)

        # For now, collect publications + social data
        # In Stage 2, could add automated clinic discovery + sampling

        evidence = {
            "clinic_type": clinic_type,
            "location": location,
            "sample_size": sample_size,
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "sources": {}
        }

        # Collect industry-wide evidence
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                "publications": executor.submit(
                    self._collect_publications_evidence,
                    clinic_type
                ),
                "reddit": executor.submit(
                    self._collect_reddit_evidence,
                    f"{clinic_type} UK problems",
                    [clinic_type, "pain points"],
                    self._get_subreddits_for_type(clinic_type)
                ),
                "x": executor.submit(
                    self._collect_x_evidence,
                    f"{clinic_type} {location}",
                    [clinic_type, "clinic"]
                ),
                "google_trends": executor.submit(
                    self._collect_trends_evidence,
                    [clinic_type, f"{clinic_type} {location}"]
                )
            }

            for source, future in futures.items():
                try:
                    evidence['sources'][source] = future.result(timeout=120)
                    print(f"  ✅ {source.capitalize()} data collected")
                except Exception as e:
                    print(f"  ⚠️  {source.capitalize()} failed: {e}")
                    evidence['sources'][source] = {"error": str(e)}

        # Generate insights
        evidence['unified_insights'] = self._generate_type_insights(evidence)
        evidence['evidence_score'] = self._calculate_clinic_evidence_score(evidence)

        print(f"\n✅ Clinic Type Evidence Collection Complete")
        print(f"📈 Evidence Score: {evidence['evidence_score']}/100")

        return evidence

    def _generate_type_insights(self, evidence: Dict) -> Dict:
        """Generate insights for clinic type (industry-wide)"""
        sources = evidence.get("sources", {})

        # Aggregate pain points across all sources
        all_pain_points = []

        for source in ["publications", "reddit", "x"]:
            if source in sources and "pain_points" in sources[source]:
                all_pain_points.extend(sources[source]["pain_points"])

        # Group by keyword
        pain_groups = {}
        for pain in all_pain_points:
            keyword = pain.get("keyword", "unknown")
            if keyword not in pain_groups:
                pain_groups[keyword] = {"count": 0, "sources": []}
            pain_groups[keyword]["count"] += 1
            pain_groups[keyword]["sources"].append(pain.get("source", "unknown"))

        # Rank by frequency
        top_pain_points = sorted(
            [
                {"keyword": k, "frequency": v["count"], "sources": list(set(v["sources"]))}
                for k, v in pain_groups.items()
            ],
            key=lambda x: x["frequency"],
            reverse=True
        )[:10]

        return {
            "clinic_type": evidence["clinic_type"],
            "top_pain_points": top_pain_points,
            "data_sources": len([s for s in sources.values() if "error" not in s]),
            "total_pain_points_discovered": len(all_pain_points),
            "recommendation": f"Analyzed {len(all_pain_points)} pain points across industry sources"
        }


if __name__ == "__main__":
    # Test the clinics collector
    collector = ClinicsEvidenceCollector()

    # Example 1: Single clinic analysis
    clinic_evidence = collector.collect_clinic_evidence(
        clinic_name="London Physiotherapy Clinic",
        clinic_type="physiotherapy",
        location="London UK",
        include_social=True
    )

    print(f"\n📊 Clinic Evidence Score: {clinic_evidence['evidence_score']}/100")
    print(f"💡 Recommendation: {clinic_evidence['unified_insights']['recommendation']}")

    # Example 2: Clinic type analysis
    type_evidence = collector.collect_clinic_type_evidence(
        clinic_type="physiotherapy",
        location="UK",
        sample_size=10
    )

    print(f"\n📊 Type Evidence Score: {type_evidence['evidence_score']}/100")
    print(f"🔥 Top Pain Points: {[p['keyword'] for p in type_evidence['unified_insights']['top_pain_points'][:5]]}")

    # Save reports
    collector.save_evidence_report(
        clinic_evidence,
        "data/reports/clinic_evidence.json"
    )
