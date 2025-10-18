"""
trend_research_agent.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trend Research Agent - Social Media Trending & Pain Point Discovery

Purpose:
    Discovers trending topics, viral content patterns, and customer pain
    points across social media platforms (YouTube, Reddit, X, LinkedIn).

    Uses AI models (TwHIN-BERT, BERTopic, sentiment analysis) to:
    - Identify viral content and trending topics
    - Extract customer pain points and problems
    - Analyze market demand and opportunities
    - Generate product ideas from social insights

Inherits from: BaseAgent
Dependencies: None (research/discovery stage, runs first)

Location: agents/trend_research_agent/trend_research_agent.py

Created: 2025-10-17
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import yaml
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone

# Import BaseAgent
from core.base_agent import BaseAgent, AgentContext
from core.agent_protocol import AgentOutput

# Import connectors
from src.integrations.youtube_connector import YouTubeConnector
from src.integrations.reddit_connector import RedditConnector
from src.integrations.x_connector import XConnector
from src.integrations.evidence_collector import EvidenceCollector

# Import AI models
from src.ml.twhin_predictor import TwHINPredictor
from src.ml.virality_analyzer import ViralityAnalyzer
from src.ml.pain_point_extractor import PainPointExtractor
from src.ml.topic_clustering import TopicClusterer


class TrendResearchAgent(BaseAgent):
    """
    Trend Research Agent - Discover trending topics and pain points

    Responsibilities:
    - Collect data from YouTube, Reddit, X (Twitter)
    - Analyze viral content patterns
    - Extract customer pain points
    - Discover trending topics with BERTopic
    - Generate market opportunity insights

    Output:
    - Trending topics across platforms
    - Viral content analysis
    - Pain point clusters
    - Product opportunity recommendations
    """

    @property
    def name(self) -> str:
        """Agent name for registry"""
        return "TrendResearchAgent"

    @property
    def dependencies(self) -> List[str]:
        """No dependencies - runs first for research"""
        return []

    def validate_inputs(self, context: AgentContext) -> bool:
        """
        Validate inputs before execution

        Args:
            context: Execution context with inputs

        Returns:
            True if inputs are valid
        """
        # Check for required inputs
        required_keys = ["research_query", "platforms"]

        for key in required_keys:
            if key not in context.inputs:
                print(f"❌ Missing required input: {key}")
                return False

        # Validate platforms
        valid_platforms = ["youtube", "reddit", "twitter", "linkedin"]
        platforms = context.inputs.get("platforms", [])

        if not platforms:
            print("❌ No platforms specified")
            return False

        for platform in platforms:
            if platform not in valid_platforms:
                print(f"⚠️  Unknown platform: {platform}")

        return True

    def execute(self, context: AgentContext) -> AgentOutput:
        """
        Main execution - discover trends and pain points

        Args:
            context: Shared execution context

        Returns:
            AgentOutput with trending data and recommendations
        """
        print(f"\n{'=' * 70}")
        print(f"🔍 {self.name} - Starting Trend Research")
        print(f"{'=' * 70}\n")

        # Extract inputs
        research_query = context.inputs.get("research_query", "")
        platforms = context.inputs.get("platforms", [])
        max_results = context.inputs.get("max_results", 50)
        config_path = context.inputs.get("config_path")

        print(f"Research Query: {research_query}")
        print(f"Platforms: {', '.join(platforms)}")
        print(f"Max Results: {max_results}\n")

        # Initialize connectors and AI models
        print("📥 Loading connectors and AI models...\n")
        connectors = self._init_connectors(config_path)
        ai_models = self._init_ai_models()

        # Collect data from platforms
        print(f"\n{'─' * 70}")
        print("📊 Phase 1: Data Collection")
        print(f"{'─' * 70}\n")

        all_data = self._collect_data(
            research_query, platforms, max_results, connectors
        )

        # Analyze viral patterns
        print(f"\n{'─' * 70}")
        print("🔥 Phase 2: Viral Pattern Analysis")
        print(f"{'─' * 70}\n")

        viral_analysis = self._analyze_virality(all_data, ai_models)

        # Extract pain points
        print(f"\n{'─' * 70}")
        print("💬 Phase 3: Pain Point Extraction")
        print(f"{'─' * 70}\n")

        pain_points = self._extract_pain_points(all_data, ai_models)

        # Discover topics
        print(f"\n{'─' * 70}")
        print("🔬 Phase 4: Topic Discovery")
        print(f"{'─' * 70}\n")

        topics = self._discover_topics(all_data, ai_models)

        # Generate recommendations
        print(f"\n{'─' * 70}")
        print("💡 Phase 5: Generating Recommendations")
        print(f"{'─' * 70}\n")

        recommendations = self._generate_recommendations(
            research_query, viral_analysis, pain_points, topics
        )

        # Calculate confidence score
        confidence = self._calculate_confidence(all_data, pain_points, topics)

        # Prepare output data
        output_data = {
            "research_query": research_query,
            "platforms_analyzed": platforms,
            "data_collected": {
                "total_items": sum(data["count"] for data in all_data.values()),
                "by_platform": {
                    platform: data["count"]
                    for platform, data in all_data.items()
                }
            },
            "viral_analysis": viral_analysis,
            "pain_points": pain_points,
            "topics": topics,
            "recommendations": recommendations,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        # Save detailed report
        self._save_report(output_data, context.session_id)

        # Generate summary
        summary = self._generate_summary(output_data)

        print(f"\n{'=' * 70}")
        print(f"✅ {self.name} - Research Complete")
        print(f"{'=' * 70}\n")

        # Return AgentOutput
        return AgentOutput(
            agent_name=self.name,
            decision="approve",  # Always approve for research
            reasoning=summary,
            data_for_next_agent=output_data,
            confidence=confidence
        )

    def _init_connectors(self, config_path: str = None) -> Dict:
        """Initialize platform connectors"""
        return {
            "youtube": YouTubeConnector(config_path),
            "reddit": RedditConnector(config_path),
            "x": XConnector(config_path)
        }

    def _init_ai_models(self) -> Dict:
        """Initialize AI analysis models"""
        print("  Loading TwHIN-BERT predictor...")
        print("  Loading virality analyzer...")
        print("  Loading pain point extractor...")
        print("  Loading topic clusterer...")

        return {
            "engagement": TwHINPredictor(),
            "virality": ViralityAnalyzer(),
            "pain_extractor": PainPointExtractor(),
            "topic_clusterer": TopicClusterer()
        }

    def _collect_data(
        self,
        query: str,
        platforms: List[str],
        max_results: int,
        connectors: Dict
    ) -> Dict:
        """Collect data from specified platforms"""
        all_data = {}

        # YouTube
        if "youtube" in platforms:
            print("  📺 YouTube: Fetching trending videos...")
            youtube_data = connectors["youtube"].get_trending_videos(
                region_code="US",
                max_results=max_results
            )
            all_data["youtube"] = {
                "count": youtube_data.get("total_videos", 0),
                "items": youtube_data.get("videos", [])
            }
            print(f"    ✅ Collected {all_data['youtube']['count']} videos\n")

        # Reddit
        if "reddit" in platforms:
            print("  🔴 Reddit: Searching for discussions...")
            reddit_data = connectors["reddit"].search_pain_points(
                query,
                subreddits=["productivity", "SaaS", "Entrepreneur"],
                limit=max_results
            )
            all_data["reddit"] = {
                "count": reddit_data.get("total_posts", 0),
                "items": reddit_data.get("posts", []),
                "pain_points": reddit_data.get("pain_points", [])
            }
            print(f"    ✅ Collected {all_data['reddit']['count']} posts\n")

        # X (Twitter)
        if "twitter" in platforms or "x" in platforms:
            print("  🐦 X (Twitter): Searching tweets...")
            x_data = connectors["x"].search_sentiment(
                query,
                limit=max_results
            )
            all_data["twitter"] = {
                "count": x_data.get("total_tweets", 0),
                "items": x_data.get("tweets", [])
            }
            print(f"    ✅ Collected {all_data['twitter']['count']} tweets\n")

        return all_data

    def _analyze_virality(self, all_data: Dict, ai_models: Dict) -> Dict:
        """Analyze viral patterns across platforms"""
        virality_analyzer = ai_models["virality"]

        # Collect text for analysis
        all_texts = []
        for platform, data in all_data.items():
            for item in data.get("items", [])[:20]:  # Limit for performance
                if platform == "youtube":
                    all_texts.append(item.get("title", ""))
                elif platform == "reddit":
                    all_texts.append(item.get("title", "") + " " + item.get("selftext", ""))
                elif platform == "twitter":
                    all_texts.append(item.get("text", ""))

        if not all_texts:
            return {"error": "No content to analyze"}

        # Analyze virality
        print(f"  Analyzing {len(all_texts)} content items...")
        analyses = virality_analyzer.batch_analyze(all_texts[:50])  # Limit batch size

        # Aggregate results
        avg_score = sum(a["virality_score"] for a in analyses) / len(analyses) if analyses else 0

        high_viral = [a for a in analyses if a["virality_level"] == "high"]
        medium_viral = [a for a in analyses if a["virality_level"] == "medium"]

        print(f"  ✅ Average virality score: {avg_score:.1f}/100")
        print(f"  ✅ High virality content: {len(high_viral)} items")

        return {
            "average_virality_score": round(avg_score, 1),
            "high_viral_count": len(high_viral),
            "medium_viral_count": len(medium_viral),
            "top_viral_content": analyses[:10],  # Top 10
            "viral_patterns": self._extract_viral_patterns(analyses)
        }

    def _extract_viral_patterns(self, analyses: List[Dict]) -> Dict:
        """Extract patterns from viral content"""
        # Collect recommendations from all analyses
        all_recommendations = []
        for analysis in analyses:
            all_recommendations.extend(analysis.get("recommendations", []))

        # Count frequency
        from collections import Counter
        rec_freq = Counter(all_recommendations)

        return {
            "common_recommendations": rec_freq.most_common(10),
            "avg_sentiment_score": round(
                sum(a["components"]["sentiment"]["score"] for a in analyses) / len(analyses), 1
            ) if analyses else 0
        }

    def _extract_pain_points(self, all_data: Dict, ai_models: Dict) -> Dict:
        """Extract customer pain points from collected data"""
        pain_extractor = ai_models["pain_extractor"]

        # Collect text for pain point extraction
        all_texts = []
        for platform, data in all_data.items():
            # Reddit already has pain points extracted
            if platform == "reddit" and "pain_points" in data:
                continue

            for item in data.get("items", [])[:50]:  # Limit
                if platform == "youtube":
                    text = item.get("description", "")
                elif platform == "twitter":
                    text = item.get("text", "")
                else:
                    text = item.get("title", "") + " " + item.get("selftext", "")

                if text:
                    all_texts.append(text)

        if not all_texts:
            return {"error": "No content for pain point extraction"}

        # Extract pain points
        print(f"  Extracting pain points from {len(all_texts)} items...")
        results = pain_extractor.batch_extract(all_texts[:100])  # Limit batch

        # Aggregate
        aggregated = pain_extractor.aggregate_pain_points(results)

        print(f"  ✅ Pain points found in {aggregated['texts_with_pain_points']} items ({aggregated['pain_point_percentage']}%)")
        print(f"  ✅ Average severity: {aggregated['average_severity']}/10")

        # Get top pain keywords
        top_keywords = [kw for kw, count in aggregated['top_pain_keywords'][:10]]
        if top_keywords:
            print(f"  ✅ Top pain keywords: {', '.join(top_keywords[:5])}")

        return aggregated

    def _discover_topics(self, all_data: Dict, ai_models: Dict) -> Dict:
        """Discover trending topics using BERTopic"""
        topic_clusterer = ai_models["topic_clusterer"]

        # Collect documents
        documents = []
        for platform, data in all_data.items():
            for item in data.get("items", []):
                if platform == "youtube":
                    doc = item.get("title", "") + " " + item.get("description", "")
                elif platform == "reddit":
                    doc = item.get("title", "") + " " + item.get("selftext", "")
                elif platform == "twitter":
                    doc = item.get("text", "")
                else:
                    continue

                if doc.strip():
                    documents.append(doc)

        if len(documents) < 10:
            print("  ⚠️  Not enough documents for topic modeling")
            return {"error": "Insufficient data", "topics": []}

        # Discover topics
        print(f"  Discovering topics from {len(documents)} documents...")
        topics_result = topic_clusterer.discover_topics(documents, min_topic_size=5)

        if "error" in topics_result:
            print(f"  ⚠️  {topics_result['error']}")
        else:
            print(f"  ✅ Discovered {topics_result['num_topics']} topics")

        return topics_result

    def _generate_recommendations(
        self,
        query: str,
        viral_analysis: Dict,
        pain_points: Dict,
        topics: Dict
    ) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []

        # Recommendation 1: Product opportunities from pain points
        if pain_points.get("top_pain_keywords"):
            top_pains = [kw for kw, count in pain_points["top_pain_keywords"][:5]]
            recommendations.append({
                "type": "product_opportunity",
                "priority": "high",
                "title": "Address Top Customer Pain Points",
                "description": f"Build solutions targeting: {', '.join(top_pains)}",
                "evidence": {
                    "pain_point_percentage": pain_points.get("pain_point_percentage", 0),
                    "average_severity": pain_points.get("average_severity", 0)
                }
            })

        # Recommendation 2: Viral content strategy
        if viral_analysis.get("viral_patterns"):
            common_recs = viral_analysis["viral_patterns"].get("common_recommendations", [])
            if common_recs:
                top_rec = common_recs[0][0] if common_recs else "Optimize content"
                recommendations.append({
                    "type": "content_strategy",
                    "priority": "medium",
                    "title": "Optimize Content for Virality",
                    "description": top_rec,
                    "evidence": {
                        "avg_virality_score": viral_analysis.get("average_virality_score", 0),
                        "high_viral_count": viral_analysis.get("high_viral_count", 0)
                    }
                })

        # Recommendation 3: Trending topic alignment
        if topics.get("topics"):
            top_topic = topics["topics"][0] if topics["topics"] else None
            if top_topic:
                recommendations.append({
                    "type": "market_trend",
                    "priority": "high",
                    "title": f"Align with Trending Topic: {top_topic['label']}",
                    "description": f"Focus on {', '.join(top_topic['keywords'][:5])}",
                    "evidence": {
                        "topic_size": top_topic["size"],
                        "keywords": top_topic["keywords"][:10]
                    }
                })

        return recommendations

    def _calculate_confidence(
        self,
        all_data: Dict,
        pain_points: Dict,
        topics: Dict
    ) -> float:
        """Calculate confidence in research findings"""
        confidence = 0.5  # Base

        # Boost for data volume
        total_items = sum(data["count"] for data in all_data.values())
        if total_items > 100:
            confidence += 0.2
        elif total_items > 50:
            confidence += 0.1

        # Boost for pain point detection
        if pain_points.get("pain_point_percentage", 0) > 30:
            confidence += 0.15

        # Boost for topic discovery
        if topics.get("num_topics", 0) >= 3:
            confidence += 0.15

        return min(confidence, 1.0)

    def _generate_summary(self, output_data: Dict) -> str:
        """Generate human-readable summary"""
        lines = []

        lines.append(f"Research Query: {output_data['research_query']}")
        lines.append(f"Data Collected: {output_data['data_collected']['total_items']} items from {len(output_data['platforms_analyzed'])} platforms")

        # Viral analysis
        viral = output_data["viral_analysis"]
        lines.append(f"Virality Score: {viral.get('average_virality_score', 0)}/100 ({viral.get('high_viral_count', 0)} high-viral items)")

        # Pain points
        pain = output_data["pain_points"]
        lines.append(f"Pain Points: Found in {pain.get('texts_with_pain_points', 0)} items ({pain.get('pain_point_percentage', 0)}%)")

        # Topics
        topics = output_data["topics"]
        lines.append(f"Topics Discovered: {topics.get('num_topics', 0)} distinct topics")

        # Recommendations
        recs = output_data["recommendations"]
        lines.append(f"Recommendations: {len(recs)} actionable insights generated")

        return "\n".join(lines)

    def _save_report(self, output_data: Dict, session_id: str):
        """Save detailed research report"""
        # Save JSON
        output_dir = Path("outputs/trend_research")
        output_dir.mkdir(parents=True, exist_ok=True)

        json_path = output_dir / f"research_{session_id}.json"
        with open(json_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n💾 Report saved: {json_path}")

        # Save Markdown summary
        md_path = output_dir / f"research_{session_id}.md"
        self._save_markdown_report(output_data, md_path)
        print(f"💾 Summary saved: {md_path}")

    def _save_markdown_report(self, data: Dict, path: Path):
        """Generate Markdown report"""
        md_lines = []

        md_lines.append(f"# Trend Research Report")
        md_lines.append(f"\n**Query:** {data['research_query']}")
        md_lines.append(f"**Date:** {data['timestamp']}")
        md_lines.append(f"**Platforms:** {', '.join(data['platforms_analyzed'])}\n")

        md_lines.append(f"## 📊 Data Collection\n")
        md_lines.append(f"- **Total Items:** {data['data_collected']['total_items']}\n")

        md_lines.append(f"## 🔥 Viral Analysis\n")
        viral = data["viral_analysis"]
        md_lines.append(f"- **Average Virality Score:** {viral.get('average_virality_score', 0)}/100")
        md_lines.append(f"- **High Viral Content:** {viral.get('high_viral_count', 0)} items\n")

        md_lines.append(f"## 💬 Pain Points\n")
        pain = data["pain_points"]
        md_lines.append(f"- **Detection Rate:** {pain.get('pain_point_percentage', 0)}%")
        md_lines.append(f"- **Average Severity:** {pain.get('average_severity', 0)}/10")
        if pain.get("top_pain_keywords"):
            md_lines.append(f"\n**Top Pain Keywords:**")
            for kw, count in pain["top_pain_keywords"][:10]:
                md_lines.append(f"- {kw}: {count} mentions")

        md_lines.append(f"\n## 🔬 Topics\n")
        topics = data["topics"]
        md_lines.append(f"- **Topics Discovered:** {topics.get('num_topics', 0)}\n")

        md_lines.append(f"## 💡 Recommendations\n")
        for rec in data["recommendations"]:
            md_lines.append(f"\n### {rec['title']}")
            md_lines.append(f"**Priority:** {rec['priority']}")
            md_lines.append(f"\n{rec['description']}\n")

        with open(path, 'w') as f:
            f.write('\n'.join(md_lines))


# ==============================================
# Example Usage / Testing
# ==============================================
if __name__ == "__main__":
    from core.base_agent import AgentContext

    print("\n" + "=" * 70)
    print("🧪 TrendResearchAgent - Test Suite")
    print("=" * 70 + "\n")

    # Create test context
    context = AgentContext(
        session_id="test_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        inputs={
            "research_query": "productivity app for developers",
            "platforms": ["youtube", "reddit", "twitter"],
            "max_results": 20
        },
        shared_data={}
    )

    # Initialize agent
    agent = TrendResearchAgent()

    # Validate inputs
    print("Test 1: Validating inputs...")
    is_valid = agent.validate_inputs(context)
    print(f"  {'✅' if is_valid else '❌'} Input validation: {is_valid}\n")

    # Execute agent
    print("Test 2: Executing agent...")
    result = agent.execute(context)

    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Decision: {result.decision}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"\nSummary:")
    print(result.reasoning)

    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70 + "\n")
