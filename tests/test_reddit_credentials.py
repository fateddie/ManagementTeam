#!/usr/bin/env python3
"""
Test Reddit API credentials.

Quick validation that Reddit credentials are configured correctly
before running the full data collection.

Usage:
    python tests/test_reddit_credentials.py

Returns:
    Exit code 0 if successful, 1 if failed
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import praw
    from src.utils.config_loader import get_env, load_env
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Install with: pip install praw")
    sys.exit(1)


def test_reddit_credentials():
    """Test Reddit API credentials."""
    print("\n" + "="*70)
    print("🔧 Testing Reddit API Credentials")
    print("="*70)

    # Load environment
    try:
        load_env()
        print("✅ Environment loaded")
    except Exception as e:
        print(f"⚠️  Warning: Could not load .env file: {e}")

    # Get credentials
    client_id = get_env("REDDIT_CLIENT_ID")
    client_secret = get_env("REDDIT_CLIENT_SECRET")
    user_agent = get_env("REDDIT_USER_AGENT", "test_agent")

    print(f"\nChecking credentials...")
    print(f"  REDDIT_CLIENT_ID: {'✅ Set' if client_id else '❌ Missing'}")
    print(f"  REDDIT_CLIENT_SECRET: {'✅ Set' if client_secret else '❌ Missing'}")
    print(f"  REDDIT_USER_AGENT: {user_agent}")

    if not client_id or not client_secret:
        print("\n❌ Reddit credentials not configured!")
        print("\n📋 Setup Instructions:")
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Click 'Create App' or 'Create Another App'")
        print("3. Choose 'script' type")
        print("4. Add to config/.env:")
        print("   REDDIT_CLIENT_ID=your_client_id")
        print("   REDDIT_CLIENT_SECRET=your_client_secret")
        print("   REDDIT_USER_AGENT=your_app_name/1.0")
        print("\n" + "="*70)
        return False

    # Test connection
    print("\n🔌 Testing connection to Reddit API...")
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        # Fetch a few posts from a popular subreddit
        print("📥 Fetching 3 posts from r/smallbusiness...")
        posts = list(reddit.subreddit("smallbusiness").hot(limit=3))

        if len(posts) == 0:
            print("⚠️  No posts returned (API may be rate-limited)")
            return False

        print(f"✅ Successfully fetched {len(posts)} posts:")
        for i, post in enumerate(posts, 1):
            title = post.title[:60] + "..." if len(post.title) > 60 else post.title
            print(f"   {i}. {title}")

        print("\n✅ Reddit API credentials are valid!")
        print("="*70)
        return True

    except praw.exceptions.PRAWException as e:
        print(f"\n❌ Reddit API error: {e}")
        print("\nPossible issues:")
        print("  • Invalid client_id or client_secret")
        print("  • App not properly configured on Reddit")
        print("  • Network connection issues")
        print("\n📋 Verify your credentials at: https://www.reddit.com/prefs/apps")
        print("="*70)
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("="*70)
        return False


if __name__ == "__main__":
    success = test_reddit_credentials()
    sys.exit(0 if success else 1)
