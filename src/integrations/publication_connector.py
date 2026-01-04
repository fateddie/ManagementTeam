#!/usr/bin/env python3
"""
Publication Connector
Collects articles and insights from industry publications for trend analysis.

Features:
- Scrape RSS feeds from industry publications
- Extract pain points and trends from articles
- Content analysis of professional journals and blogs
- Track emerging issues in healthcare professions

Usage:
    from src.integrations.publication_connector import PublicationConnector

    connector = PublicationConnector()
    results = connector.get_recent_articles(publication="physio_first", limit=20)
"""

import os
import json
import time
import re
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False
    print("⚠️  Warning: feedparser not installed. Install with: pip install feedparser")

try:
    from bs4 import BeautifulSoup
    import requests
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("⚠️  Warning: beautifulsoup4/requests not installed. Install with: pip install beautifulsoup4 requests")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except (ImportError, LookupError) as e:
    TEXTBLOB_AVAILABLE = False
    if 'textblob' not in str(e).lower():
        print("⚠️  Warning: textblob available but NLTK data missing. Sentiment analysis disabled.")
    else:
        print("⚠️  Warning: textblob not installed. Install with: pip install textblob")

try:
    from config.env_manager import get_config_cached
    ENV_MANAGER_AVAILABLE = True
except ImportError:
    ENV_MANAGER_AVAILABLE = False
    print("⚠️  Warning: env_manager not available. Using os.getenv fallback")


