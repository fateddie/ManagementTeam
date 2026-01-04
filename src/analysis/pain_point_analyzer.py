#!/usr/bin/env python3
"""
pain_point_analyzer.py
-------------------------------------
Extends DemandValidator for clinic-specific pain point analysis.
Cross-validates pain points from Google Reviews with social data (Reddit, X).

Features:
- Inherits transparency principles from DemandValidator
- Cross-source pain point validation
- Clinic review sentiment analysis
- Industry trend correlation
- Confidence scoring based on multiple sources

TRANSPARENCY PRINCIPLES (inherited):
- All metrics include source_reviews/source_posts arrays
- Confidence levels based on cross-validation
- Audit trails for reproducibility
- Example quotes from multiple sources
- Configurable scoring via config file

See PRINCIPLES.md and CLAUDE.md for implementation guidelines.
-------------------------------------
"""

import pandas as pd
from collections import Counter
from typing import Dict, List, Optional
import json
from datetime import datetime
from pathlib import Path

# Import base class
from .demand_validator import DemandValidator


class PainPointAnalyzer(DemandValidator):
    """
    Extends DemandValidator for clinic pain point analysis.

    Inherits:
        - Transparency patterns (source tracking, confidence scoring, audit trails)
        - Configuration management
        - Example quote extraction

    Adds:
        - Cross-validation between clinic reviews and social data
        - Review-specific sentiment analysis
        - Industry publication correlation
        - Clinic-type specific insights
    """

    def __init__(
        self,
        csv_path: str = None,
        config_path: str = "config/transparency_config.json",
        reviews_df: pd.DataFrame = None
    ):
        """
        Initialize Pain Point Analyzer

        Args:
            csv_path: Path to social posts CSV (optional if reviews_df provided)
            config_path: Path to transparency configuration
            reviews_df: DataFrame of clinic reviews (optional)
        """
        # Initialize parent if social data provided
        if csv_path:
            super().__init__(csv_path, config_path)
        else:
            # Minimal initialization if only using reviews
            self.df = pd.DataFrame()
            self.total_posts = 0
            self.csv_path = None

            # Load config using parent's pattern
            from src.utils.config_utils import load_config
            default_config = {
                "scoring_config": {
                    "thresholds": {
                        "minimum_reviews": 10,
                        "cross_validation_threshold": 3
                    },
                    "confidence_thresholds": {
                        "high_confidence_posts": 10,
                        "medium_confidence_posts": 5,
                        "low_confidence_posts": 2
                    }
                }
            }
            self.config = load_config(config_path, default_config)
            self.config_path = config_path
            self.thresholds = self.config.get('scoring_config', {}).get('thresholds', {})
            self.confidence_thresholds = self.config.get('scoring_config', {}).get('confidence_thresholds', {})

        # Clinic-specific data
        self.reviews_df = reviews_df if reviews_df is not None else pd.DataFrame()
        self.total_reviews = len(self.reviews_df)

    def analyze_pain_points(
        self,
        clinic_evidence: Dict
    ) -> Dict:
        """
        Cross-validate pain points from clinic reviews + social sources

        Args:
            clinic_evidence: Evidence dict from ClinicsEvidenceCollector

        Returns:
            Dict with cross-validated pain points, confidence scores, examples
        """
        print("\n🔍 Analyzing Pain Points with Cross-Validation")
        print("=" * 70)

        # Extract pain points from each source
        clinic_pains = self._extract_clinic_pain_points(
            clinic_evidence.get("sources", {}).get("google_reviews", {})
        )

        social_pains = self._extract_social_pain_points(
            clinic_evidence.get("sources", {})
        )

        publication_pains = self._extract_publication_pain_points(
            clinic_evidence.get("sources", {}).get("publications", {})
        )

        # Cross-validate
        cross_validated = self._cross_validate_pain_points(
            clinic_pains,
            social_pains,
            publication_pains
        )

        # Generate analysis
        analysis = {
            "clinic_name": clinic_evidence.get("clinic_name"),
            "clinic_type": clinic_evidence.get("clinic_type"),
            "analyzed_at": datetime.now().isoformat(),
            "pain_points": cross_validated,
            "summary": {
                "total_pain_points_identified": len(cross_validated),
                "high_confidence_pain_points": len([p for p in cross_validated if p["confidence"] == "high"]),
                "medium_confidence_pain_points": len([p for p in cross_validated if p["confidence"] == "medium"]),
                "low_confidence_pain_points": len([p for p in cross_validated if p["confidence"] == "low"]),
                "sources_analyzed": {
                    "google_reviews": len(clinic_pains),
                    "social_media": len(social_pains),
                    "publications": len(publication_pains)
                }
            },
            "_audit_trail": {
                "generated_at": datetime.now().isoformat(),
                "clinic_reviews_analyzed": len(clinic_evidence.get("sources", {}).get("google_reviews", {}).get("top_reviews", [])),
                "social_posts_analyzed": clinic_evidence.get("sources", {}).get("reddit", {}).get("total_posts", 0),
                "publications_analyzed": clinic_evidence.get("sources", {}).get("publications", {}).get("total_articles", 0),
                "cross_validation_method": "keyword_overlap_with_sentiment",
                "confidence_thresholds": self.confidence_thresholds,
                "config_file": self.config_path
            }
        }

        print(f"\n✅ Pain Point Analysis Complete")
        print(f"📊 Total Pain Points: {analysis['summary']['total_pain_points_identified']}")
        print(f"🎯 High Confidence: {analysis['summary']['high_confidence_pain_points']}")

        return analysis

    def _extract_clinic_pain_points(self, google_reviews_data: Dict) -> List[Dict]:
        """Extract pain points from Google Reviews"""
        pain_points = []

        for pain_group in google_reviews_data.get("pain_points", []):
            pain_points.append({
                "keyword": pain_group.get("keyword"),
                "frequency": pain_group.get("frequency", 0),
                "source": "google_reviews",
                "examples": pain_group.get("examples", []),
                "avg_rating": pain_group.get("avg_rating"),
                "sentiment": pain_group.get("avg_sentiment")
            })

        return pain_points

    def _extract_social_pain_points(self, sources: Dict) -> List[Dict]:
        """Extract pain points from social sources (Reddit, X)"""
        pain_points = []

        # Reddit pain points
        if "reddit" in sources:
            for pain_group in sources["reddit"].get("pain_points", []):
                pain_points.append({
                    "keyword": pain_group.get("keyword"),
                    "frequency": pain_group.get("frequency", 0),
                    "source": "reddit",
                    "examples": pain_group.get("examples", []),
                    "avg_score": pain_group.get("avg_score"),
                    "sentiment": pain_group.get("avg_sentiment")
                })

        # X pain points (if available)
        # Note: X connector may not have pain_points extraction yet
        # This is future-proofing

        return pain_points

    def _extract_publication_pain_points(self, publications_data: Dict) -> List[Dict]:
        """Extract pain points from industry publications"""
        pain_points = []

        for pain_group in publications_data.get("pain_points", []):
            pain_points.append({
                "keyword": pain_group.get("keyword"),
                "frequency": pain_group.get("frequency", 0),
                "source": "publications",
                "examples": pain_group.get("examples", []),
                "recent_mentions": pain_group.get("recent_mentions", 0),
                "sentiment": pain_group.get("avg_sentiment")
            })

        return pain_points

    def _cross_validate_pain_points(
        self,
        clinic_pains: List[Dict],
        social_pains: List[Dict],
        publication_pains: List[Dict]
    ) -> List[Dict]:
        """
        Cross-validate pain points across sources

        High confidence: Mentioned in 2+ source types
        Medium confidence: Strong signal in 1 source
        Low confidence: Weak signals
        """
        # Group all pain points by keyword
        pain_groups = {}

        for pain in clinic_pains + social_pains + publication_pains:
            keyword = pain["keyword"]
            if keyword not in pain_groups:
                pain_groups[keyword] = {
                    "keyword": keyword,
                    "sources": set(),
                    "clinic_mentions": 0,
                    "social_mentions": 0,
                    "publication_mentions": 0,
                    "examples": {"clinic": [], "social": [], "publications": []},
                    "sentiment_scores": []
                }

            pg = pain_groups[keyword]
            pg["sources"].add(pain["source"])

            if pain["source"] == "google_reviews":
                pg["clinic_mentions"] += pain["frequency"]
                pg["examples"]["clinic"].extend(pain.get("examples", [])[:2])
                if pain.get("sentiment") is not None:
                    pg["sentiment_scores"].append(pain["sentiment"])

            elif pain["source"] in ["reddit", "x"]:
                pg["social_mentions"] += pain["frequency"]
                pg["examples"]["social"].extend(pain.get("examples", [])[:2])
                if pain.get("sentiment") is not None:
                    pg["sentiment_scores"].append(pain["sentiment"])

            elif pain["source"] == "publications":
                pg["publication_mentions"] += pain["frequency"]
                pg["examples"]["publications"].extend(pain.get("examples", [])[:2])
                if pain.get("sentiment") is not None:
                    pg["sentiment_scores"].append(pain["sentiment"])

        # Convert to ranked list with confidence scoring
        cross_validated = []

        for keyword, data in pain_groups.items():
            # Confidence assessment
            num_sources = len(data["sources"])
            total_mentions = data["clinic_mentions"] + data["social_mentions"] + data["publication_mentions"]

            # High: 2+ sources OR 10+ mentions in one source
            if num_sources >= 2 or total_mentions >= 10:
                confidence = "high"
                confidence_score = 0.9 if num_sources >= 3 else 0.8 if num_sources >= 2 else 0.7
            # Medium: Strong signal in 1 source (5+ mentions)
            elif total_mentions >= 5:
                confidence = "medium"
                confidence_score = 0.6
            # Low: Weak signals
            else:
                confidence = "low"
                confidence_score = 0.3

            # Aggregate sentiment
            avg_sentiment = sum(data["sentiment_scores"]) / len(data["sentiment_scores"]) if data["sentiment_scores"] else None

            # Importance score: mentions × sources × sentiment_severity
            sentiment_severity = (1 - avg_sentiment) if avg_sentiment is not None else 1.0
            importance = total_mentions * num_sources * sentiment_severity

            cross_validated.append({
                "pain_point": keyword.replace("_", " ").title(),
                "keyword": keyword,
                "total_mentions": total_mentions,
                "clinic_mentions": data["clinic_mentions"],
                "social_mentions": data["social_mentions"],
                "publication_mentions": data["publication_mentions"],
                "sources": list(data["sources"]),
                "num_sources": num_sources,
                "confidence": confidence,
                "confidence_score": round(confidence_score, 2),
                "importance_score": round(importance, 2),
                "avg_sentiment": round(avg_sentiment, 2) if avg_sentiment is not None else None,
                "examples": {
                    "clinic": [e["text"] if isinstance(e, dict) else str(e)[:200] for e in data["examples"]["clinic"][:2]],
                    "social": [e["text"] if isinstance(e, dict) else str(e)[:200] for e in data["examples"]["social"][:2]],
                    "publications": [e["text"] if isinstance(e, dict) else str(e)[:200] for e in data["examples"]["publications"][:2]]
                },
                "source_reviews": self._extract_source_ids(data["examples"]["clinic"]),
                "source_posts": self._extract_source_ids(data["examples"]["social"]),
                "source_articles": self._extract_source_ids(data["examples"]["publications"]),
                "interpretation": self._interpret_pain_point(
                    keyword,
                    num_sources,
                    total_mentions,
                    avg_sentiment
                )
            })

        # Sort by importance score
        cross_validated.sort(key=lambda x: x["importance_score"], reverse=True)

        return cross_validated

    def _extract_source_ids(self, examples: List) -> List[str]:
        """Extract source IDs from example objects"""
        ids = []
        for ex in examples:
            if isinstance(ex, dict):
                # Try common ID fields
                id_val = ex.get("id") or ex.get("review_id") or ex.get("url")
                if id_val:
                    ids.append(str(id_val))
        return ids

    def _interpret_pain_point(
        self,
        keyword: str,
        num_sources: int,
        mentions: int,
        sentiment: Optional[float]
    ) -> str:
        """Generate human-readable interpretation of pain point"""

        strength = "STRONG" if num_sources >= 2 else "MODERATE" if mentions >= 5 else "WEAK"

        if sentiment is not None and sentiment < -0.3:
            severity = "CRITICAL - Highly negative sentiment"
        elif sentiment is not None and sentiment < 0:
            severity = "SIGNIFICANT - Negative sentiment"
        else:
            severity = "MODERATE - Mixed sentiment"

        validation = f"Validated across {num_sources} sources" if num_sources >= 2 else "Single source validation"

        return f"{strength} signal: {validation}. {severity}."

    def generate_pain_point_report(
        self,
        analysis: Dict,
        output_format: str = "markdown"
    ) -> str:
        """
        Generate human-readable pain point report

        Args:
            analysis: Pain point analysis dict
            output_format: "markdown" or "json"

        Returns:
            Formatted report string
        """
        if output_format == "json":
            return json.dumps(analysis, indent=2)

        # Markdown report
        md = f"""# Pain Point Analysis Report

**Clinic:** {analysis.get('clinic_name', 'Unknown')}
**Type:** {analysis.get('clinic_type', 'Unknown')}
**Analyzed:** {analysis['analyzed_at']}

---

## Executive Summary

**Total Pain Points Identified:** {analysis['summary']['total_pain_points_identified']}

**Confidence Breakdown:**
- 🎯 High Confidence: {analysis['summary']['high_confidence_pain_points']}
- 🟡 Medium Confidence: {analysis['summary']['medium_confidence_pain_points']}
- ⚪ Low Confidence: {analysis['summary']['low_confidence_pain_points']}

**Data Sources:**
- Google Reviews: {analysis['summary']['sources_analyzed']['google_reviews']} pain points
- Social Media: {analysis['summary']['sources_analyzed']['social_media']} pain points
- Publications: {analysis['summary']['sources_analyzed']['publications']} pain points

---

## Top Pain Points (Cross-Validated)

"""

        # Top 10 pain points
        for i, pain in enumerate(analysis['pain_points'][:10], 1):
            confidence_badge = "🎯" if pain['confidence'] == "high" else "🟡" if pain['confidence'] == "medium" else "⚪"

            md += f"""### {i}. {pain['pain_point']} {confidence_badge}

**Mentions:** {pain['total_mentions']} total (Clinic: {pain['clinic_mentions']}, Social: {pain['social_mentions']}, Publications: {pain['publication_mentions']})

**Sources:** {', '.join(pain['sources'])}

**Confidence:** {pain['confidence']} ({pain['confidence_score']})

**Importance Score:** {pain['importance_score']}

**Interpretation:** {pain['interpretation']}

**Example Quotes:**
"""

            if pain['examples']['clinic']:
                md += f"- *Clinic Review:* \"{pain['examples']['clinic'][0][:150]}...\"\n"
            if pain['examples']['social']:
                md += f"- *Social Media:* \"{pain['examples']['social'][0][:150]}...\"\n"
            if pain['examples']['publications']:
                md += f"- *Publication:* \"{pain['examples']['publications'][0][:150]}...\"\n"

            md += "\n---\n\n"

        # Audit trail
        md += f"""## Audit Trail

**Generated:** {analysis['_audit_trail']['generated_at']}

**Data Analyzed:**
- Clinic Reviews: {analysis['_audit_trail']['clinic_reviews_analyzed']}
- Social Posts: {analysis['_audit_trail']['social_posts_analyzed']}
- Publications: {analysis['_audit_trail']['publications_analyzed']}

**Method:** {analysis['_audit_trail']['cross_validation_method']}

**Config:** {analysis['_audit_trail']['config_file']}

---

*Report generated by Pain Point Analyzer (extends DemandValidator)*
*Follows transparency principles: All pain points include source references, confidence scores, and example quotes*
"""

        return md

    def export_pain_point_report(
        self,
        analysis: Dict,
        output_path: str,
        format: str = "markdown"
    ):
        """
        Export pain point report to file

        Args:
            analysis: Pain point analysis dict
            output_path: Path to save report
            format: "markdown" or "json"
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        report = self.generate_pain_point_report(analysis, output_format=format)

        with open(output_file, 'w') as f:
            f.write(report)

        print(f"\n💾 Pain point report saved to: {output_file}")

        # Also save raw JSON
        if format == "markdown":
            json_file = output_file.with_suffix('.json')
            with open(json_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            print(f"📊 Raw data saved to: {json_file}")


if __name__ == "__main__":
    # Test the analyzer with mock data
    print("Pain Point Analyzer - Test Mode")
    print("=" * 70)

    # Mock clinic evidence (in real usage, this comes from ClinicsEvidenceCollector)
    mock_evidence = {
        "clinic_name": "London Physiotherapy Clinic",
        "clinic_type": "physiotherapy",
        "sources": {
            "google_reviews": {
                "pain_points": [
                    {
                        "keyword": "waiting",
                        "frequency": 12,
                        "avg_rating": 2.5,
                        "avg_sentiment": -0.4,
                        "examples": [
                            {"text": "Waited 3 weeks for an appointment", "id": "1"},
                            {"text": "Long waiting times are frustrating", "id": "2"}
                        ]
                    },
                    {
                        "keyword": "booking",
                        "frequency": 8,
                        "avg_rating": 3.0,
                        "avg_sentiment": -0.2,
                        "examples": [
                            {"text": "Booking system is terrible", "id": "3"}
                        ]
                    }
                ]
            },
            "reddit": {
                "total_posts": 43,
                "pain_points": [
                    {
                        "keyword": "waiting",
                        "frequency": 7,
                        "avg_score": 15.3,
                        "avg_sentiment": -0.3,
                        "examples": [
                            {"text": "Physio clinics have terrible waiting times", "url": "reddit.com/123"}
                        ]
                    }
                ]
            },
            "publications": {
                "total_articles": 10,
                "pain_points": [
                    {
                        "keyword": "waiting",
                        "frequency": 5,
                        "recent_mentions": 3,
                        "avg_sentiment": -0.1,
                        "examples": [
                            {"text": "Industry faces patient access challenges", "url": "article.com/1"}
                        ]
                    },
                    {
                        "keyword": "staffing",
                        "frequency": 8,
                        "recent_mentions": 6,
                        "avg_sentiment": -0.5,
                        "examples": [
                            {"text": "Chronic staffing shortages affect service", "url": "article.com/2"}
                        ]
                    }
                ]
            }
        }
    }

    # Analyze pain points
    analyzer = PainPointAnalyzer()
    analysis = analyzer.analyze_pain_points(mock_evidence)

    # Print summary
    print(f"\n📊 Analysis Summary:")
    print(f"Total Pain Points: {analysis['summary']['total_pain_points_identified']}")
    print(f"High Confidence: {analysis['summary']['high_confidence_pain_points']}")

    # Print top 3 pain points
    print(f"\n🔥 Top 3 Pain Points:")
    for i, pain in enumerate(analysis['pain_points'][:3], 1):
        print(f"{i}. {pain['pain_point']} - {pain['total_mentions']} mentions "
              f"({pain['num_sources']} sources, {pain['confidence']} confidence)")

    # Export report
    analyzer.export_pain_point_report(
        analysis,
        "data/reports/pain_point_analysis.md",
        format="markdown"
    )
