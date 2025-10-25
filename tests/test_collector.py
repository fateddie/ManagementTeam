#!/usr/bin/env python3
"""
Quick Reddit-only test for pain discovery.
Collects real business conversations without complexity.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.integrations import message_collector_v2

# REDDIT ONLY (faster, better emotional signal)
message_collector_v2.MAX_TWEETS = 0  # Skip Twitter
message_collector_v2.MAX_REDDIT = 100  # 100 posts per keyword

print("\n" + "="*70)
print("🧪 REDDIT-ONLY TEST COLLECTION")
print("="*70)
print(f"\nKeywords: {len(message_collector_v2.KEYWORDS)}")
print(f"Reddit posts per keyword: {message_collector_v2.MAX_REDDIT}")
print(f"Expected total: ~{len(message_collector_v2.KEYWORDS) * message_collector_v2.MAX_REDDIT} posts")
print("\nThis will take ~5 minutes...\n")

# Run collection
df = message_collector_v2.run_collector()

if df is not None and len(df) > 0:
    print("\n" + "="*70)
    print("✅ SUCCESS")
    print("="*70)
    print(f"\nTotal posts collected: {len(df)}")
    print(f"Platforms: {df['platform'].unique().tolist()}")
    print(f"\n📊 Posts by keyword (top 5):")
    print(df['keyword'].value_counts().head())

    print(f"\n📋 Sample of collected data:")
    print("-"*70)
    for idx, row in df.head(10).iterrows():
        print(f"\nKeyword: {row['keyword']}")
        print(f"Text: {row['text_excerpt'][:150]}...")
        print(f"Sentiment: {row['sentiment']}")

    print("\n" + "="*70)
    print(f"💾 Full data saved to: {message_collector_v2.OUTPUT_FILE}")
    print("="*70)

    # Quality check
    if len(df) >= 100:
        print("\n✅ EXCELLENT: 100+ posts - ready for analysis")
    elif len(df) >= 50:
        print("\n✅ GOOD: 50+ posts - sufficient for analysis")
    else:
        print(f"\n⚠️  WARNING: Only {len(df)} posts - may need to adjust keywords")

else:
    print("\n" + "="*70)
    print("❌ COLLECTION FAILED")
    print("="*70)
    print("\nPossible issues:")
    print("  • Reddit API credentials not configured")
    print("  • Network connection problems")
    print("  • Keywords too narrow")
    print("\nRun: python tests/test_reddit_credentials.py")
