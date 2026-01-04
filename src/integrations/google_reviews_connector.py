#!/usr/bin/env python3
"""
Google Reviews Connector
Collects customer reviews from Google Maps for pain point analysis.

Features:
- Search for business reviews on Google Maps
- Extract pain points from customer feedback
- Sentiment analysis of reviews
- Ethical scraping with rate limiting

Usage:
    from src.integrations.google_reviews_connector import GoogleReviewsConnector

    connector = GoogleReviewsConnector()
    results = connector.get_reviews("London Physiotherapy Clinic", limit=20)
"""

import os
import json
import time
import re
from typing import List, Dict, Optional
from datetime import datetime, timezone
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Warning: playwright not installed. Install with: pip install playwright && playwright install chromium")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except (ImportError, LookupError) as e:
    TEXTBLOB_AVAILABLE = False
    if 'textblob' not in str(e).lower():
        print("⚠️  Warning: textblob available but NLTK data missing. Sentiment analysis disabled.")
        print("    To enable: python -c 'import nltk; nltk.download(\"wordnet\"); nltk.download(\"brown\")'")
    else:
        print("⚠️  Warning: textblob not installed. Install with: pip install textblob")

try:
    from config.env_manager import get_config_cached
    ENV_MANAGER_AVAILABLE = True
except ImportError:
    ENV_MANAGER_AVAILABLE = False
    print("⚠️  Warning: env_manager not available. Using os.getenv fallback")


