#!/usr/bin/env python3
"""
Reddit API Connector
Collects evidence from Reddit for market research and pain validation.

Features:
- Search subreddits for relevant discussions
- Extract pain points from posts and comments
- Sentiment analysis of community feedback
- Trend detection in discussions

Usage:
    from src.integrations.reddit_connector import RedditConnector

    reddit = RedditConnector()
    results = reddit.search_pain_points("productivity app", subreddits=["productivity"])
"""

import os
import json
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    print("⚠️  Warning: praw not installed. Install with: pip install praw")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("⚠️  Warning: textblob not installed. Install with: pip install textblob")


class RedditConnector:
    """Connect to Reddit API for market research and pain validation"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Reddit connector

        Args:
            config_path: Path to config file with Reddit credentials
        """
        self.config = self._load_config(config_path)
        self.reddit = None
        self.cache = {}

        if PRAW_AVAILABLE and self._has_credentials():
            self._init_reddit_client()
        else:
            print("⚠️  Reddit API not configured. Using mock mode.")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or environment"""
        config = {
            "client_id": os.getenv("REDDIT_CLIENT_ID"),
            "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
            "user_agent": os.getenv("REDDIT_USER_AGENT", "VES Market Research Bot v1.0")
        }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config.get("reddit", {}))

        return config

    def _has_credentials(self) -> bool:
        """Check if Reddit credentials are configured"""
        return bool(self.config.get("client_id") and self.config.get("client_secret"))

    def _init_reddit_client(self):
        """Initialize PRAW Reddit client"""
        try:
            self.reddit = praw.Reddit(
                client_id=self.config["client_id"],
                client_secret=self.config["client_secret"],
                user_agent=self.config["user_agent"]
            )
            print("✅ Reddit API connected")
        except Exception as e:
            print(f"❌ Failed to connect to Reddit API: {e}")
            self.reddit = None

    def search_pain_points(
        self,
        query: str,
        subreddits: List[str] = None,
        time_filter: str = "month",
        limit: int = 100
    ) -> Dict:
        """
        Search Reddit for pain points related to a topic

        Args:
            query: Search query (e.g., "productivity app problems")
            subreddits: List of subreddits to search (default: popular ones)
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Maximum number of posts to analyze

        Returns:
            Dict with pain points, sentiment analysis, and evidence
        """
        if not self.reddit:
            return self._mock_search_results(query)

        # Default subreddits for common topics
        if not subreddits:
            subreddits = ["productivity", "smallbusiness", "Entrepreneur",
                         "SaaS", "startups", "technology"]

        print(f"\n🔍 Searching Reddit for: '{query}'")
        print(f"📍 Subreddits: {', '.join(subreddits)}")

        all_posts = []
        pain_points = []

        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)

                # Search posts
                for post in subreddit.search(query, time_filter=time_filter, limit=limit):
                    post_data = {
                        "id": post.id,
                        "title": post.title,
                        "selftext": post.selftext,
                        "score": post.score,
                        "num_comments": post.num_comments,
                        "created_utc": post.created_utc,
                        "subreddit": subreddit_name,
                        "url": f"https://reddit.com{post.permalink}",
                        "author": str(post.author) if post.author else "[deleted]"
                    }

                    all_posts.append(post_data)

                    # Extract pain points from title and body
                    text = f"{post.title} {post.selftext}"
                    extracted_pains = self._extract_pain_points(text, post_data)
                    pain_points.extend(extracted_pains)

                    # Analyze top comments
                    try:
                        post.comments.replace_more(limit=0)
                        for comment in post.comments[:5]:  # Top 5 comments
                            comment_pains = self._extract_pain_points(
                                comment.body,
                                {**post_data, "is_comment": True}
                            )
                            pain_points.extend(comment_pains)
                    except:
                        pass

                print(f"  ✅ {subreddit_name}: {len(all_posts)} posts analyzed")
                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"  ⚠️  {subreddit_name}: {e}")
                continue

        # Aggregate and rank pain points
        results = {
            "query": query,
            "subreddits": subreddits,
            "time_filter": time_filter,
            "total_posts": len(all_posts),
            "total_pain_points": len(pain_points),
            "pain_points": self._rank_pain_points(pain_points),
            "posts": all_posts[:20],  # Top 20 posts
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "sentiment_summary": self._analyze_overall_sentiment(pain_points)
        }

        return results

    def _extract_pain_points(self, text: str, context: Dict) -> List[Dict]:
        """Extract pain points from text using pattern matching"""
        pain_patterns = [
            "problem", "issue", "difficult", "hard", "frustrating", "annoying",
            "hate", "wish", "need", "struggle", "pain", "challenge", "bug",
            "broken", "doesn't work", "terrible", "awful", "sucks", "disappointed"
        ]

        text_lower = text.lower()
        pain_points = []

        for pattern in pain_patterns:
            if pattern in text_lower:
                # Extract sentence containing the pain keyword
                sentences = text.split('.')
                for sentence in sentences:
                    if pattern in sentence.lower():
                        pain_point = {
                            "text": sentence.strip(),
                            "keyword": pattern,
                            "source": "reddit",
                            "subreddit": context.get("subreddit"),
                            "url": context.get("url"),
                            "score": context.get("score", 0),
                            "sentiment": self._analyze_sentiment(sentence),
                            "is_comment": context.get("is_comment", False)
                        }
                        pain_points.append(pain_point)

        return pain_points

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
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

    def _rank_pain_points(self, pain_points: List[Dict]) -> List[Dict]:
        """Rank pain points by frequency and score"""
        # Group similar pain points
        pain_groups = {}

        for pain in pain_points:
            key = pain["keyword"]
            if key not in pain_groups:
                pain_groups[key] = []
            pain_groups[key].append(pain)

        # Rank by frequency and average score
        ranked = []
        for keyword, pains in pain_groups.items():
            avg_score = sum(p["score"] for p in pains) / len(pains)
            avg_polarity = sum(p["sentiment"]["polarity"] for p in pains) / len(pains)

            ranked.append({
                "keyword": keyword,
                "frequency": len(pains),
                "avg_score": round(avg_score, 1),
                "avg_sentiment": round(avg_polarity, 2),
                "examples": pains[:3],  # Top 3 examples
                "importance_score": len(pains) * (1 + avg_score / 100)
            })

        # Sort by importance score
        ranked.sort(key=lambda x: x["importance_score"], reverse=True)

        return ranked

    def _analyze_overall_sentiment(self, pain_points: List[Dict]) -> Dict:
        """Analyze overall sentiment of all pain points"""
        if not pain_points:
            return {"avg_polarity": 0, "distribution": {}}

        polarities = [p["sentiment"]["polarity"] for p in pain_points]
        avg_polarity = sum(polarities) / len(polarities)

        distribution = {
            "positive": sum(1 for p in polarities if p > 0.1) / len(polarities),
            "neutral": sum(1 for p in polarities if -0.1 <= p <= 0.1) / len(polarities),
            "negative": sum(1 for p in polarities if p < -0.1) / len(polarities)
        }

        return {
            "avg_polarity": round(avg_polarity, 2),
            "distribution": {k: round(v, 2) for k, v in distribution.items()},
            "sentiment_label": "negative" if avg_polarity < -0.1 else "neutral" if avg_polarity < 0.1 else "positive"
        }

    def _mock_search_results(self, query: str) -> Dict:
        """Return mock results when API is not configured"""
        return {
            "query": query,
            "subreddits": ["productivity", "smallbusiness"],
            "time_filter": "month",
            "total_posts": 0,
            "total_pain_points": 0,
            "pain_points": [],
            "posts": [],
            "collected_at": datetime.utcnow().isoformat() + "Z",
            "sentiment_summary": {"avg_polarity": 0, "distribution": {}},
            "note": "Mock data - Reddit API not configured"
        }

    def search_competitor_mentions(
        self,
        competitor_name: str,
        subreddits: List[str] = None,
        time_filter: str = "month"
    ) -> Dict:
        """Search for mentions of competitors"""
        query = f'"{competitor_name}"'
        results = self.search_pain_points(query, subreddits, time_filter)

        # Filter to only mentions of the competitor
        results["competitor"] = competitor_name
        results["mention_count"] = results["total_posts"]

        return results

    def get_trending_topics(
        self,
        subreddit_name: str,
        time_filter: str = "week",
        limit: int = 50
    ) -> List[Dict]:
        """Get trending topics in a subreddit"""
        if not self.reddit:
            return []

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            trending = []

            for post in subreddit.hot(limit=limit):
                trending.append({
                    "title": post.title,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "created_utc": post.created_utc
                })

            return trending
        except Exception as e:
            print(f"❌ Error getting trending topics: {e}")
            return []


if __name__ == "__main__":
    # Test the connector
    reddit = RedditConnector()

    # Example search
    results = reddit.search_pain_points(
        "email management problems",
        subreddits=["productivity"],
        time_filter="month",
        limit=20
    )

    print(f"\n📊 Results:")
    print(f"Total posts analyzed: {results['total_posts']}")
    print(f"Pain points found: {results['total_pain_points']}")

    if results['pain_points']:
        print(f"\n🔥 Top Pain Points:")
        for pain in results['pain_points'][:5]:
            print(f"  • {pain['keyword']}: {pain['frequency']} mentions, score: {pain['avg_score']}")