class PublicationConnector:
    """Connect to industry publications for trend and pain point analysis"""

    # Publication sources with RSS feeds and URLs
    PUBLICATIONS = {
        "physio_first": {
            "name": "Physio First",
            "url": "https://www.physiofirst.org.uk/news-and-views",
            "rss": "https://www.physiofirst.org.uk/rss.xml",
            "type": "physiotherapy"
        },
        "frontline": {
            "name": "Frontline Magazine (CSP)",
            "url": "https://www.csp.org.uk/frontline",
            "rss": None,  # May need HTML scraping
            "type": "physiotherapy"
        },
        "bacp": {
            "name": "BACP Therapy Today",
            "url": "https://www.bacp.co.uk/bacp-journals/therapy-today/",
            "rss": "https://www.bacp.co.uk/feed/",
            "type": "counselling"
        },
        "rcpod": {
            "name": "Royal College of Podiatry",
            "url": "https://www.rcpod.org.uk/news",
            "rss": "https://www.rcpod.org.uk/rss.xml",
            "type": "chiropody"
        },
        "podiatry_now": {
            "name": "Podiatry Now",
            "url": "https://www.podiatrytoday.com/",
            "rss": None,
            "type": "chiropody"
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Publication connector

        Args:
            config_path: Path to config file with scraping settings
        """
        self.config = self._load_config(config_path)
        self.cache = {}
        self.session = None

        if SCRAPING_AVAILABLE:
            self._init_session()
            print("✅ Scraping libraries available")
        else:
            print("⚠️  Scraping libraries not available. Using mock mode.")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or environment"""
        # Load environment variables from config/.env using centralized env_manager
        if ENV_MANAGER_AVAILABLE:
            try:
                env_config = get_config_cached()
                config = {
                    "user_agent": getattr(env_config, 'publication_user_agent', None) or
                                "ManagementTeam Research Bot/1.0",
                    "rate_limit_seconds": getattr(env_config, 'publication_rate_limit', None) or 5,
                    "timeout_seconds": getattr(env_config, 'publication_timeout', None) or 30,
                    "max_retries": getattr(env_config, 'publication_max_retries', None) or 3
                }
            except Exception as e:
                print(f"⚠️  Warning: Failed to load from env_manager: {e}")
                config = {
                    "user_agent": os.getenv("PUBLICATION_USER_AGENT", "ManagementTeam Research Bot/1.0"),
                    "rate_limit_seconds": int(os.getenv("PUBLICATION_RATE_LIMIT_SECONDS", "5")),
                    "timeout_seconds": int(os.getenv("PUBLICATION_TIMEOUT_SECONDS", "30")),
                    "max_retries": int(os.getenv("PUBLICATION_MAX_RETRIES", "3"))
                }
        else:
            # Fallback to os.getenv
            config = {
                "user_agent": os.getenv("PUBLICATION_USER_AGENT", "ManagementTeam Research Bot/1.0"),
                "rate_limit_seconds": int(os.getenv("PUBLICATION_RATE_LIMIT_SECONDS", "5")),
                "timeout_seconds": int(os.getenv("PUBLICATION_TIMEOUT_SECONDS", "30")),
                "max_retries": int(os.getenv("PUBLICATION_MAX_RETRIES", "3"))
            }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config.get("publications", {}))

        return config

    def _init_session(self):
        """Initialize requests session with headers"""
        if not SCRAPING_AVAILABLE:
            return

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config["user_agent"],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def get_recent_articles(
        self,
        publication: str = "all",
        limit: int = 20,
        days_back: int = 90
    ) -> Dict:
        """
        Get recent articles from publication(s)

        Args:
            publication: Publication key (see PUBLICATIONS dict) or "all"
            limit: Maximum number of articles per publication
            days_back: Number of days to look back

        Returns:
            Dict with articles, pain points, trends, and metadata
        """
        if not FEEDPARSER_AVAILABLE and not SCRAPING_AVAILABLE:
            return self._mock_articles(publication)

        print(f"\n📰 Fetching articles from: {publication}")

        # Determine which publications to query
        if publication == "all":
            pub_keys = list(self.PUBLICATIONS.keys())
        elif publication in self.PUBLICATIONS:
            pub_keys = [publication]
        else:
            print(f"❌ Unknown publication: {publication}")
            return self._mock_articles(publication)

        all_articles = []
        pain_points = []

        for pub_key in pub_keys:
            pub_info = self.PUBLICATIONS[pub_key]

            # Check cache
            cache_key = f"{pub_key}_{limit}_{days_back}"
            if cache_key in self.cache:
                print(f"📦 Using cached results for: {pub_info['name']}")
                cached = self.cache[cache_key]
                all_articles.extend(cached.get("articles", []))
                pain_points.extend(cached.get("pain_points", []))
                continue

            # Try RSS first, then HTML scraping
            articles = []
            if pub_info.get("rss") and FEEDPARSER_AVAILABLE:
                articles = self._fetch_rss_articles(pub_info, limit, days_back)
            elif SCRAPING_AVAILABLE:
                articles = self._scrape_html_articles(pub_info, limit, days_back)

            # Extract pain points and trends
            for article in articles:
                extracted = self._extract_pain_points(article["content"], article)
                pain_points.extend(extracted)

            all_articles.extend(articles)

            # Cache results
            self.cache[cache_key] = {
                "articles": articles,
                "pain_points": [p for p in pain_points if p.get("source_publication") == pub_key]
            }

            print(f"  ✅ {pub_info['name']}: {len(articles)} articles collected")

            # Rate limiting
            time.sleep(self.config["rate_limit_seconds"])

        # Compile results
        results = {
            "publication": publication,
            "publications_queried": pub_keys,
            "total_articles_collected": len(all_articles),
            "total_pain_points": len(pain_points),
            "articles": all_articles[:limit * len(pub_keys)],  # Limit total
            "pain_points": self._rank_pain_points(pain_points),
            "trend_summary": self._analyze_trends(all_articles),
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "_audit_trail": {
                "limit_per_publication": limit,
                "days_back": days_back,
                "method": "rss_and_html_scraping",
                "rate_limit_seconds": self.config["rate_limit_seconds"]
            }
        }

        return results

    def _fetch_rss_articles(
        self,
        pub_info: Dict,
        limit: int,
        days_back: int
    ) -> List[Dict]:
        """Fetch articles from RSS feed"""
        if not FEEDPARSER_AVAILABLE:
            return []

        try:
            print(f"  📡 Fetching RSS: {pub_info['rss']}")
            feed = feedparser.parse(pub_info['rss'])

            articles = []
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)

            for entry in feed.entries[:limit]:
                # Parse publish date
                pub_date = None
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, 'updated_parsed'):
                    pub_date = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)

                # Filter by date
                if pub_date and pub_date < cutoff_date:
                    continue

                # Extract content
                content = ""
                if hasattr(entry, 'summary'):
                    content = entry.summary
                elif hasattr(entry, 'description'):
                    content = entry.description

                # Clean HTML from content
                if content:
                    content = BeautifulSoup(content, 'html.parser').get_text() if SCRAPING_AVAILABLE else content

                article = {
                    "id": entry.get('id', entry.get('link', '')),
                    "title": entry.get('title', ''),
                    "content": content,
                    "url": entry.get('link', ''),
                    "published_date": pub_date.isoformat() if pub_date else None,
                    "source": pub_info['name'],
                    "source_type": pub_info['type'],
                    "collection_method": "rss"
                }

                articles.append(article)

            return articles

        except Exception as e:
            print(f"  ⚠️  Error fetching RSS: {e}")
            return []

    def _scrape_html_articles(
        self,
        pub_info: Dict,
        limit: int,
        days_back: int
    ) -> List[Dict]:
        """Scrape articles from HTML page (fallback when no RSS)"""
        if not SCRAPING_AVAILABLE:
            return []

        try:
            print(f"  🌐 Scraping HTML: {pub_info['url']}")
            response = self.session.get(
                pub_info['url'],
                timeout=self.config["timeout_seconds"]
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Generic article extraction (adapt per site)
            articles = []

            # Look for common article patterns
            article_elements = soup.find_all(['article', 'div'], class_=re.compile(r'(post|article|news|blog)'))

            for element in article_elements[:limit]:
                # Extract title
                title_elem = element.find(['h1', 'h2', 'h3', 'a'])
                title = title_elem.get_text(strip=True) if title_elem else ""

                # Extract link
                link_elem = element.find('a', href=True)
                url = urljoin(pub_info['url'], link_elem['href']) if link_elem else ""

                # Extract snippet/summary
                content_elem = element.find(['p', 'div'], class_=re.compile(r'(summary|excerpt|description)'))
                content = content_elem.get_text(strip=True) if content_elem else ""

                # Extract date (best effort)
                date_elem = element.find(['time', 'span'], class_=re.compile(r'(date|time|published)'))
                date_text = date_elem.get_text(strip=True) if date_elem else None

                if title and (content or url):
                    article = {
                        "id": url,
                        "title": title,
                        "content": content,
                        "url": url,
                        "published_date": date_text,
                        "source": pub_info['name'],
                        "source_type": pub_info['type'],
                        "collection_method": "html_scraping"
                    }
                    articles.append(article)

            return articles

        except Exception as e:
            print(f"  ⚠️  Error scraping HTML: {e}")
            return []

    def _extract_pain_points(self, text: str, context: Dict) -> List[Dict]:
        """Extract pain points and issues from article content"""
        if not text:
            return []

        # Healthcare-specific pain patterns
        pain_patterns = [
            "challenge", "problem", "issue", "difficulty", "struggle", "barrier",
            "shortage", "lack of", "need for", "crisis", "concern", "risk",
            "waiting times", "waiting list", "burnout", "stress", "pressure",
            "understaffed", "overworked", "retention", "recruitment", "funding"
        ]

        text_lower = text.lower()
        pain_points = []

        for pattern in pain_patterns:
            if pattern in text_lower:
                # Extract sentence containing the pain keyword
                sentences = re.split(r'[.!?]', text)
                for sentence in sentences:
                    if pattern in sentence.lower() and len(sentence.strip()) > 20:
                        pain_point = {
                            "text": sentence.strip(),
                            "keyword": pattern,
                            "source": "publication",
                            "source_publication": context.get("source"),
                            "publication_type": context.get("source_type"),
                            "article_title": context.get("title"),
                            "article_url": context.get("url"),
                            "published_date": context.get("published_date"),
                            "sentiment": self._analyze_sentiment(sentence)
                        }
                        pain_points.append(pain_point)

        return pain_points

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        if not TEXTBLOB_AVAILABLE or not text:
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
        """Rank pain points by frequency and recency"""
        # Group similar pain points
        pain_groups = {}

        for pain in pain_points:
            key = pain["keyword"]
            if key not in pain_groups:
                pain_groups[key] = []
            pain_groups[key].append(pain)

        # Rank by frequency, recency, and sentiment
        ranked = []
        for keyword, pains in pain_groups.items():
            avg_polarity = sum(p["sentiment"]["polarity"] for p in pains) / len(pains)

            # Recency boost (recent articles = higher importance)
            recency_score = 1.0
            recent_count = sum(1 for p in pains if self._is_recent(p.get("published_date"), days=30))
            if recent_count > 0:
                recency_score = 1 + (recent_count / len(pains))

            # Importance: frequency × recency × sentiment severity
            importance = len(pains) * recency_score * (1 - avg_polarity)

            ranked.append({
                "keyword": keyword,
                "frequency": len(pains),
                "recent_mentions": recent_count,
                "avg_sentiment": round(avg_polarity, 2),
                "examples": pains[:3],  # Top 3 examples
                "importance_score": round(importance, 2),
                "confidence": "high" if len(pains) >= 5 else "medium" if len(pains) >= 3 else "low",
                "publications": list(set(p.get("source_publication", "unknown") for p in pains))
            })

        # Sort by importance score
        ranked.sort(key=lambda x: x["importance_score"], reverse=True)

        return ranked

    def _is_recent(self, date_str: Optional[str], days: int = 30) -> bool:
        """Check if date is within recent days"""
        if not date_str:
            return False

        try:
            # Try to parse ISO format
            pub_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            return pub_date >= cutoff
        except:
            return False

    def _analyze_trends(self, articles: List[Dict]) -> Dict:
        """Analyze trends across articles"""
        if not articles:
            return {"trending_topics": [], "publication_breakdown": {}}

        # Extract common keywords/themes
        all_text = " ".join([
            f"{a.get('title', '')} {a.get('content', '')}"
            for a in articles
        ]).lower()

        # Healthcare trending topics (simple keyword frequency)
        trending_keywords = [
            "digital", "technology", "AI", "telehealth", "remote",
            "burnout", "wellbeing", "mental health",
            "NHS", "waiting times", "capacity",
            "training", "CPD", "education",
            "regulation", "standards", "quality"
        ]

        trending = []
        for keyword in trending_keywords:
            count = all_text.count(keyword.lower())
            if count > 0:
                trending.append({
                    "keyword": keyword,
                    "mentions": count,
                    "trend_strength": "high" if count >= 10 else "medium" if count >= 5 else "low"
                })

        trending.sort(key=lambda x: x["mentions"], reverse=True)

        # Publication breakdown
        pub_breakdown = {}
        for article in articles:
            pub_type = article.get("source_type", "unknown")
            pub_breakdown[pub_type] = pub_breakdown.get(pub_type, 0) + 1

        return {
            "trending_topics": trending[:10],  # Top 10
            "publication_breakdown": pub_breakdown,
            "date_range": {
                "earliest": min([a.get("published_date") for a in articles if a.get("published_date")], default=None),
                "latest": max([a.get("published_date") for a in articles if a.get("published_date")], default=None)
            }
        }

    def _mock_articles(self, publication: str) -> Dict:
        """Return mock results when scraping is not available"""
        return {
            "publication": publication,
            "publications_queried": [],
            "total_articles_collected": 0,
            "total_pain_points": 0,
            "articles": [],
            "pain_points": [],
            "trend_summary": {"trending_topics": [], "publication_breakdown": {}},
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "note": "Mock data - Scraping libraries not available. Install with: pip install feedparser beautifulsoup4 requests"
        }

    def search_topic(
        self,
        topic: str,
        publication: str = "all",
        limit: int = 20
    ) -> Dict:
        """
        Search for specific topic across publications

        Args:
            topic: Topic to search for (e.g., "appointment booking", "staff retention")
            publication: Publication key or "all"
            limit: Maximum number of articles

        Returns:
            Dict with relevant articles and pain points
        """
        # Get recent articles
        results = self.get_recent_articles(publication, limit=limit * 2)  # Get more to filter

        # Filter articles by topic
        topic_lower = topic.lower()
        relevant_articles = [
            a for a in results["articles"]
            if topic_lower in a.get("title", "").lower() or
               topic_lower in a.get("content", "").lower()
        ][:limit]

        # Filter pain points
        relevant_pain_points = [
            p for p in results.get("pain_points", [])
            if topic_lower in p.get("text", "").lower()
        ]

        return {
            "topic": topic,
            "publication": publication,
            "total_articles_found": len(relevant_articles),
            "total_pain_points_found": len(relevant_pain_points),
            "articles": relevant_articles,
            "pain_points": self._rank_pain_points(relevant_pain_points),
            "collected_at": results["collected_at"],
            "_audit_trail": {
                "search_query": topic,
                "total_articles_scanned": len(results["articles"]),
                "relevance_filter": "keyword_match"
            }
        }


if __name__ == "__main__":
    # Test the connector
    connector = PublicationConnector()

    # Example: Get recent articles
    results = connector.get_recent_articles(
        publication="all",
        limit=10,
        days_back=90
    )

    print(f"\n📊 Results:")
    print(f"Total articles collected: {results['total_articles_collected']}")
    print(f"Pain points found: {results['total_pain_points']}")

    if results['pain_points']:
        print(f"\n🔥 Top Pain Points:")
        for pain in results['pain_points'][:5]:
            print(f"  • {pain['keyword']}: {pain['frequency']} mentions "
                  f"(confidence: {pain['confidence']}, importance: {pain['importance_score']})")

    if results['trend_summary'].get('trending_topics'):
        print(f"\n📈 Trending Topics:")
        for topic in results['trend_summary']['trending_topics'][:5]:
            print(f"  • {topic['keyword']}: {topic['mentions']} mentions ({topic['trend_strength']})")