class GoogleReviewsConnector:
    """Connect to Google Maps for clinic review collection and pain point analysis"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Google Reviews connector

        Args:
            config_path: Path to config file with scraping settings
        """
        self.config = self._load_config(config_path)
        self.cache = {}
        self.playwright = None
        self.browser = None
        self.context = None

        if PLAYWRIGHT_AVAILABLE:
            print("✅ Playwright available - scraping enabled")
        else:
            print("⚠️  Playwright not available. Using mock mode.")

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or environment"""
        # Load environment variables from config/.env using centralized env_manager
        if ENV_MANAGER_AVAILABLE:
            try:
                env_config = get_config_cached()
                config = {
                    "user_agent": getattr(env_config, 'google_user_agent', None) or
                                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "rate_limit_seconds": getattr(env_config, 'google_rate_limit', None) or 10,
                    "timeout_ms": getattr(env_config, 'google_timeout_ms', None) or 30000,
                    "headless": getattr(env_config, 'google_headless', None) or True
                }
            except Exception as e:
                print(f"⚠️  Warning: Failed to load from env_manager: {e}")
                config = {
                    "user_agent": os.getenv("GOOGLE_USER_AGENT",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"),
                    "rate_limit_seconds": int(os.getenv("GOOGLE_RATE_LIMIT_SECONDS", "10")),
                    "timeout_ms": int(os.getenv("GOOGLE_TIMEOUT_MS", "30000")),
                    "headless": os.getenv("GOOGLE_HEADLESS", "true").lower() == "true"
                }
        else:
            # Fallback to os.getenv
            config = {
                "user_agent": os.getenv("GOOGLE_USER_AGENT",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"),
                "rate_limit_seconds": int(os.getenv("GOOGLE_RATE_LIMIT_SECONDS", "10")),
                "timeout_ms": int(os.getenv("GOOGLE_TIMEOUT_MS", "30000")),
                "headless": os.getenv("GOOGLE_HEADLESS", "true").lower() == "true"
            }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config.get("google_reviews", {}))

        return config

    def _init_browser(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            return False

        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.config["headless"]
            )
            self.context = self.browser.new_context(
                user_agent=self.config["user_agent"],
                viewport={"width": 1920, "height": 1080}
            )
            print("✅ Playwright browser initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize browser: {e}")
            return False

    def _close_browser(self):
        """Close Playwright browser"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"⚠️  Warning: Error closing browser: {e}")

    def get_reviews(
        self,
        business_name: str,
        location: str = "UK",
        limit: int = 20,
        min_rating: Optional[int] = None,
        max_rating: Optional[int] = None
    ) -> Dict:
        """
        Get reviews for a business from Google Maps

        Args:
            business_name: Name of the business (e.g., "London Physiotherapy Clinic")
            location: Location filter (default: "UK")
            limit: Maximum number of reviews to collect
            min_rating: Minimum star rating filter (1-5)
            max_rating: Maximum star rating filter (1-5)

        Returns:
            Dict with reviews, pain points, sentiment analysis, and metadata
        """
        if not PLAYWRIGHT_AVAILABLE:
            return self._mock_reviews(business_name)

        # Check cache
        cache_key = f"{business_name}_{location}_{limit}"
        if cache_key in self.cache:
            print(f"📦 Using cached results for: {business_name}")
            return self.cache[cache_key]

        print(f"\n🔍 Searching Google Maps for: '{business_name}' in {location}")

        if not self._init_browser():
            return self._mock_reviews(business_name)

        try:
            page = self.context.new_page()

            # Search Google Maps
            search_query = f"{business_name} {location}"
            maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

            print(f"🌐 Loading: {maps_url}")
            page.goto(maps_url, timeout=self.config["timeout_ms"])
            time.sleep(3)  # Wait for dynamic content

            # Extract business information
            business_info = self._extract_business_info(page)

            # Click on reviews tab if available
            try:
                # Look for reviews button/tab
                page.click('button[aria-label*="Review"]', timeout=5000)
                time.sleep(2)
            except:
                print("⚠️  Reviews tab not found, using default view")

            # Scroll to load more reviews
            reviews = self._scroll_and_extract_reviews(page, limit)

            # Filter by rating if specified
            if min_rating or max_rating:
                reviews = [
                    r for r in reviews
                    if (min_rating is None or r["rating"] >= min_rating) and
                       (max_rating is None or r["rating"] <= max_rating)
                ]

            # Extract pain points
            pain_points = []
            for review in reviews:
                extracted = self._extract_pain_points(review["text"], review)
                pain_points.extend(extracted)

            # Compile results
            results = {
                "business_name": business_name,
                "location": location,
                "business_info": business_info,
                "total_reviews_collected": len(reviews),
                "total_pain_points": len(pain_points),
                "reviews": reviews,
                "pain_points": self._rank_pain_points(pain_points),
                "sentiment_summary": self._analyze_overall_sentiment(reviews),
                "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "_audit_trail": {
                    "search_query": search_query,
                    "limit_requested": limit,
                    "rating_filter": {"min": min_rating, "max": max_rating},
                    "scraping_method": "playwright",
                    "rate_limit_seconds": self.config["rate_limit_seconds"]
                }
            }

            # Cache results
            self.cache[cache_key] = results

            page.close()
            return results

        except Exception as e:
            print(f"❌ Error scraping reviews: {e}")
            return self._mock_reviews(business_name)
        finally:
            self._close_browser()
            # Rate limiting (ethical scraping)
            time.sleep(self.config["rate_limit_seconds"])

    def _extract_business_info(self, page) -> Dict:
        """Extract basic business information"""
        try:
            # Try to extract business name, rating, total reviews
            info = {
                "name": None,
                "average_rating": None,
                "total_reviews": None,
                "address": None,
                "phone": None
            }

            # Extract what's available (Google Maps DOM is dynamic)
            try:
                info["name"] = page.locator("h1").first.inner_text()
            except:
                pass

            try:
                # Rating format: "4.5★" or similar
                rating_text = page.locator('[role="img"][aria-label*="stars"]').first.get_attribute("aria-label")
                if rating_text:
                    match = re.search(r'([\d.]+)\s*star', rating_text)
                    if match:
                        info["average_rating"] = float(match.group(1))
            except:
                pass

            try:
                # Total reviews format: "123 reviews"
                reviews_text = page.locator('button[aria-label*="review"]').first.inner_text()
                if reviews_text:
                    match = re.search(r'([\d,]+)', reviews_text)
                    if match:
                        info["total_reviews"] = int(match.group(1).replace(',', ''))
            except:
                pass

            return info

        except Exception as e:
            print(f"⚠️  Could not extract business info: {e}")
            return {}

    def _scroll_and_extract_reviews(self, page, limit: int) -> List[Dict]:
        """Scroll reviews panel and extract review data"""
        reviews = []

        try:
            # Find the scrollable reviews container
            scrollable_div = page.locator('div[role="feed"]').first

            # Scroll and collect reviews
            last_height = 0
            scroll_attempts = 0
            max_scroll_attempts = 10

            while len(reviews) < limit and scroll_attempts < max_scroll_attempts:
                # Extract currently visible reviews
                review_elements = page.locator('[data-review-id]').all()

                for element in review_elements:
                    if len(reviews) >= limit:
                        break

                    try:
                        review_data = self._parse_review_element(element)
                        if review_data and review_data["id"] not in [r["id"] for r in reviews]:
                            reviews.append(review_data)
                    except Exception as e:
                        print(f"⚠️  Error parsing review: {e}")
                        continue

                # Scroll down
                try:
                    scrollable_div.evaluate("el => el.scrollTop = el.scrollHeight")
                    time.sleep(1.5)  # Wait for new reviews to load
                    scroll_attempts += 1
                except:
                    break

            print(f"  ✅ Collected {len(reviews)} reviews")
            return reviews[:limit]

        except Exception as e:
            print(f"⚠️  Error scrolling reviews: {e}")
            return reviews

    def _parse_review_element(self, element) -> Optional[Dict]:
        """Parse individual review element"""
        try:
            review_id = element.get_attribute("data-review-id")

            # Extract rating (look for aria-label with stars)
            rating = None
            try:
                rating_text = element.locator('[role="img"][aria-label*="star"]').first.get_attribute("aria-label")
                match = re.search(r'(\d+)', rating_text)
                if match:
                    rating = int(match.group(1))
            except:
                pass

            # Extract review text
            text = ""
            try:
                # Click "More" button if present
                try:
                    more_button = element.locator('button[aria-label*="More"]').first
                    more_button.click(timeout=1000)
                    time.sleep(0.5)
                except:
                    pass

                text = element.locator('[class*="review-text"]').first.inner_text()
            except:
                pass

            # Extract reviewer name
            reviewer = "Anonymous"
            try:
                reviewer = element.locator('[class*="reviewer"]').first.inner_text()
            except:
                pass

            # Extract date
            date_text = None
            try:
                date_text = element.locator('[class*="review-date"]').first.inner_text()
            except:
                pass

            return {
                "id": review_id,
                "reviewer": reviewer,
                "rating": rating,
                "text": text,
                "date": date_text,
                "source": "google_maps",
                "sentiment": self._analyze_sentiment(text) if text else None
            }

        except Exception as e:
            print(f"⚠️  Error parsing review element: {e}")
            return None

    def _extract_pain_points(self, text: str, context: Dict) -> List[Dict]:
        """Extract pain points from review text using pattern matching"""
        if not text:
            return []

        pain_patterns = [
            "problem", "issue", "difficult", "hard", "frustrating", "annoying",
            "hate", "wish", "need", "struggle", "pain", "challenge", "bad",
            "terrible", "awful", "horrible", "worst", "disappointed", "unhappy",
            "waiting", "wait", "late", "delayed", "slow", "rude", "unprofessional"
        ]

        text_lower = text.lower()
        pain_points = []

        for pattern in pain_patterns:
            if pattern in text_lower:
                # Extract sentence containing the pain keyword
                sentences = re.split(r'[.!?]', text)
                for sentence in sentences:
                    if pattern in sentence.lower() and len(sentence.strip()) > 10:
                        pain_point = {
                            "text": sentence.strip(),
                            "keyword": pattern,
                            "source": "google_reviews",
                            "business": context.get("business_name"),
                            "rating": context.get("rating"),
                            "reviewer": context.get("reviewer"),
                            "sentiment": self._analyze_sentiment(sentence),
                            "review_id": context.get("id")
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
        """Rank pain points by frequency and severity"""
        # Group similar pain points
        pain_groups = {}

        for pain in pain_points:
            key = pain["keyword"]
            if key not in pain_groups:
                pain_groups[key] = []
            pain_groups[key].append(pain)

        # Rank by frequency and sentiment
        ranked = []
        for keyword, pains in pain_groups.items():
            avg_rating = sum(p.get("rating", 0) for p in pains if p.get("rating")) / len(pains)
            avg_polarity = sum(p["sentiment"]["polarity"] for p in pains) / len(pains)

            # Importance: frequency × severity (lower rating + negative sentiment = higher importance)
            severity = (5 - avg_rating) if avg_rating > 0 else 2.5  # Lower rating = higher severity
            importance = len(pains) * (1 + severity / 5) * (1 - avg_polarity)

            ranked.append({
                "keyword": keyword,
                "frequency": len(pains),
                "avg_rating": round(avg_rating, 1) if avg_rating > 0 else None,
                "avg_sentiment": round(avg_polarity, 2),
                "examples": pains[:3],  # Top 3 examples
                "importance_score": round(importance, 2),
                "confidence": "high" if len(pains) >= 5 else "medium" if len(pains) >= 3 else "low"
            })

        # Sort by importance score
        ranked.sort(key=lambda x: x["importance_score"], reverse=True)

        return ranked

    def _analyze_overall_sentiment(self, reviews: List[Dict]) -> Dict:
        """Analyze overall sentiment of all reviews"""
        if not reviews:
            return {"avg_rating": None, "avg_polarity": 0, "distribution": {}}

        # Rating distribution
        ratings = [r["rating"] for r in reviews if r.get("rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else None

        # Sentiment distribution
        sentiments = [r["sentiment"] for r in reviews if r.get("sentiment")]
        if sentiments:
            polarities = [s["polarity"] for s in sentiments]
            avg_polarity = sum(polarities) / len(polarities)

            distribution = {
                "positive": sum(1 for p in polarities if p > 0.1) / len(polarities),
                "neutral": sum(1 for p in polarities if -0.1 <= p <= 0.1) / len(polarities),
                "negative": sum(1 for p in polarities if p < -0.1) / len(polarities)
            }
        else:
            avg_polarity = 0
            distribution = {}

        return {
            "avg_rating": round(avg_rating, 1) if avg_rating else None,
            "rating_distribution": self._get_rating_distribution(ratings),
            "avg_polarity": round(avg_polarity, 2),
            "sentiment_distribution": {k: round(v, 2) for k, v in distribution.items()},
            "sentiment_label": "negative" if avg_polarity < -0.1 else "neutral" if avg_polarity < 0.1 else "positive"
        }

    def _get_rating_distribution(self, ratings: List[int]) -> Dict:
        """Get distribution of star ratings"""
        if not ratings:
            return {}

        distribution = {}
        for i in range(1, 6):
            count = sum(1 for r in ratings if r == i)
            distribution[f"{i}_star"] = {
                "count": count,
                "percentage": round(count / len(ratings) * 100, 1)
            }

        return distribution

    def _mock_reviews(self, business_name: str) -> Dict:
        """Return mock results when scraping is not available"""
        return {
            "business_name": business_name,
            "location": "UK",
            "business_info": {},
            "total_reviews_collected": 0,
            "total_pain_points": 0,
            "reviews": [],
            "pain_points": [],
            "sentiment_summary": {"avg_rating": None, "avg_polarity": 0, "distribution": {}},
            "collected_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "note": "Mock data - Playwright not available. Install with: pip install playwright && playwright install chromium"
        }

    def search_clinics_by_type(
        self,
        clinic_type: str,
        location: str = "UK",
        limit: int = 10
    ) -> List[Dict]:
        """
        Search for clinics by type (e.g., "physiotherapy clinic", "counselling practice")

        Args:
            clinic_type: Type of clinic to search for
            location: Location to search in
            limit: Number of clinics to find

        Returns:
            List of clinic information with basic details
        """
        if not PLAYWRIGHT_AVAILABLE:
            return []

        print(f"\n🔍 Searching for {clinic_type} in {location}")

        if not self._init_browser():
            return []

        try:
            page = self.context.new_page()

            search_query = f"{clinic_type} {location}"
            maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"

            page.goto(maps_url, timeout=self.config["timeout_ms"])
            time.sleep(3)

            # Extract clinic listings
            clinics = []
            # This is a simplified version - full implementation would extract
            # clinic names, addresses, ratings from the search results
            # For now, return empty list as this requires more complex DOM parsing

            return clinics

        except Exception as e:
            print(f"❌ Error searching clinics: {e}")
            return []
        finally:
            self._close_browser()


if __name__ == "__main__":
    # Test the connector
    connector = GoogleReviewsConnector()

    # Example: Get reviews for a business
    results = connector.get_reviews(
        business_name="London Physiotherapy Clinic",
        location="London UK",
        limit=10
    )

    print(f"\n📊 Results:")
    print(f"Business: {results.get('business_info', {}).get('name', 'N/A')}")
    print(f"Total reviews collected: {results['total_reviews_collected']}")
    print(f"Pain points found: {results['total_pain_points']}")

    if results['pain_points']:
        print(f"\n🔥 Top Pain Points:")
        for pain in results['pain_points'][:5]:
            print(f"  • {pain['keyword']}: {pain['frequency']} mentions "
                  f"(importance: {pain['importance_score']}, confidence: {pain['confidence']})")

    if results['sentiment_summary'].get('avg_rating'):
        print(f"\n⭐ Average Rating: {results['sentiment_summary']['avg_rating']}/5")
