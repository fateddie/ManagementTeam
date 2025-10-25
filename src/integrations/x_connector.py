#!/usr/bin/env python3
"""
X (Twitter) API Connector
Collects social signals and sentiment from X for market validation.

Features:
- Search tweets related to topics
- Sentiment analysis of mentions
- Influencer identification
- Trending topics analysis
- Competitor mention tracking

Usage:
    from src.integrations.x_connector import XConnector

    x_api = XConnector()
    results = x_api.search_sentiment("productivity app", limit=100)
"""

import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("⚠️  Warning: tweepy not installed. Install with: pip install tweepy")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from src.utils.config_loader import load_env, get_env
    CONFIG_LOADER_AVAILABLE = True
except ImportError:
    CONFIG_LOADER_AVAILABLE = False
    print("⚠️  Warning: config_loader not available. Using os.getenv fallback")


class XConnector:
    """Connect to X (Twitter) API for social signal analysis"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize X connector

        Args:
            config_path: Path to config file with X API credentials
        """
        self.config = self._load_config(config_path)
        self.client = None
        self.cache = {}

        if TWEEPY_AVAILABLE and self._has_credentials():
            self._init_x_client()
        else:
            print("⚠️  X API not configured. Using mock mode.")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or environment"""
        # Load environment variables from config/.env
        if CONFIG_LOADER_AVAILABLE:
            load_env()
            config = {
                "bearer_token": get_env("X_BEARER_TOKEN"),
                "api_key": get_env("X_API_KEY"),
                "api_secret": get_env("X_API_SECRET"),
                "access_token": get_env("X_ACCESS_TOKEN"),
                "access_token_secret": get_env("X_ACCESS_TOKEN_SECRET")
            }
        else:
            # Fallback to os.getenv
            config = {
                "bearer_token": os.getenv("X_BEARER_TOKEN"),
                "api_key": os.getenv("X_API_KEY"),
                "api_secret": os.getenv("X_API_SECRET"),
                "access_token": os.getenv("X_ACCESS_TOKEN"),
                "access_token_secret": os.getenv("X_ACCESS_TOKEN_SECRET")
            }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config.get("x", {}))

        return config

    def _has_credentials(self) -> bool:
        """Check if X API credentials are configured"""
        # Can use either OAuth 2.0 (bearer token) or OAuth 1.0a
        has_bearer = bool(self.config.get("bearer_token"))
        has_oauth1 = all([
            self.config.get("api_key"),
            self.config.get("api_secret"),
            self.config.get("access_token"),
            self.config.get("access_token_secret")
        ])
        return has_bearer or has_oauth1

    def _init_x_client(self):
        """Initialize Tweepy client"""
        try:
            if self.config.get("bearer_token"):
                # OAuth 2.0 Bearer Token (recommended for v2 API)
                self.client = tweepy.Client(bearer_token=self.config["bearer_token"])
            else:
                # OAuth 1.0a
                auth = tweepy.OAuth1UserHandler(
                    self.config["api_key"],
                    self.config["api_secret"],
                    self.config["access_token"],
                    self.config["access_token_secret"]
                )
                api = tweepy.API(auth)
                self.client = tweepy.Client(
                    consumer_key=self.config["api_key"],
                    consumer_secret=self.config["api_secret"],
                    access_token=self.config["access_token"],
                    access_token_secret=self.config["access_token_secret"]
                )

            print("✅ X API connected")
        except Exception as e:
            print(f"❌ Failed to connect to X API: {e}")
            self.client = None

    def search_sentiment(
        self,
        query: str,
        limit: int = 100,
        language: str = "en"
    ) -> Dict:
        """
        Search X for tweets and analyze sentiment

        Args:
            query: Search query
            limit: Maximum number of tweets
            language: Language filter

        Returns:
            Dict with tweets, sentiment analysis, and insights
        """
        if not self.client:
            return self._mock_search_results(query)

        print(f"\n🐦 Searching X for: '{query}'")

        try:
            # Search recent tweets
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=min(limit, 100),  # API limit
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                expansions=['author_id'],
                user_fields=['username', 'public_metrics']
            )

            if not tweets.data:
                print("  No tweets found")
                return self._mock_search_results(query)

            # Process tweets
            processed_tweets = []
            for tweet in tweets.data:
                # Get author info
                author = self._get_author_info(tweet.author_id, tweets.includes)

                # Analyze sentiment
                sentiment = self._analyze_sentiment(tweet.text)

                processed_tweets.append({
                    "id": tweet.id,
                    "text": tweet.text,
                    "created_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "author": author,
                    "metrics": {
                        "likes": tweet.public_metrics.get('like_count', 0),
                        "retweets": tweet.public_metrics.get('retweet_count', 0),
                        "replies": tweet.public_metrics.get('reply_count', 0),
                        "engagement": (
                            tweet.public_metrics.get('like_count', 0) +
                            tweet.public_metrics.get('retweet_count', 0) * 2 +
                            tweet.public_metrics.get('reply_count', 0)
                        )
                    },
                    "sentiment": sentiment,
                    "url": f"https://twitter.com/i/web/status/{tweet.id}"
                })

            # Aggregate sentiment
            sentiment_summary = self._aggregate_sentiment(processed_tweets)

            # Find influential mentions
            top_tweets = sorted(
                processed_tweets,
                key=lambda x: x['metrics']['engagement'],
                reverse=True
            )[:10]

            results = {
                "query": query,
                "total_tweets": len(processed_tweets),
                "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "tweets": processed_tweets[:20],  # Top 20 for storage
                "top_influential_tweets": top_tweets,
                "sentiment_summary": sentiment_summary,
                "insights": self._generate_insights(processed_tweets, sentiment_summary)
            }

            print(f"✅ Analyzed {len(processed_tweets)} tweets")
            return results

        except Exception as e:
            print(f"❌ Error searching X: {e}")
            return self._mock_search_results(query)

    def _get_author_info(self, author_id, includes) -> Dict:
        """Extract author information from includes"""
        if not includes or 'users' not in includes:
            return {"username": "unknown", "followers": 0}

        for user in includes['users']:
            if user.id == author_id:
                return {
                    "username": user.username,
                    "followers": user.public_metrics.get('followers_count', 0),
                    "verified": getattr(user, 'verified', False)
                }

        return {"username": "unknown", "followers": 0}

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of tweet"""
        if not TEXTBLOB_AVAILABLE:
            return {"polarity": 0, "subjectivity": 0, "label": "neutral"}

        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            label = "neutral"
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"

            return {
                "polarity": round(polarity, 2),
                "subjectivity": round(subjectivity, 2),
                "label": label
            }
        except:
            return {"polarity": 0, "subjectivity": 0, "label": "neutral"}

    def _aggregate_sentiment(self, tweets: List[Dict]) -> Dict:
        """Aggregate sentiment across all tweets"""
        if not tweets:
            return {}

        polarities = [t['sentiment']['polarity'] for t in tweets]
        avg_polarity = sum(polarities) / len(polarities)

        distribution = {
            "positive": sum(1 for p in polarities if p > 0.1) / len(polarities),
            "neutral": sum(1 for p in polarities if -0.1 <= p <= 0.1) / len(polarities),
            "negative": sum(1 for p in polarities if p < -0.1) / len(polarities)
        }

        # Calculate weighted sentiment (considering engagement)
        weighted_sentiment = sum(
            t['sentiment']['polarity'] * t['metrics']['engagement']
            for t in tweets
        ) / sum(t['metrics']['engagement'] for t in tweets if t['metrics']['engagement'] > 0)

        return {
            "avg_polarity": round(avg_polarity, 2),
            "weighted_polarity": round(weighted_sentiment, 2) if weighted_sentiment else 0,
            "distribution": {k: round(v * 100, 1) for k, v in distribution.items()},
            "sentiment_label": "negative" if avg_polarity < -0.1 else "neutral" if avg_polarity < 0.1 else "positive",
            "total_engagement": sum(t['metrics']['engagement'] for t in tweets)
        }

    def _generate_insights(self, tweets: List[Dict], sentiment_summary: Dict) -> Dict:
        """Generate insights from tweet analysis"""
        if not tweets:
            return {}

        # Top influencers
        influencers = sorted(
            tweets,
            key=lambda x: x['author']['followers'],
            reverse=True
        )[:5]

        # Extract pain points and opportunities
        pain_points = []
        opportunities = []

        for tweet in tweets:
            text_lower = tweet['text'].lower()
            if tweet['sentiment']['label'] == 'negative':
                if any(word in text_lower for word in ['problem', 'issue', 'hate', 'terrible']):
                    pain_points.append(tweet['text'])
            elif tweet['sentiment']['label'] == 'positive':
                if any(word in text_lower for word in ['love', 'great', 'amazing', 'perfect']):
                    opportunities.append(tweet['text'])

        return {
            "social_proof": "strong" if len(tweets) > 50 else "moderate" if len(tweets) > 20 else "weak",
            "sentiment_signal": sentiment_summary.get('sentiment_label', 'neutral'),
            "engagement_level": "high" if sentiment_summary.get('total_engagement', 0) > 1000 else "medium" if sentiment_summary.get('total_engagement', 0) > 100 else "low",
            "top_influencers": [{"username": i['author']['username'], "followers": i['author']['followers']} for i in influencers],
            "pain_points_sample": pain_points[:3],
            "opportunities_sample": opportunities[:3],
            "recommendation": self._generate_recommendation(sentiment_summary, len(tweets))
        }

    def _generate_recommendation(self, sentiment: Dict, tweet_count: int) -> str:
        """Generate recommendation based on analysis"""
        sentiment_label = sentiment.get('sentiment_label', 'neutral')
        distribution = sentiment.get('distribution', {})

        if sentiment_label == 'positive' and tweet_count > 50:
            return "Strong positive social signal - high market interest"
        elif sentiment_label == 'negative' and distribution.get('negative', 0) > 50:
            return "Negative sentiment detected - investigate pain points carefully"
        elif tweet_count < 20:
            return "Low social visibility - market validation needed"
        else:
            return "Mixed sentiment - requires deeper analysis"

    def track_competitor_mentions(
        self,
        competitor_name: str,
        limit: int = 100
    ) -> Dict:
        """Track mentions of competitors"""
        query = f'"{competitor_name}" OR @{competitor_name}'
        results = self.search_sentiment(query, limit=limit)

        results['competitor'] = competitor_name
        results['mention_count'] = results['total_tweets']

        return results

    def get_trending_topics(
        self,
        location_id: int = 1  # 1 = Worldwide
    ) -> List[Dict]:
        """Get trending topics (requires elevated access)"""
        if not self.client:
            return []

        print("⚠️  Trending topics requires X API elevated access")
        return []

    def _mock_search_results(self, query: str) -> Dict:
        """Return mock results when API is not configured"""
        return {
            "query": query,
            "total_tweets": 0,
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "tweets": [],
            "top_influential_tweets": [],
            "sentiment_summary": {},
            "insights": {},
            "note": "Mock data - X API not configured"
        }


if __name__ == "__main__":
    # Test the connector
    x_api = XConnector()

    # Example search
    results = x_api.search_sentiment("productivity app", limit=50)

    print(f"\n📊 Results:")
    print(f"Total tweets: {results['total_tweets']}")

    if results.get('sentiment_summary'):
        print(f"\n💭 Sentiment Summary:")
        summary = results['sentiment_summary']
        print(f"  Average polarity: {summary.get('avg_polarity')}")
        print(f"  Sentiment: {summary.get('sentiment_label')}")
        print(f"  Distribution: {summary.get('distribution')}")

    if results.get('insights'):
        print(f"\n💡 Insights:")
        insights = results['insights']
        print(f"  Social proof: {insights.get('social_proof')}")
        print(f"  Recommendation: {insights.get('recommendation')}")
