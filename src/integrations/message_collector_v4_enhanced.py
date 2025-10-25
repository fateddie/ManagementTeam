#!/usr/bin/env python3
"""
message_collector_v4_enhanced.py
-------------------------------------
ENHANCED VERSION with actionable intelligence extraction:
- Posts + top comments
- ICP extraction (industry, size, location)
- Urgency detection
- Competitor mentions
- Pricing signals
- Feature must-haves
-------------------------------------
"""

import os
import sys
import csv
import datetime
import re
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pytrends.request import TrendReq
import praw
from tqdm import tqdm
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load credentials
from src.utils.config_loader import get_env, load_env
load_env()

# ---------- CONFIG ----------
OUTPUT_FILE = "social_posts_enriched.csv"
MAX_REDDIT_PER_KEYWORD = 50
MAX_COMMENTS_PER_POST = 10

# Business subreddits
BUSINESS_SUBREDDITS = [
    "smallbusiness", "entrepreneur", "startups",
    "business", "sales", "marketing"
]

# Keywords (phrase search)
KEYWORDS = [
    "missing phone calls",
    "missed calls losing business",
    "can't answer the phone",
    "need receptionist",
    "call answering service",
    "virtual receptionist",
    "AI receptionist",
    "phone automation"
]

# Business context words
BUSINESS_CONTEXT = [
    "business", "customer", "client", "lead", "sales", "revenue",
    "company", "startup", "entrepreneur", "service", "appointment",
    "booking", "shop", "store", "owner", "agency"
]

# ICP detection patterns
INDUSTRY_PATTERNS = {
    "dental": r"\b(dent(?:al|ist)|teeth|orthodont)\b",
    "medical": r"\b(medical|doctor|clinic|physician|healthcare|medspa|hospital)\b",
    "legal": r"\b(law|legal|lawyer|attorney|firm)\b",
    "insurance": r"\b(insurance|policy|claim)\b",
    "real_estate": r"\b(real estate|realtor|property|housing)\b",
    "automotive": r"\b(car|auto|garage|mechanic|dealer)\b",
    "beauty": r"\b(salon|beauty|hair|spa|nail)\b",
    "fitness": r"\b(gym|fitness|health club|personal training)\b",
    "hospitality": r"\b(hotel|restaurant|cafe|catering)\b",
    "construction": r"\b(construct|builder|contractor|plumb|electric)\b",
    "retail": r"\b(retail|store|shop|ecommerce)\b",
    "consulting": r"\b(consult(?:ant|ing)|advisory)\b"
}

SIZE_PATTERNS = {
    "solo": r"\b(solo|myself|one[ -]person|just me|own(?:er)? ?(?:business)?)\b",
    "micro": r"\b([2-5][ -]employees?|small team|few employees)\b",
    "small": r"\b([6-9]|10|fifteen|twenty|30)[ -](?:person|employee|people)\b",
    "medium": r"\b([4-9]0|hundred)[ -](?:person|employee|people)\b"
}

LOCATION_PATTERNS = {
    "UK": r"\b(UK|United Kingdom|Britain|England|Scotland|Wales)\b",
    "Ireland": r"\b(Ireland|Dublin|Irish)\b",
    "US": r"\b(US|USA|United States|America)\b",
    "Canada": r"\b(Canada|Canadian|Toronto|Vancouver)\b",
    "Australia": r"\b(Australia|Australian|Sydney)\b"
}

# Urgency patterns
URGENCY_PATTERNS = {
    "critical": r"\b(urgent|asap|immediately|now|today|this week|losing (?:customer|money|lead)s?)\b",
    "high": r"\b(soon|need(?:ed)?|actively looking|comparing|researching)\b",
    "low": r"\b(consider(?:ing)?|thinking about|might|maybe|eventual(?:ly)?)\b"
}

# Competitor patterns (common ones - expand based on industry)
COMPETITOR_PATTERNS = [
    r"@?(\w+(?:AI|Bot|Voice|Call|Phone))",
    r"\b(Dialpad|Ruby|Moneypenny|Smith\.ai|Sonant|CallJoy|Aircall)\b"
]

