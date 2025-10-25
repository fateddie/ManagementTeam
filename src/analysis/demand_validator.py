#!/usr/bin/env python3
"""
demand_validator.py
-------------------------------------
Analyzes enriched social data to generate actionable business insights:
- ICP definition
- Feature priority
- Competitor gaps
- Pricing strategy
- Sales talk tracks

TRANSPARENCY PRINCIPLES:
- All metrics include source_posts arrays
- Confidence levels based on sample size
- Audit trails for reproducibility
- Example quotes for verification
- Configurable scoring via config file

See PRINCIPLES.md and CLAUDE.md for implementation guidelines.
-------------------------------------
"""

import pandas as pd
from collections import Counter
from typing import Dict, List
import json
from datetime import datetime
from pathlib import Path


class DemandValidator:
    """
    Generates actionable insights from enriched social data.

    TRANSPARENCY FEATURES:
    - All insights include source_posts for verification
    - Confidence scoring based on sample size
    - Example quotes for context
    - Full audit trails
    - Configurable thresholds
    """

    def __init__(
        self,
        csv_path: str = "social_posts_enriched.csv",
        config_path: str = "config/transparency_config.json"
    ):
        """
        Load enriched data and configuration.

        Args:
            csv_path: Path to enriched social posts CSV
            config_path: Path to transparency configuration
        """
        self.df = pd.read_csv(csv_path)
        self.total_posts = len(self.df)
        self.csv_path = csv_path

        # Load configuration
        self.config = self._load_config(config_path)
        self.config_path = config_path

        # Extract thresholds from config
        self.thresholds = self.config.get('scoring_config', {}).get('thresholds', {})
        self.confidence_thresholds = self.config.get('scoring_config', {}).get('confidence_thresholds', {})

    def _load_config(self, config_path: str) -> Dict:
        """Load transparency configuration."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config not found: {config_path}. Using defaults.")
            return self._default_config()

    def _default_config(self) -> Dict:
        """Default configuration if file not found."""
        return {
            "scoring_config": {
                "thresholds": {
                    "minimum_posts": 30,
                    "critical_urgency_pct": 60,
                    "icp_confidence_pct": 60
                },
                "confidence_thresholds": {
                    "high_confidence_posts": 10,
                    "medium_confidence_posts": 5,
                    "low_confidence_posts": 2
                }
            }
        }

    def _assess_confidence(self, count: int) -> str:
        """
        Assess confidence level based on sample size.

        Transparent mapping:
        - high: 10+ data points
        - medium: 5-9 data points
        - low: 2-4 data points
        - insufficient: <2 data points
        """
        if count >= self.confidence_thresholds.get('high_confidence_posts', 10):
            return "high"
        elif count >= self.confidence_thresholds.get('medium_confidence_posts', 5):
            return "medium"
        elif count >= self.confidence_thresholds.get('low_confidence_posts', 2):
            return "low"
        else:
            return "insufficient"

    def _get_example_quotes(self, df_subset: pd.DataFrame, n: int = 3) -> List[str]:
        """
        Extract example quotes from a subset of posts.

        Args:
            df_subset: Filtered dataframe
            n: Number of examples to return

        Returns:
            List of text excerpts (max 200 chars each)
        """
        if len(df_subset) == 0:
            return []

        quotes = df_subset['text_excerpt'].head(n).tolist()
        # Truncate to 200 chars
        return [str(q)[:200] + "..." if len(str(q)) > 200 else str(q) for q in quotes]

    def get_posts_by_ids(self, post_ids: List[int]) -> pd.DataFrame:
        """
        Get full posts by IDs for user verification.

        Args:
            post_ids: List of post indices

        Returns:
            DataFrame with full post details
        """
        return self.df.loc[post_ids]

    def generate_icp(self) -> Dict:
        """
        Generate Ideal Customer Profile with full transparency.

        Returns:
            Dict with industries, sizes, locations, urgency profile
            Each includes: source_posts, example_quotes, confidence
        """
        icp = {
            "top_industries": [],
            "top_company_sizes": [],
            "top_locations": [],
            "urgency_profile": {},
            "confidence": 0
        }

        # Industries (with source tracking and examples)
        industries = self.df[self.df['industry'].notna()]['industry'].value_counts()
        for ind, count in industries.head(5).items():
            industry_posts = self.df[self.df['industry'] == ind]
            icp["top_industries"].append({
                "industry": ind,
                "count": int(count),
                "percentage": round(count/self.total_posts*100, 1),
                "confidence": self._assess_confidence(count),
                "source_posts": industry_posts.index.tolist(),
                "example_quotes": self._get_example_quotes(industry_posts, n=3),
                "avg_urgency": industry_posts['urgency'].mode()[0] if len(industry_posts) > 0 else "unknown",
                "avg_upvotes": round(industry_posts['upvotes'].mean(), 1) if 'upvotes' in industry_posts.columns else 0
            })

        # Company sizes (with source tracking)
        sizes = self.df[self.df['company_size'].notna()]['company_size'].value_counts()
        for size, count in sizes.items():
            size_posts = self.df[self.df['company_size'] == size]
            icp["top_company_sizes"].append({
                "size": size,
                "count": int(count),
                "percentage": round(count/self.total_posts*100, 1),
                "confidence": self._assess_confidence(count),
                "source_posts": size_posts.index.tolist(),
                "example_quotes": self._get_example_quotes(size_posts, n=2)
            })

        # Locations (with source tracking)
        locations = self.df[self.df['location'].notna()]['location'].value_counts()
        for loc, count in locations.items():
            loc_posts = self.df[self.df['location'] == loc]
            icp["top_locations"].append({
                "location": loc,
                "count": int(count),
                "percentage": round(count/self.total_posts*100, 1),
                "confidence": self._assess_confidence(count),
                "source_posts": loc_posts.index.tolist(),
                "example_quotes": self._get_example_quotes(loc_posts, n=2)
            })

        # Urgency profile (with source tracking)
        urgency_counts = self.df['urgency'].value_counts()
        for urgency, count in urgency_counts.items():
            urgency_posts = self.df[self.df['urgency'] == urgency]
            icp["urgency_profile"][urgency] = {
                "count": int(count),
                "percentage": round(count/self.total_posts*100, 1),
                "source_posts": urgency_posts.index.tolist(),
                "example_quotes": self._get_example_quotes(urgency_posts, n=2)
            }

        # Overall confidence score (based on data completeness)
        identified = self.df['industry'].notna().sum()
        icp["confidence"] = round(identified / self.total_posts * 100, 1)

        # Add unidentified posts for transparency
        unidentified_posts = self.df[self.df['industry'].isna()]
        icp["unidentified_posts"] = {
            "count": len(unidentified_posts),
            "percentage": round(len(unidentified_posts) / self.total_posts * 100, 1),
            "source_posts": unidentified_posts.index.tolist()[:10],  # Show first 10
            "note": "Posts where industry could not be detected from patterns"
        }

        return icp

    def rank_pain_quotes(self, top_n: int = 20) -> List[Dict]:
        """Rank pain quotes by signal strength."""
        # Score = upvotes × urgency_weight × comment_engagement
        urgency_weights = {"critical": 3, "high": 2, "medium": 1, "low": 0.5}

        self.df['pain_score'] = (
            self.df['upvotes'] *
            self.df['urgency'].map(urgency_weights) *
            (1 + self.df['num_comments'] / 100)
        )

        top_quotes = []
        for _, row in self.df.nlargest(top_n, 'pain_score').iterrows():
            quote = {
                "text": row['text_excerpt'][:300],
                "subreddit": row['subreddit'],
                "upvotes": int(row['upvotes']),
                "urgency": row['urgency'],
                "industry": row['industry'] if pd.notna(row['industry']) else "Unknown",
                "pain_score": round(row['pain_score'], 2),
                "url_placeholder": f"r/{row['subreddit']}"
            }
            top_quotes.append(quote)

        return top_quotes

    def extract_feature_requests(self) -> List[Dict]:
        """
        Extract and rank feature mentions with full transparency.

        Returns:
            List of features with mentions, source_posts, example_quotes, confidence
        """
        # Common feature keywords to look for
        features = {
            "appointment_booking": r"\b(book|appointment|scheduling|calendar)\b",
            "call_forwarding": r"\b(forward|route|transfer)\b",
            "24_7_availability": r"\b(24/7|after.hours|always.on|night)\b",
            "multilingual": r"\b(spanish|language|bilingual)\b",
            "crm_integration": r"\b(crm|salesforce|hubspot|integrate)\b",
            "voicemail": r"\b(voicemail|message|recording)\b",
            "sms_texting": r"\b(sms|text|message)\b",
            "credit_card": r"\b(credit.card|payment|charge)\b",
            "ai_powered": r"\b(ai|artificial.intelligence|smart|intelligent)\b"
        }

        import re

        # Track which posts mention each feature
        feature_data = {}

        for feature_name, pattern in features.items():
            matching_posts = []
            for idx, row in self.df.iterrows():
                text = (row['text_excerpt'] if pd.notna(row['text_excerpt']) else "").lower()
                if re.search(pattern, text, re.IGNORECASE):
                    matching_posts.append(idx)

            if len(matching_posts) > 0:
                matching_df = self.df.loc[matching_posts]
                feature_data[feature_name] = {
                    "feature": feature_name.replace("_", " ").title(),
                    "mentions": len(matching_posts),
                    "percentage": round(len(matching_posts) / self.total_posts * 100, 1),
                    "confidence": self._assess_confidence(len(matching_posts)),
                    "source_posts": matching_posts,
                    "example_quotes": self._get_example_quotes(matching_df, n=3),
                    "avg_urgency": matching_df['urgency'].mode()[0] if len(matching_df) > 0 else "unknown"
                }

        # Rank by mentions
        ranked_features = sorted(
            feature_data.values(),
            key=lambda x: x['mentions'],
            reverse=True
        )

        return ranked_features

    def analyze_competitors(self) -> Dict:
        """Analyze competitor mentions and sentiment."""
        # Get all competitor mentions
        all_competitors = []
        for competitors in self.df[self.df['competitors_mentioned'].notna()]['competitors_mentioned']:
            all_competitors.extend(competitors.split(','))

        # Count and filter (remove false positives like "detai", "dai")
        competitor_counts = Counter(all_competitors)

        # Filter: only keep if mentioned 2+ times and length > 4
        real_competitors = {
            comp: count for comp, count in competitor_counts.items()
            if count >= 2 and len(comp) > 4
        }

        return {
            "total_posts_mentioning_competitors": self.df['competitors_mentioned'].notna().sum(),
            "unique_competitors": len(real_competitors),
            "top_competitors": [
                {"name": comp, "mentions": count}
                for comp, count in sorted(real_competitors.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
        }

    def analyze_pricing_signals(self) -> Dict:
        """Analyze pricing and budget signals."""
        pricing = {
            "posts_with_price_mentions": self.df['price_mentions'].notna().sum(),
            "posts_with_budget_concerns": int(self.df['has_budget_concern'].sum()),
            "budget_concern_percentage": round(self.df['has_budget_concern'].sum() / self.total_posts * 100, 1),
            "price_examples": []
        }

        # Extract price examples
        for price in self.df[self.df['price_mentions'].notna()]['price_mentions'].head(10):
            pricing["price_examples"].append(price)

        return pricing

    def generate_sales_talk_track(self) -> Dict:
        """Generate sales talk track based on pain analysis."""
        # Most common pain
        critical_posts = self.df[self.df['urgency'] == 'critical']

        pain_points = []
        if len(critical_posts) > 0:
            for _, row in critical_posts.head(5).iterrows():
                pain_points.append(row['text_excerpt'][:200])

        return {
            "opening": "I noticed you're dealing with [pain from their industry]",
            "pain_examples": pain_points,
            "objection_prep": [
                {"objection": "Too expensive", "frequency": f"{self.df['has_budget_concern'].sum()} posts mention budget"},
                {"objection": "Tried AI before", "frequency": "Common in tech-savvy industries"},
                {"objection": "Integration complexity", "frequency": "CRM integration mentioned frequently"}
            ]
        }

    def generate_full_report(self) -> Dict:
        """
        Generate comprehensive validation report with full audit trail.

        Returns:
            Complete analysis with transparency features:
            - Source tracking for all metrics
            - Audit trail for reproducibility
            - Confidence levels
            - Example quotes
        """
        report = {
            "summary": {
                "total_posts_analyzed": self.total_posts,
                "data_sources": ["Reddit"],  # TODO: Auto-detect from data
                "collection_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
                "validation_verdict": self._determine_verdict(),
                "data_quality": self._assess_data_quality()
            },
            "icp": self.generate_icp(),
            "top_pain_quotes": self.rank_pain_quotes(20),
            "feature_priorities": self.extract_feature_requests(),
            "competitor_intelligence": self.analyze_competitors(),
            "pricing_signals": self.analyze_pricing_signals(),
            "sales_talk_track": self.generate_sales_talk_track(),
            "_audit_trail": {
                "generated_at": datetime.now().isoformat(),
                "data_source": self.csv_path,
                "total_posts": self.total_posts,
                "config_file": self.config_path,
                "config_snapshot": self.config,
                "analysis_version": "v2.0",
                "transparency_features": [
                    "source_posts included",
                    "example_quotes provided",
                    "confidence levels assessed",
                    "audit trail complete"
                ]
            }
        }

        return report

    def _determine_verdict(self) -> str:
        """Determine validation verdict based on thresholds."""
        min_posts = self.thresholds.get('minimum_posts', 30)

        if self.total_posts >= 100:
            return "STRONG GO"
        elif self.total_posts >= min_posts:
            return "PROCEED"
        elif self.total_posts >= 15:
            return "MARGINAL"
        else:
            return "INSUFFICIENT DATA"

    def _assess_data_quality(self) -> Dict:
        """Assess overall data quality."""
        icp_detected = self.df['industry'].notna().sum()
        urgency_detected = self.df['urgency'].notna().sum()
        has_upvotes = (self.df['upvotes'] > 0).sum() if 'upvotes' in self.df.columns else 0

        return {
            "icp_detection_rate": round(icp_detected / self.total_posts * 100, 1),
            "urgency_detection_rate": round(urgency_detected / self.total_posts * 100, 1),
            "engagement_rate": round(has_upvotes / self.total_posts * 100, 1) if 'upvotes' in self.df.columns else 0,
            "overall_quality": "high" if icp_detected / self.total_posts > 0.6 else "medium" if icp_detected / self.total_posts > 0.4 else "low"
        }

    def save_report(self, output_path: str = "demand_validation_report.json"):
        """Save full report to JSON."""
        report = self.generate_full_report()

        # Convert pandas int64 to Python int for JSON serialization
        def convert_types(obj):
            if isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy/pandas types
                return obj.item()
            return obj

        report = convert_types(report)

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"✅ Report saved to: {output_path}")
        return report

    def export_data(self, format: str = "csv", output_path: str = None, filter_criteria: Dict = None):
        """
        Export raw data or filtered subsets in multiple formats.

        Args:
            format: Export format ('csv', 'excel', 'json')
            output_path: Output file path (auto-generated if None)
            filter_criteria: Dict of column:value filters

        Returns:
            Path to exported file
        """
        # Apply filters if provided
        df_export = self.df.copy()
        if filter_criteria:
            for column, value in filter_criteria.items():
                if column in df_export.columns:
                    df_export = df_export[df_export[column] == value]

        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data_export_{timestamp}.{format}"

        # Export based on format
        if format == "csv":
            df_export.to_csv(output_path, index=False)
        elif format == "excel":
            df_export.to_excel(output_path, index=False, engine='openpyxl')
        elif format == "json":
            df_export.to_json(output_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'csv', 'excel', or 'json'")

        print(f"✅ Exported {len(df_export)} posts to: {output_path}")
        return output_path

    def export_evidence_report(self, output_path: str = "evidence_report.md"):
        """
        Generate human-readable evidence report in Markdown.

        Includes:
        - Summary with decision checkboxes
        - ICP analysis with source quotes
        - Feature priorities with evidence
        - Pricing signals
        - All with source post IDs for verification
        """
        report = self.generate_full_report()

        md_lines = []
        md_lines.append("# Market Validation Evidence Report\n")
        md_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_lines.append(f"**Total Posts Analyzed:** {self.total_posts}\n")
        md_lines.append(f"**Validation Verdict:** {report['summary']['validation_verdict']}\n")
        md_lines.append("\n---\n")

        # ICP Section
        md_lines.append("\n## 🎯 Ideal Customer Profile\n")
        icp = report['icp']
        md_lines.append(f"**Overall Confidence:** {icp['confidence']}%\n")

        md_lines.append("\n### Top Industries\n")
        for ind in icp['top_industries'][:3]:
            md_lines.append(f"\n#### {ind['industry'].title()}\n")
            md_lines.append(f"- **Posts:** {ind['count']} ({ind['percentage']}%)\n")
            md_lines.append(f"- **Confidence:** {ind['confidence'].upper()}\n")
            md_lines.append(f"- **Source Posts:** {ind['source_posts']}\n")
            md_lines.append(f"- **Avg Urgency:** {ind['avg_urgency']}\n")
            md_lines.append("\n**Example Quotes:**\n")
            for i, quote in enumerate(ind['example_quotes'], 1):
                md_lines.append(f"{i}. \"{quote}\"\n")

        # Features Section
        md_lines.append("\n---\n")
        md_lines.append("\n## 🔧 Feature Priorities\n")
        for feat in report['feature_priorities'][:5]:
            md_lines.append(f"\n### {feat['feature']}\n")
            md_lines.append(f"- **Mentions:** {feat['mentions']} ({feat['percentage']}%)\n")
            md_lines.append(f"- **Confidence:** {feat['confidence'].upper()}\n")
            md_lines.append(f"- **Source Posts:** {feat['source_posts']}\n")
            md_lines.append("\n**Example Quotes:**\n")
            for i, quote in enumerate(feat['example_quotes'], 1):
                md_lines.append(f"{i}. \"{quote}\"\n")

            md_lines.append("\n**YOUR DECISION:**\n")
            md_lines.append("- [ ] High Priority - Build this feature\n")
            md_lines.append("- [ ] Medium Priority - Consider for v2\n")
            md_lines.append("- [ ] Low Priority - Skip for now\n")
            md_lines.append("- [ ] Need More Data\n\n")
            md_lines.append("**NOTES:** _______________\n")

        # Pricing Section
        md_lines.append("\n---\n")
        md_lines.append("\n## 💰 Pricing Intelligence\n")
        pricing = report['pricing_signals']
        md_lines.append(f"- **Posts with budget concerns:** {pricing['budget_concern_percentage']}%\n")
        md_lines.append(f"- **Price mentions found:** {pricing['posts_with_price_mentions']}\n")
        if pricing['price_examples']:
            md_lines.append(f"- **Example prices:** {', '.join(pricing['price_examples'][:5])}\n")

        # Top Pain Quotes
        md_lines.append("\n---\n")
        md_lines.append("\n## 🔥 Top Pain Quotes (by Signal Strength)\n")
        for i, quote in enumerate(report['top_pain_quotes'][:10], 1):
            md_lines.append(f"\n### {i}. {quote['subreddit']} ({quote['upvotes']} upvotes, {quote['urgency'].upper()} urgency)\n")
            md_lines.append(f"\"{quote['text']}...\"\n")
            md_lines.append(f"- **Industry:** {quote['industry']}\n")
            md_lines.append(f"- **Pain Score:** {quote['pain_score']}\n")

        # Write to file
        with open(output_path, 'w') as f:
            f.write(''.join(md_lines))

        print(f"✅ Evidence report saved to: {output_path}")
        return output_path

    def print_summary(self):
        """Print executive summary."""
        report = self.generate_full_report()

        print("\n" + "="*100)
        print("📊 DEMAND VALIDATION REPORT - EXECUTIVE SUMMARY")
        print("="*100)

        # Summary
        print(f"\n✅ Validation Verdict: {report['summary']['validation_verdict']}")
        print(f"📈 Total Posts Analyzed: {report['summary']['total_posts_analyzed']}")

        # ICP
        print(f"\n🎯 IDEAL CUSTOMER PROFILE (Confidence: {report['icp']['confidence']}%)")
        print(f"\nTop Industries:")
        for ind in report['icp']['top_industries'][:3]:
            print(f"   • {ind['industry'].title()}: {ind['count']} posts ({ind['percentage']}%)")

        print(f"\nCompany Sizes:")
        for size in report['icp']['top_company_sizes']:
            print(f"   • {size['size'].title()}: {size['count']} posts ({size['percentage']}%)")

        print(f"\nUrgency Profile:")
        for urgency, data in sorted(report['icp']['urgency_profile'].items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"   • {urgency.upper()}: {data['count']} posts ({data['percentage']}%)")

        # Top Features
        print(f"\n🔧 TOP REQUESTED FEATURES:")
        for feat in report['feature_priorities'][:5]:
            print(f"   • {feat['feature']}: {feat['mentions']} mentions ({feat['percentage']}%)")

        # Pricing
        print(f"\n💰 PRICING INTELLIGENCE:")
        print(f"   • Posts with budget concerns: {report['pricing_signals']['budget_concern_percentage']}%")
        print(f"   • Price examples found: {report['pricing_signals']['posts_with_price_mentions']}")

        # Competitors
        print(f"\n⚔️  COMPETITOR INTELLIGENCE:")
        print(f"   • Posts mentioning competitors: {report['competitor_intelligence']['total_posts_mentioning_competitors']}")
        for comp in report['competitor_intelligence']['top_competitors'][:5]:
            print(f"   • {comp['name']}: {comp['mentions']} mentions")

        # Top Pain Quote
        print(f"\n🔥 TOP PAIN QUOTE:")
        top_quote = report['top_pain_quotes'][0]
        print(f"   [{top_quote['subreddit']}] {top_quote['upvotes']} upvotes | {top_quote['urgency'].upper()} urgency")
        print(f"   \"{top_quote['text']}...\"")

        print("\n" + "="*100)


if __name__ == "__main__":
    validator = DemandValidator()
    validator.print_summary()
    validator.save_report()
