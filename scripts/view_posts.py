#!/usr/bin/env python3
"""
view_posts.py
--------------
Utility script to view posts by IDs or filter criteria.

Supports TRANSPARENCY by allowing quick verification of source data.

Usage:
    # View specific posts by ID
    python scripts/view_posts.py --ids 1,5,12,23

    # Filter by industry
    python scripts/view_posts.py --industry dental

    # Filter by urgency
    python scripts/view_posts.py --urgency critical

    # Filter by multiple criteria
    python scripts/view_posts.py --industry medical --urgency critical

    # Export filtered results
    python scripts/view_posts.py --industry dental --export dental_posts.csv
"""

import argparse
import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def view_posts_by_ids(csv_path: str, post_ids: list):
    """View specific posts by their IDs."""
    df = pd.read_csv(csv_path)

    print("\n" + "="*100)
    print(f"📋 VIEWING {len(post_ids)} POSTS")
    print("="*100)

    for post_id in post_ids:
        if post_id >= len(df):
            print(f"\n⚠️  Post ID {post_id} not found (max: {len(df)-1})")
            continue

        post = df.iloc[post_id]

        print(f"\n{'─'*100}")
        print(f"POST ID: {post_id}")
        print(f"{'─'*100}")
        print(f"Platform: {post.get('platform', 'Unknown')}")
        print(f"Subreddit: {post.get('subreddit', 'N/A')}")
        print(f"Keyword: {post.get('keyword', 'N/A')}")
        print(f"Date: {post.get('date', 'N/A')}")
        print(f"Upvotes: {post.get('upvotes', 0)}")
        print(f"Comments: {post.get('num_comments', 0)}")
        print(f"\nINDUSTRY: {post.get('industry', 'Not detected')}")
        print(f"COMPANY SIZE: {post.get('company_size', 'Not detected')}")
        print(f"LOCATION: {post.get('location', 'Not detected')}")
        print(f"URGENCY: {post.get('urgency', 'Not detected').upper()}")
        print(f"\nCOMPETITORS: {post.get('competitors_mentioned', 'None')}")
        print(f"PRICING: {post.get('price_mentions', 'None')}")
        print(f"BUDGET CONCERN: {'Yes' if post.get('has_budget_concern') else 'No'}")
        print(f"\nTEXT:")
        print(f"{post.get('text_excerpt', 'No text')}")

    print("\n" + "="*100)


def filter_posts(csv_path: str, filters: dict):
    """Filter posts by criteria."""
    df = pd.read_csv(csv_path)

    # Apply filters
    filtered_df = df.copy()
    for column, value in filters.items():
        if column in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[column] == value]

    print("\n" + "="*100)
    print(f"📊 FILTERED RESULTS: {len(filtered_df)} posts")
    print("="*100)

    if len(filtered_df) == 0:
        print("\n⚠️  No posts match the filter criteria.")
        return filtered_df

    # Show summary
    print(f"\nFilter criteria:")
    for column, value in filters.items():
        print(f"   • {column}: {value}")

    print(f"\nMatching Post IDs: {filtered_df.index.tolist()}")

    # Show first 5 posts
    print(f"\nShowing first 5 posts:")
    for i, (idx, post) in enumerate(filtered_df.head(5).iterrows()):
        print(f"\n{'─'*100}")
        print(f"POST ID: {idx}")
        print(f"{'─'*100}")
        print(f"Subreddit: r/{post.get('subreddit', 'N/A')}")
        print(f"Upvotes: {post.get('upvotes', 0)} | Urgency: {post.get('urgency', 'unknown').upper()}")
        print(f"Text: \"{post.get('text_excerpt', '')[:200]}...\"")

    print("\n" + "="*100)

    return filtered_df


def export_posts(df: pd.DataFrame, output_path: str):
    """Export filtered posts."""
    df.to_csv(output_path, index=True)
    print(f"\n✅ Exported {len(df)} posts to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="View posts by ID or filter criteria",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View specific posts
  python scripts/view_posts.py --ids 1,5,12

  # Filter by industry
  python scripts/view_posts.py --industry dental

  # Filter and export
  python scripts/view_posts.py --industry medical --urgency critical --export medical_critical.csv
        """
    )

    parser.add_argument('--csv', default='data/raw/social_posts_enriched.csv', help='Path to CSV file')
    parser.add_argument('--ids', help='Comma-separated post IDs to view')
    parser.add_argument('--industry', help='Filter by industry')
    parser.add_argument('--urgency', help='Filter by urgency (critical, high, medium, low)')
    parser.add_argument('--company-size', dest='company_size', help='Filter by company size')
    parser.add_argument('--location', help='Filter by location')
    parser.add_argument('--keyword', help='Filter by keyword')
    parser.add_argument('--export', help='Export filtered results to CSV')

    args = parser.parse_args()

    # Check if CSV exists
    if not Path(args.csv).exists():
        print(f"❌ File not found: {args.csv}")
        print(f"   Run data collection first.")
        sys.exit(1)

    # View by IDs
    if args.ids:
        post_ids = [int(x.strip()) for x in args.ids.split(',')]
        view_posts_by_ids(args.csv, post_ids)
        return

    # Filter by criteria
    filters = {}
    if args.industry:
        filters['industry'] = args.industry
    if args.urgency:
        filters['urgency'] = args.urgency
    if args.company_size:
        filters['company_size'] = args.company_size
    if args.location:
        filters['location'] = args.location
    if args.keyword:
        filters['keyword'] = args.keyword

    if filters:
        filtered_df = filter_posts(args.csv, filters)

        if args.export and len(filtered_df) > 0:
            export_posts(filtered_df, args.export)
    else:
        print("❌ Please specify either --ids or filter criteria")
        parser.print_help()


if __name__ == "__main__":
    main()