# Pricing patterns
PRICING_PATTERNS = {
    "explicit": r"[$£€]([0-9,]+)(?:\/|\s?per\s?)(month|mo|year|yr)",
    "budget": r"\b(afford|cheap|budget|expensive|cost|price|pricing)\b",
    "loss": r"\b(los(?:e|ing)|miss(?:ed)?|waste)\s+[$£€]?([0-9,]+)",
}

# ---------- SETUP ----------
analyzer = SentimentIntensityAnalyzer()
seen_hashes = set()


def clean_text(text: str) -> str:
    """Clean text for processing."""
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^A-Za-z0-9\s.,!?'$£€/-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.encode("utf-8", "ignore").decode()


def has_business_context(text: str) -> bool:
    """Check if text has business context."""
    text_lower = text.lower()
    return any(word in text_lower for word in BUSINESS_CONTEXT)


def extract_icp(text: str) -> Dict[str, Optional[str]]:
    """Extract ICP attributes from text."""
    text_lower = text.lower()

    icp = {
        "industry": None,
        "size": None,
        "location": None
    }

    # Industry detection
    for industry, pattern in INDUSTRY_PATTERNS.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            icp["industry"] = industry
            break

    # Size detection
    for size, pattern in SIZE_PATTERNS.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            icp["size"] = size
            break

    # Location detection
    for location, pattern in LOCATION_PATTERNS.items():
        if re.search(pattern, text_lower, re.IGNORECASE):
            icp["location"] = location
            break

    return icp


def detect_urgency(text: str) -> str:
    """Detect urgency level."""
    text_lower = text.lower()

    if re.search(URGENCY_PATTERNS["critical"], text_lower, re.IGNORECASE):
        return "critical"
    elif re.search(URGENCY_PATTERNS["high"], text_lower, re.IGNORECASE):
        return "high"
    elif re.search(URGENCY_PATTERNS["low"], text_lower, re.IGNORECASE):
        return "low"
    else:
        return "medium"


def extract_competitors(text: str) -> List[str]:
    """Extract competitor mentions."""
    competitors = []
    for pattern in COMPETITOR_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        competitors.extend(matches)
    return list(set(competitors))[:5]  # Unique, max 5


def extract_pricing_signals(text: str) -> Dict[str, any]:
    """Extract pricing information."""
    signals = {
        "price_mentions": [],
        "has_budget_concern": False,
        "quantified_loss": None
    }

    # Explicit pricing
    explicit_matches = re.findall(PRICING_PATTERNS["explicit"], text, re.IGNORECASE)
    signals["price_mentions"] = [f"${m[0]}/{m[1]}" for m in explicit_matches]

    # Budget concerns
    signals["has_budget_concern"] = bool(re.search(PRICING_PATTERNS["budget"], text, re.IGNORECASE))

    # Quantified loss
    loss_match = re.search(PRICING_PATTERNS["loss"], text, re.IGNORECASE)
    if loss_match and len(loss_match.groups()) > 1:
        signals["quantified_loss"] = loss_match.group(2)

    return signals


