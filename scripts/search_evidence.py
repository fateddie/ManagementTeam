#!/usr/bin/env python3
"""
search_evidence.py
------------------
Semantic search for evidence reports using sentence-transformers.

ZERO-COST alternative to OpenAI embeddings!

Features:
- Semantic similarity search (better than keyword matching)
- Industry and urgency filtering
- Export filtered results
- Uses existing sentence-transformers (already installed!)

Usage:
    # Find similar pain points
    python scripts/search_evidence.py "struggling with missed calls"

    # Filter by industry
    python scripts/search_evidence.py "customer service" --industry legal

    # Export results
    python scripts/search_evidence.py "AI receptionist" --top-k 50 --export results.csv
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    import pandas as pd
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    print(f"❌ Missing dependencies: {e}")
    print("   Install with: pip install sentence-transformers torch pandas")


class SemanticEvidenceSearch:
    """
    Semantic search engine for evidence reports.

    Uses sentence-transformers to find semantically similar posts,
    not just keyword matches. FREE after initial model download!
    """

    def __init__(self, csv_path="data/raw/social_posts_enriched.csv"):
        """
        Initialize semantic search engine.

        Args:
            csv_path: Path to enriched CSV data
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies not available")

        self.csv_path = csv_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Already installed!
        self.df = None
        self.embeddings = None

        print(f"📥 Loading data from {csv_path}...")
        self.df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(self.df)} posts")

    def build_index(self, force_rebuild=False):
        """
        Build semantic index (one-time operation).

        Creates embeddings for all posts. This takes ~5 seconds for 100 posts,
        but only needs to be done once!

        Args:
            force_rebuild: Force rebuild even if cache exists
        """
        cache_file = Path("data/cache/embeddings.pt")

        # Try to load from cache
        if cache_file.exists() and not force_rebuild:
            print("📂 Loading embeddings from cache...")
            self.embeddings = torch.load(cache_file)
            print(f"✅ Loaded {len(self.embeddings)} cached embeddings")
            return

        print("🔨 Building semantic index (this may take a moment)...")
        texts = self.df['text_excerpt'].tolist()

        self.embeddings = self.model.encode(
            texts,
            convert_to_tensor=True,
            show_progress_bar=True,
            batch_size=32
        )

        # Cache for next time
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.embeddings, cache_file)
        print(f"✅ Index built and cached to {cache_file}")

    def search(
        self,
        query: str,
        top_k=10,
        industry=None,
        urgency=None,
        min_similarity=0.0
    ):
        """
        Search by semantic similarity.

        Args:
            query: Search query (natural language)
            top_k: Number of results to return
            industry: Filter by industry (e.g., 'dental', 'legal')
            urgency: Filter by urgency (e.g., 'critical', 'high')
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of matching posts with similarity scores
        """
        if self.embeddings is None:
            self.build_index()

        print(f"\n🔍 Searching for: \"{query}\"")

        # Encode query
        query_embedding = self.model.encode(query, convert_to_tensor=True)

        # Calculate similarity
        scores = util.cos_sim(query_embedding, self.embeddings)[0]

        # Get top matches
        top_results = scores.topk(min(top_k * 3, len(scores)))  # Get extra for filtering

        results = []
        for score, idx in zip(top_results.values, top_results.indices):
            similarity = float(score)

            if similarity < min_similarity:
                continue

            row = self.df.iloc[int(idx)]

            # Apply filters
            if industry and row.get('industry', '').lower() != industry.lower():
                continue
            if urgency and row.get('urgency', '').lower() != urgency.lower():
                continue

            results.append({
                "similarity": similarity,
                "text": row['text_excerpt'],
                "industry": row.get('industry', 'Unknown'),
                "urgency": row.get('urgency', 'Unknown'),
                "upvotes": row.get('upvotes', 0),
                "subreddit": row.get('subreddit', 'Unknown'),
                "post_id": int(idx)
            })

            if len(results) >= top_k:
                break

        return results

    def display_results(self, results):
        """Display search results in a readable format."""
        print(f"\n📊 Found {len(results)} matching posts:\n")
        print("="*80)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. Similarity: {result['similarity']:.3f} | "
                  f"Industry: {result['industry']} | "
                  f"Urgency: {result['urgency'].upper()}")
            print(f"   [{result['subreddit']}] {result['upvotes']} upvotes")
            print(f"   \"{result['text'][:200]}...\"")

        print("\n" + "="*80)

    def export_results(self, results, output_path):
        """Export results to CSV."""
        if not results:
            print("⚠️  No results to export")
            return

        export_df = pd.DataFrame(results)
        export_df.to_csv(output_path, index=False)
        print(f"\n✅ Exported {len(results)} results to {output_path}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Semantic search for evidence reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find similar pain points
  python scripts/search_evidence.py "struggling with missed calls"

  # Filter by industry
  python scripts/search_evidence.py "customer service" --industry legal

  # Export results
  python scripts/search_evidence.py "AI receptionist" --top-k 50 --export results.csv

  # High similarity matches only
  python scripts/search_evidence.py "phone automation" --min-similarity 0.7
        """
    )

    parser.add_argument(
        'query',
        help='Search query (natural language)'
    )

    parser.add_argument(
        '--csv',
        default='data/raw/social_posts_enriched.csv',
        help='Path to enriched CSV file'
    )

    parser.add_argument(
        '--top-k',
        type=int,
        default=10,
        help='Number of results to return (default: 10)'
    )

    parser.add_argument(
        '--industry',
        help='Filter by industry (e.g., dental, legal, medical)'
    )

    parser.add_argument(
        '--urgency',
        help='Filter by urgency (critical, high, medium, low)'
    )

    parser.add_argument(
        '--min-similarity',
        type=float,
        default=0.0,
        help='Minimum similarity score 0-1 (default: 0.0)'
    )

    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export results to CSV file'
    )

    parser.add_argument(
        '--rebuild-index',
        action='store_true',
        help='Force rebuild of semantic index'
    )

    args = parser.parse_args()

    try:
        # Initialize search engine
        searcher = SemanticEvidenceSearch(args.csv)

        # Build index if needed
        if args.rebuild_index:
            searcher.build_index(force_rebuild=True)

        # Search
        results = searcher.search(
            query=args.query,
            top_k=args.top_k,
            industry=args.industry,
            urgency=args.urgency,
            min_similarity=args.min_similarity
        )

        # Display results
        searcher.display_results(results)

        # Export if requested
        if args.export:
            searcher.export_results(results, args.export)

    except FileNotFoundError:
        print(f"\n❌ Data file not found: {args.csv}")
        print("   Run data collection first:")
        print("   python cli/interactive_workflow.py")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
