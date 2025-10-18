#!/usr/bin/env python3
"""
YouTube Data API Connector
Collects trending videos, viral patterns, and market insights from YouTube.

Features:
- Fetch trending videos by region/category
- Analyze viral video patterns (titles, tags, engagement)
- Track content trends and topics
- Extract successful content strategies

Usage:
    from src.integrations.youtube_connector import YouTubeConnector

    youtube = YouTubeConnector()
    trending = youtube.get_trending_videos(region_code="US", max_results=50)
    patterns = youtube.analyze_viral_patterns(trending['videos'])
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import Counter

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    print("⚠️  Warning: google-api-python-client not installed. Install with: pip install google-api-python-client")


class YouTubeConnector:
    """Connect to YouTube Data API for trending analysis and market research"""

    # YouTube API quota costs (v3)
    QUOTA_COSTS = {
        "search": 100,
        "videos_list": 1,
        "channels_list": 1,
        "comment_threads": 1
    }

    # Trending categories (IDs from YouTube)
    CATEGORIES = {
        "all": None,
        "music": "10",
        "gaming": "20",
        "entertainment": "24",
        "news": "25",
        "education": "27",
        "howto": "26",
        "tech": "28",
        "sports": "17"
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize YouTube connector

        Args:
            config_path: Path to config file with YouTube API key
        """
        self.config = self._load_config(config_path)
        self.youtube = None
        self.quota_used = 0
        self.quota_limit = 10000  # Default daily quota
        self.cache = {}

        if YOUTUBE_API_AVAILABLE and self._has_credentials():
            self._init_youtube_client()
        else:
            print("⚠️  YouTube API not configured. Using mock mode.")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or environment"""
        config = {
            "api_key": os.getenv("YOUTUBE_API_KEY"),
            "quota_limit": int(os.getenv("YOUTUBE_QUOTA_LIMIT", "10000"))
        }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config.get("youtube", {}))

        return config

    def _has_credentials(self) -> bool:
        """Check if YouTube API key is configured"""
        return bool(self.config.get("api_key"))

    def _init_youtube_client(self):
        """Initialize YouTube Data API client"""
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.config["api_key"])
            self.quota_limit = self.config.get("quota_limit", 10000)
            print("✅ YouTube API connected")
        except Exception as e:
            print(f"❌ Failed to connect to YouTube API: {e}")
            self.youtube = None

    def _track_quota(self, operation: str, count: int = 1):
        """Track API quota usage"""
        cost = self.QUOTA_COSTS.get(operation, 1) * count
        self.quota_used += cost

        if self.quota_used >= self.quota_limit:
            print(f"⚠️  Warning: Approaching quota limit ({self.quota_used}/{self.quota_limit})")

    def get_trending_videos(
        self,
        region_code: str = "US",
        category_id: Optional[str] = None,
        max_results: int = 50
    ) -> Dict:
        """
        Get trending videos from YouTube

        Args:
            region_code: ISO 3166-1 alpha-2 country code (e.g., "US", "GB", "JP")
            category_id: YouTube category ID (see CATEGORIES)
            max_results: Maximum number of videos to return (max 50)

        Returns:
            Dict with trending videos and metadata
        """
        if not self.youtube:
            return self._mock_trending_videos(region_code, max_results)

        cache_key = f"trending_{region_code}_{category_id}_{max_results}"
        if cache_key in self.cache:
            print(f"📦 Using cached trending videos for {region_code}")
            return self.cache[cache_key]

        try:
            # Build request
            request_params = {
                "part": "snippet,contentDetails,statistics",
                "chart": "mostPopular",
                "regionCode": region_code,
                "maxResults": min(max_results, 50)  # YouTube API limit
            }

            if category_id:
                request_params["videoCategoryId"] = category_id

            # Execute request
            request = self.youtube.videos().list(**request_params)
            response = request.execute()

            self._track_quota("videos_list")

            # Parse videos
            videos = []
            for item in response.get("items", []):
                video = self._parse_video(item)
                videos.append(video)

            result = {
                "region": region_code,
                "category": category_id,
                "total_videos": len(videos),
                "videos": videos,
                "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }

            self.cache[cache_key] = result
            return result

        except HttpError as e:
            if e.resp.status == 403:
                print("❌ YouTube API quota exceeded or invalid API key")
            else:
                print(f"❌ YouTube API error: {e}")
            return self._mock_trending_videos(region_code, max_results)

        except Exception as e:
            print(f"❌ Unexpected error fetching trending videos: {e}")
            return self._mock_trending_videos(region_code, max_results)

    def _parse_video(self, item: Dict) -> Dict:
        """Parse YouTube API video item into standardized format"""
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        content_details = item.get("contentDetails", {})

        return {
            "video_id": item.get("id"),
            "title": snippet.get("title", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "channel_id": snippet.get("channelId", ""),
            "description": snippet.get("description", ""),
            "published_at": snippet.get("publishedAt", ""),
            "thumbnails": snippet.get("thumbnails", {}),
            "tags": snippet.get("tags", []),
            "category_id": snippet.get("categoryId", ""),
            "duration": content_details.get("duration", ""),
            "view_count": int(statistics.get("viewCount", 0)),
            "like_count": int(statistics.get("likeCount", 0)),
            "comment_count": int(statistics.get("commentCount", 0)),
            "engagement_rate": self._calculate_engagement_rate(statistics)
        }

    def _calculate_engagement_rate(self, stats: Dict) -> float:
        """Calculate engagement rate (likes + comments) / views"""
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        if views == 0:
            return 0.0

        engagement = (likes + comments) / views * 100
        return round(engagement, 2)

    def analyze_viral_patterns(self, videos: List[Dict]) -> Dict:
        """
        Analyze patterns in viral/trending videos

        Args:
            videos: List of video dicts from get_trending_videos()

        Returns:
            Dict with viral pattern insights
        """
        if not videos:
            return {"error": "No videos to analyze"}

        # Collect patterns
        all_tags = []
        title_lengths = []
        title_words = []
        top_channels = []
        engagement_scores = []

        for video in videos:
            # Tags
            all_tags.extend(video.get("tags", []))

            # Titles
            title = video.get("title", "")
            title_lengths.append(len(title))
            title_words.extend(title.lower().split())

            # Channels
            top_channels.append(video.get("channel_title", ""))

            # Engagement
            engagement_scores.append(video.get("engagement_rate", 0))

        # Analyze patterns
        tag_freq = Counter(all_tags)
        word_freq = Counter(title_words)
        channel_freq = Counter(top_channels)

        # Calculate statistics
        avg_title_length = sum(title_lengths) / len(title_lengths) if title_lengths else 0
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0

        # Calculate view velocity (views per day since publish)
        velocities = []
        for video in videos:
            published = datetime.fromisoformat(video["published_at"].replace("Z", "+00:00"))
            days_old = (datetime.now(timezone.utc) - published).days + 1  # Avoid divide by zero
            velocity = video["view_count"] / days_old
            velocities.append(velocity)

        avg_velocity = sum(velocities) / len(velocities) if velocities else 0

        return {
            "total_videos_analyzed": len(videos),
            "top_tags": tag_freq.most_common(20),
            "top_title_words": word_freq.most_common(30),
            "top_channels": channel_freq.most_common(10),
            "title_patterns": {
                "avg_length": round(avg_title_length, 1),
                "optimal_range": (30, 70)  # Research-based optimal title length
            },
            "engagement_metrics": {
                "avg_engagement_rate": round(avg_engagement, 2),
                "top_performers": sorted(videos, key=lambda v: v["engagement_rate"], reverse=True)[:5]
            },
            "view_velocity": {
                "avg_views_per_day": round(avg_velocity, 0),
                "fastest_growing": sorted(zip(videos, velocities), key=lambda x: x[1], reverse=True)[:5]
            }
        }

    def search_videos(
        self,
        query: str,
        max_results: int = 25,
        order: str = "relevance",
        published_after: Optional[datetime] = None
    ) -> Dict:
        """
        Search for videos by keyword

        Args:
            query: Search query
            max_results: Maximum results (default 25, max 50)
            order: Sort order (relevance, date, viewCount, rating)
            published_after: Only return videos published after this date

        Returns:
            Dict with search results
        """
        if not self.youtube:
            return self._mock_search_results(query, max_results)

        try:
            request_params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": min(max_results, 50),
                "order": order
            }

            if published_after:
                request_params["publishedAfter"] = published_after.isoformat() + "Z"

            request = self.youtube.search().list(**request_params)
            response = request.execute()

            self._track_quota("search")

            # Get detailed statistics for found videos
            video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
            videos = self._get_video_details(video_ids)

            return {
                "query": query,
                "total_results": len(videos),
                "videos": videos,
                "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            }

        except HttpError as e:
            print(f"❌ YouTube search error: {e}")
            return self._mock_search_results(query, max_results)

    def _get_video_details(self, video_ids: List[str]) -> List[Dict]:
        """Fetch detailed statistics for multiple videos"""
        if not video_ids or not self.youtube:
            return []

        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(video_ids)
            )
            response = request.execute()

            self._track_quota("videos_list")

            videos = [self._parse_video(item) for item in response.get("items", [])]
            return videos

        except Exception as e:
            print(f"❌ Error fetching video details: {e}")
            return []

    def get_quota_status(self) -> Dict:
        """Get current quota usage status"""
        return {
            "quota_used": self.quota_used,
            "quota_limit": self.quota_limit,
            "quota_remaining": self.quota_limit - self.quota_used,
            "quota_percentage": round((self.quota_used / self.quota_limit) * 100, 1) if self.quota_limit > 0 else 0
        }

    # ==============================================
    # Mock Data Methods (for testing without API key)
    # ==============================================

    def _mock_trending_videos(self, region_code: str, max_results: int) -> Dict:
        """Generate mock trending videos for testing"""
        print(f"📦 Using mock data for YouTube trending ({region_code})")

        mock_videos = [
            {
                "video_id": f"mock_video_{i}",
                "title": f"Trending Video {i}: How to Build Amazing Apps",
                "channel_title": f"Tech Channel {i % 5}",
                "channel_id": f"channel_{i % 5}",
                "description": "Learn how to build amazing applications...",
                "published_at": (datetime.now(timezone.utc) - timedelta(days=i)).isoformat().replace('+00:00', 'Z'),
                "thumbnails": {},
                "tags": ["tutorial", "coding", "productivity", "tech"],
                "category_id": "28",
                "duration": "PT10M30S",
                "view_count": 100000 - (i * 1000),
                "like_count": 5000 - (i * 50),
                "comment_count": 500 - (i * 5),
                "engagement_rate": 5.5 - (i * 0.1)
            }
            for i in range(min(max_results, 10))
        ]

        return {
            "region": region_code,
            "category": None,
            "total_videos": len(mock_videos),
            "videos": mock_videos,
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "mock_data": True
        }

    def _mock_search_results(self, query: str, max_results: int) -> Dict:
        """Generate mock search results for testing"""
        print(f"📦 Using mock data for YouTube search ({query})")

        mock_videos = [
            {
                "video_id": f"search_mock_{i}",
                "title": f"{query} Tutorial {i}",
                "channel_title": f"Creator {i}",
                "channel_id": f"channel_{i}",
                "description": f"A tutorial about {query}",
                "published_at": (datetime.now(timezone.utc) - timedelta(days=i*7)).isoformat().replace('+00:00', 'Z'),
                "thumbnails": {},
                "tags": query.split() + ["tutorial"],
                "category_id": "27",
                "duration": "PT8M15S",
                "view_count": 50000 - (i * 2000),
                "like_count": 2500 - (i * 100),
                "comment_count": 250 - (i * 10),
                "engagement_rate": 5.0 - (i * 0.2)
            }
            for i in range(min(max_results, 5))
        ]

        return {
            "query": query,
            "total_results": len(mock_videos),
            "videos": mock_videos,
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "mock_data": True
        }


# ==============================================
# Example Usage / Testing
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎥 YouTube Connector - Test Suite")
    print("=" * 70 + "\n")

    # Initialize connector
    youtube = YouTubeConnector()

    # Test 1: Get trending videos
    print("Test 1: Fetching trending videos (US)...")
    trending = youtube.get_trending_videos(region_code="US", max_results=10)
    print(f"✅ Found {trending['total_videos']} trending videos")
    if trending.get("mock_data"):
        print("   ℹ️  Using mock data (add YOUTUBE_API_KEY to .env for real data)")
    print()

    # Test 2: Analyze viral patterns
    print("Test 2: Analyzing viral patterns...")
    patterns = youtube.analyze_viral_patterns(trending['videos'])
    print(f"✅ Analyzed {patterns['total_videos_analyzed']} videos")
    print(f"   Top tags: {', '.join([tag for tag, count in patterns['top_tags'][:5]])}")
    print(f"   Avg engagement: {patterns['engagement_metrics']['avg_engagement_rate']}%")
    print(f"   Avg title length: {patterns['title_patterns']['avg_length']} chars")
    print()

    # Test 3: Search videos
    print("Test 3: Searching for 'productivity app'...")
    search_results = youtube.search_videos("productivity app", max_results=5)
    print(f"✅ Found {search_results['total_results']} videos")
    print()

    # Test 4: Quota status
    print("Test 4: Checking quota usage...")
    quota = youtube.get_quota_status()
    print(f"✅ Quota used: {quota['quota_used']}/{quota['quota_limit']} ({quota['quota_percentage']}%)")
    print()

    print("=" * 70)
    print("✅ All tests complete!")
    print("=" * 70 + "\n")