def collect_reddit_enhanced(keyword: str):
    """Collect Reddit posts + comments with enriched data."""
    data = []
    print(f"👥 Reddit: {keyword}")

    try:
        reddit = praw.Reddit(
            client_id=get_env("REDDIT_CLIENT_ID"),
            client_secret=get_env("REDDIT_CLIENT_SECRET"),
            user_agent=get_env("REDDIT_USER_AGENT", "collector_agent")
        )

        subreddit_string = "+".join(BUSINESS_SUBREDDITS)
        subreddit = reddit.subreddit(subreddit_string)

        # Phrase search
        search_query = f'"{keyword}"' if ' ' in keyword else keyword

        collected = 0
        for submission in subreddit.search(search_query, limit=MAX_REDDIT_PER_KEYWORD * 2, sort="new", time_filter="year"):
            if collected >= MAX_REDDIT_PER_KEYWORD:
                break

            # Process post
            post_text = clean_text(f"{submission.title} {submission.selftext}")

            if len(post_text) < 30 or not has_business_context(post_text):
                continue

            # Get top comments
            submission.comments.replace_more(limit=0)
            comments = []
            for comment in submission.comments.list()[:MAX_COMMENTS_PER_POST]:
                if hasattr(comment, 'body') and len(comment.body) > 20:
                    comments.append(clean_text(comment.body))

            # Combine post + comments for analysis
            full_text = post_text + " " + " ".join(comments)

            # Deduplication
            h = hashlib.md5(post_text.encode()).hexdigest()
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            # Extract intelligence
            icp = extract_icp(full_text)
            urgency = detect_urgency(full_text)
            competitors = extract_competitors(full_text)
            pricing = extract_pricing_signals(full_text)
            sentiment = analyzer.polarity_scores(post_text)["compound"]

            data.append({
                "platform": "Reddit",
                "keyword": keyword,
                "text_excerpt": post_text[:500],
                "comments_analyzed": len(comments),
                "sentiment": round(sentiment, 3),
                "date": datetime.date.fromtimestamp(submission.created_utc),
                "subreddit": submission.subreddit.display_name,
                "upvotes": submission.score,
                "num_comments": submission.num_comments,
                # ICP
                "industry": icp["industry"],
                "company_size": icp["size"],
                "location": icp["location"],
                # Urgency
                "urgency": urgency,
                # Competitors
                "competitors_mentioned": ",".join(competitors) if competitors else None,
                # Pricing
                "price_mentions": ",".join(pricing["price_mentions"]) if pricing["price_mentions"] else None,
                "has_budget_concern": pricing["has_budget_concern"],
                "quantified_loss": pricing["quantified_loss"]
            })
            collected += 1

            # Rate limiting
            time.sleep(0.5)

        print(f"   ✅ Collected {len(data)} enriched posts")

    except Exception as e:
        print(f"   ⚠️  Reddit error: {e}")

    return data


def collect_trends_enhanced(keyword: str):
    """Collect Google Trends with breakout/rising queries."""
    try:
        pytrend = TrendReq(hl='en-GB', tz=0)

        # Interest over time
        pytrend.build_payload([keyword], geo='GB', timeframe='today 12-m')
        interest_df = pytrend.interest_over_time()

        avg_interest = round(interest_df[keyword].mean(), 2) if not interest_df.empty else None

        # Related queries (breakout + rising)
        time.sleep(2)  # Rate limiting
        related = pytrend.related_queries()

        breakout = []
        rising = []

        if keyword in related and related[keyword]['rising'] is not None:
            rising_df = related[keyword]['rising']
            rising = rising_df['query'].head(5).tolist() if not rising_df.empty else []

        return {
            "avg_interest": avg_interest,
            "rising_queries": rising
        }

    except Exception as e:
        print(f"   ⚠️  Trends error: {e}")
        return {"avg_interest": None, "rising_queries": []}


def run_collector():
    """Main enhanced collection orchestrator."""
    all_records = []
    all_rising_queries = []

    for kw in tqdm(KEYWORDS, desc="Collecting"):
        reddit_data = collect_reddit_enhanced(kw)
        trends_data = collect_trends_enhanced(kw)

        # Add trend data to posts
        for record in reddit_data:
            record["trend_avg"] = trends_data["avg_interest"]
            all_records.append(record)

        # Collect rising queries
        if trends_data["rising_queries"]:
            all_rising_queries.extend(trends_data["rising_queries"])

    if not all_records:
        print("❌ No data collected.")
        return None, []

    df = pd.DataFrame(all_records)
    df.drop_duplicates(subset=["text_excerpt"], inplace=True)
    df.to_csv(OUTPUT_FILE, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"\n✅ Saved {len(df)} enriched records → {OUTPUT_FILE}")

    return df, list(set(all_rising_queries))


if __name__ == "__main__":
    df, rising_queries = run_collector()

    if df is not None:
        print(f"\n📊 Collection Summary:")
        print(f"Total posts: {len(df)}")
        print(f"\nBy urgency:")
        print(df['urgency'].value_counts())
        print(f"\nBy industry:")
        print(df['industry'].value_counts().head())
        print(f"\nRising search queries:")
        for q in rising_queries[:10]:
            print(f"  • {q}")
