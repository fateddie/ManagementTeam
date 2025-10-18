#!/usr/bin/env python3
"""
Virality Analyzer - Multi-Model Approach
Combines multiple AI models to predict content virality across social platforms.

Features:
- Sentiment analysis (emotional resonance)
- Engagement prediction (TwHIN-BERT)
- Topic relevance (zero-shot classification)
- Combined virality score (0-100)

Models Used:
- cardiffnlp/twitter-roberta-base-sentiment (sentiment)
- Twitter/twhin-bert-base (engagement)
- facebook/bart-large-mnli (zero-shot topics)

Usage:
    from src.ml.virality_analyzer import ViralityAnalyzer

    analyzer = ViralityAnalyzer()
    result = analyzer.analyze_virality(
        text="Check out our new app! 🚀",
        platform="twitter",
        context={"follower_count": 5000}
    )
"""

import os
import json
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Warning: transformers not installed. Install with: pip install transformers torch")

# Import our custom predictor
try:
    from src.ml.twhin_predictor import TwHINPredictor
    TWHIN_AVAILABLE = True
except ImportError:
    TWHIN_AVAILABLE = False
    print("⚠️  Warning: TwHINPredictor not available")


class ViralityAnalyzer:
    """
    Multi-model virality analysis system

    Combines sentiment, engagement, and topic models to predict
    how likely content is to go viral across social platforms.
    """

    # Model configurations
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
    TOPIC_MODEL = "facebook/bart-large-mnli"

    # Virality thresholds
    THRESHOLDS = {
        "low": 30,
        "medium": 60,
        "high": 80
    }

    # Platform-specific weights
    PLATFORM_WEIGHTS = {
        "twitter": {"sentiment": 0.25, "engagement": 0.50, "topic": 0.25},
        "reddit": {"sentiment": 0.35, "engagement": 0.30, "topic": 0.35},
        "youtube": {"sentiment": 0.20, "engagement": 0.40, "topic": 0.40},
        "linkedin": {"sentiment": 0.30, "engagement": 0.35, "topic": 0.35},
        "default": {"sentiment": 0.30, "engagement": 0.40, "topic": 0.30}
    }

    def __init__(self, device: Optional[str] = None):
        """
        Initialize virality analyzer

        Args:
            device: Device to run on ("cpu", "cuda", "mps"). Auto-detected if None.
        """
        self.device = self._get_device(device)
        self.sentiment_analyzer = None
        self.topic_classifier = None
        self.engagement_predictor = None
        self.cache = {}

        if TRANSFORMERS_AVAILABLE:
            self._load_models()
        else:
            print("⚠️  Transformers not available. Using mock analysis.")

    def _get_device(self, device: Optional[str]) -> str:
        """Determine best available device"""
        if device:
            return device

        if not TRANSFORMERS_AVAILABLE:
            return "cpu"

        import torch
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def _load_models(self):
        """Load all required models"""
        try:
            print("📥 Loading virality analysis models...")

            # 1. Sentiment analyzer (Twitter-trained RoBERTa)
            print(f"  Loading {self.SENTIMENT_MODEL}...")
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model=self.SENTIMENT_MODEL,
                device=0 if self.device == "cuda" else -1
            )

            # 2. Topic classifier (zero-shot)
            print(f"  Loading {self.TOPIC_MODEL}...")
            self.topic_classifier = pipeline(
                "zero-shot-classification",
                model=self.TOPIC_MODEL,
                device=0 if self.device == "cuda" else -1
            )

            # 3. Engagement predictor (TwHIN-BERT)
            if TWHIN_AVAILABLE:
                print("  Loading TwHIN-BERT engagement predictor...")
                self.engagement_predictor = TwHINPredictor(device=self.device)
            else:
                print("  ⚠️  TwHIN predictor not available")

            print("✅ All models loaded successfully")

        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            self.sentiment_analyzer = None
            self.topic_classifier = None
            self.engagement_predictor = None

    def analyze_virality(
        self,
        text: str,
        platform: str = "twitter",
        context: Optional[Dict] = None,
        trending_topics: Optional[List[str]] = None
    ) -> Dict:
        """
        Analyze content virality potential

        Args:
            text: Content to analyze
            platform: Social platform (twitter, reddit, youtube, linkedin)
            context: Optional context (follower_count, time_of_day, etc.)
            trending_topics: Optional list of currently trending topics

        Returns:
            Dict with virality score and detailed analysis
        """
        if not self._models_loaded():
            return self._mock_analysis(text, platform)

        # Check cache
        cache_key = f"virality_{hash(text)}_{platform}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # 1. Sentiment Analysis
            sentiment_result = self._analyze_sentiment(text)
            sentiment_score = self._sentiment_to_score(sentiment_result)

            # 2. Engagement Prediction
            engagement_result = self._predict_engagement(text, context)
            engagement_score = engagement_result.get("engagement_score", 50)

            # 3. Topic Relevance
            topic_result = self._analyze_topics(text, trending_topics)
            topic_score = topic_result.get("relevance_score", 50)

            # 4. Calculate weighted virality score
            weights = self.PLATFORM_WEIGHTS.get(platform, self.PLATFORM_WEIGHTS["default"])
            virality_score = (
                sentiment_score * weights["sentiment"] +
                engagement_score * weights["engagement"] +
                topic_score * weights["topic"]
            )

            # 5. Classify virality level
            level = self._classify_virality(virality_score)

            # 6. Generate recommendations
            recommendations = self._generate_recommendations(
                text, sentiment_result, engagement_result, topic_result
            )

            result = {
                "virality_score": round(virality_score, 2),
                "virality_level": level,
                "platform": platform,
                "components": {
                    "sentiment": {
                        "score": round(sentiment_score, 2),
                        "label": sentiment_result["label"],
                        "confidence": round(sentiment_result["score"], 2),
                        "weight": weights["sentiment"]
                    },
                    "engagement": {
                        "score": round(engagement_score, 2),
                        "level": engagement_result.get("engagement_level", "medium"),
                        "weight": weights["engagement"]
                    },
                    "topic": {
                        "score": round(topic_score, 2),
                        "top_topic": topic_result.get("top_topic", "general"),
                        "weight": weights["topic"]
                    }
                },
                "predictions": {
                    "probability_viral": round(self._calculate_viral_probability(virality_score), 2),
                    "expected_reach_multiplier": round(virality_score / 25, 2),
                    "time_to_peak_hours": self._estimate_time_to_peak(virality_score)
                },
                "recommendations": recommendations,
                "timestamp": self._get_timestamp()
            }

            self.cache[cache_key] = result
            return result

        except Exception as e:
            print(f"❌ Error analyzing virality: {e}")
            return self._mock_analysis(text, platform)

    def _models_loaded(self) -> bool:
        """Check if models are loaded"""
        return (
            self.sentiment_analyzer is not None or
            self.topic_classifier is not None or
            self.engagement_predictor is not None
        )

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using Twitter-trained RoBERTa"""
        if not self.sentiment_analyzer:
            # Fallback: simple heuristic
            return self._simple_sentiment(text)

        try:
            result = self.sentiment_analyzer(text[:512])[0]  # Limit length
            return result
        except Exception as e:
            print(f"⚠️  Sentiment analysis error: {e}")
            return self._simple_sentiment(text)

    def _sentiment_to_score(self, sentiment: Dict) -> float:
        """Convert sentiment to 0-100 score"""
        label = sentiment.get("label", "NEUTRAL").upper()
        confidence = sentiment.get("score", 0.5)

        if "POSITIVE" in label:
            # Positive sentiment: 70-100 based on confidence
            return 70 + (confidence * 30)
        elif "NEGATIVE" in label:
            # Negative sentiment can still go viral (controversy)
            # But generally lower: 40-60
            return 40 + (confidence * 20)
        else:
            # Neutral: 50-70
            return 50 + (confidence * 20)

    def _simple_sentiment(self, text: str) -> Dict:
        """Simple sentiment fallback"""
        text_lower = text.lower()

        positive_words = ['great', 'amazing', 'awesome', 'love', 'best', 'excellent', '🚀', '🔥', '💯']
        negative_words = ['bad', 'terrible', 'worst', 'hate', 'awful', 'disappointed']

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return {"label": "POSITIVE", "score": 0.7}
        elif neg_count > pos_count:
            return {"label": "NEGATIVE", "score": 0.6}
        else:
            return {"label": "NEUTRAL", "score": 0.5}

    def _predict_engagement(self, text: str, context: Optional[Dict]) -> Dict:
        """Predict engagement using TwHIN-BERT"""
        if self.engagement_predictor:
            return self.engagement_predictor.predict_engagement(text, context)
        else:
            # Fallback score
            return {"engagement_score": 50, "engagement_level": "medium"}

    def _analyze_topics(self, text: str, trending_topics: Optional[List[str]]) -> Dict:
        """Analyze topic relevance using zero-shot classification"""
        # Default trending topics if none provided
        if not trending_topics:
            trending_topics = [
                "technology", "business", "entertainment", "sports",
                "news", "lifestyle", "education", "health"
            ]

        if not self.topic_classifier:
            return {"relevance_score": 50, "top_topic": "general"}

        try:
            result = self.topic_classifier(text[:512], candidate_labels=trending_topics)

            top_topic = result["labels"][0]
            top_score = result["scores"][0]

            # Convert to 0-100 score
            relevance_score = top_score * 100

            return {
                "relevance_score": relevance_score,
                "top_topic": top_topic,
                "all_topics": list(zip(result["labels"], result["scores"]))
            }

        except Exception as e:
            print(f"⚠️  Topic analysis error: {e}")
            return {"relevance_score": 50, "top_topic": "general"}

    def _classify_virality(self, score: float) -> str:
        """Classify virality level"""
        if score >= self.THRESHOLDS["high"]:
            return "high"
        elif score >= self.THRESHOLDS["medium"]:
            return "medium"
        else:
            return "low"

    def _calculate_viral_probability(self, score: float) -> float:
        """Calculate probability of going viral (0-100%)"""
        # Sigmoid-like function
        prob = 100 / (1 + np.exp(-(score - 60) / 15))
        return prob

    def _estimate_time_to_peak(self, score: float) -> int:
        """Estimate hours to reach peak virality"""
        if score >= 80:
            return 2  # High virality: peaks quickly
        elif score >= 60:
            return 6  # Medium: moderate growth
        else:
            return 12  # Low: slow growth

    def _generate_recommendations(
        self,
        text: str,
        sentiment: Dict,
        engagement: Dict,
        topic: Dict
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Sentiment recommendations
        if sentiment.get("label") == "NEUTRAL":
            recommendations.append("Add more emotional language to increase engagement")

        # Engagement recommendations
        features = engagement.get("content_features", {})

        if features.get("hashtag_count", 0) == 0:
            recommendations.append("Add 1-3 relevant hashtags to increase discoverability")
        elif features.get("hashtag_count", 0) > 5:
            recommendations.append("Reduce hashtag count to 2-3 for better engagement")

        if not features.get("emoji_count"):
            recommendations.append("Add emojis (🚀, 🔥, 💯) to boost visual appeal")

        if not features.get("has_question") and not features.get("has_exclamation"):
            recommendations.append("Add a question or call-to-action to drive interaction")

        # Topic recommendations
        if topic.get("relevance_score", 0) < 60:
            recommendations.append(f"Align content more with trending topic: {topic.get('top_topic')}")

        # Length recommendations
        text_length = len(text)
        if text_length < 50:
            recommendations.append("Add more context (optimal: 50-280 characters)")
        elif text_length > 280:
            recommendations.append("Shorten message for better engagement (optimal: 50-280 chars)")

        return recommendations

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    def batch_analyze(
        self,
        texts: List[str],
        platform: str = "twitter",
        contexts: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """Analyze multiple texts for virality"""
        results = []
        contexts = contexts or [None] * len(texts)

        for text, context in zip(texts, contexts):
            result = self.analyze_virality(text, platform, context)
            results.append(result)

        return results

    def compare_variants(self, variants: List[str], platform: str = "twitter") -> Dict:
        """Compare virality of multiple content variants"""
        analyses = self.batch_analyze(variants, platform)

        # Rank by virality score
        ranked = sorted(
            zip(variants, analyses),
            key=lambda x: x[1]["virality_score"],
            reverse=True
        )

        return {
            "total_variants": len(variants),
            "platform": platform,
            "best_variant": {
                "text": ranked[0][0],
                "score": ranked[0][1]["virality_score"],
                "level": ranked[0][1]["virality_level"]
            },
            "rankings": [
                {
                    "rank": i + 1,
                    "text": text,
                    "score": analysis["virality_score"],
                    "level": analysis["virality_level"],
                    "top_recommendations": analysis["recommendations"][:2]
                }
                for i, (text, analysis) in enumerate(ranked)
            ]
        }

    # ==============================================
    # Mock Analysis (when models unavailable)
    # ==============================================

    def _mock_analysis(self, text: str, platform: str) -> Dict:
        """Generate mock analysis for testing"""
        print("📦 Using mock virality analysis")

        score = 55.0  # Base score
        text_lower = text.lower()

        # Simple heuristics
        if any(emoji in text for emoji in ['🚀', '🔥', '💯']):
            score += 10

        if '?' in text or '!' in text:
            score += 8

        hashtag_count = text.count('#')
        if 1 <= hashtag_count <= 3:
            score += 7

        score = min(score, 100.0)
        level = self._classify_virality(score)

        return {
            "virality_score": round(score, 2),
            "virality_level": level,
            "platform": platform,
            "components": {
                "sentiment": {"score": 65, "label": "POSITIVE", "weight": 0.3},
                "engagement": {"score": 60, "level": "medium", "weight": 0.4},
                "topic": {"score": 50, "top_topic": "general", "weight": 0.3}
            },
            "predictions": {
                "probability_viral": round(self._calculate_viral_probability(score), 2),
                "expected_reach_multiplier": round(score / 25, 2),
                "time_to_peak_hours": self._estimate_time_to_peak(score)
            },
            "recommendations": [
                "Add more emotional language",
                "Include 2-3 relevant hashtags",
                "Add emojis for visual appeal"
            ],
            "mock_data": True,
            "timestamp": self._get_timestamp()
        }


# ==============================================
# Example Usage / Testing
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔥 Virality Analyzer - Test Suite")
    print("=" * 70 + "\n")

    analyzer = ViralityAnalyzer()

    # Test posts
    test_posts = [
        "Just launched our new productivity app! 🚀 Check it out #productivity #SaaS",
        "Another day at work...",
        "🔥 This is HUGE! You won't believe what we built. Link in bio! #gamechangerReact",
        "What's your biggest productivity challenge? Let's discuss! 💬 #AskTwitter"
    ]

    print("Test 1: Analyzing individual posts\n")
    for i, post in enumerate(test_posts, 1):
        result = analyzer.analyze_virality(post, platform="twitter")
        print(f"Post {i}: {post[:50]}...")
        print(f"  Virality Score: {result['virality_score']}/100 ({result['virality_level']})")
        print(f"  Viral Probability: {result['predictions']['probability_viral']}%")
        print(f"  Sentiment: {result['components']['sentiment']['label']} ({result['components']['sentiment']['score']})")
        print(f"  Top Recommendation: {result['recommendations'][0] if result['recommendations'] else 'None'}")
        print()

    print("\n" + "-" * 70 + "\n")
    print("Test 2: Comparing content variants\n")

    variants = [
        "New feature: Dark mode",
        "🌙 Dark mode is live! Switch to the dark side 😎 #DarkMode",
        "Just shipped dark mode. What do you think?"
    ]

    comparison = analyzer.compare_variants(variants, platform="twitter")
    print(f"Best variant (score: {comparison['best_variant']['score']}):")
    print(f"  \"{comparison['best_variant']['text']}\"")
    print(f"\nAll variants:")
    for variant in comparison['rankings']:
        print(f"  {variant['rank']}. Score {variant['score']}: {variant['text'][:60]}...")

    print("\n" + "=" * 70)
    print("✅ All tests complete!")
    print("=" * 70 + "\n")
