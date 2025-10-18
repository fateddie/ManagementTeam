#!/usr/bin/env python3
"""
Topic Clustering with BERTopic
Zero-shot topic modeling for discovering trending topics and pain point patterns.

Features:
- Automatic topic discovery from social media posts
- Zero-shot classification without training data
- Topic evolution tracking over time
- Hierarchical topic clustering
- Custom topic labels

Model: BERTopic with sentence-transformers embeddings
Paper: https://arxiv.org/abs/2203.05794

Usage:
    from src.ml.topic_clustering import TopicClusterer

    clusterer = TopicClusterer()
    topics = clusterer.discover_topics(posts, min_topic_size=10)
    trending = clusterer.get_trending_topics(posts, timestamps)
"""

import os
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

try:
    from bertopic import BERTopic
    from bertopic.representation import ZeroShotClassification
    BERTOPIC_AVAILABLE = True
except ImportError:
    BERTOPIC_AVAILABLE = False
    print("⚠️  Warning: bertopic not installed. Install with: pip install bertopic")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")

try:
    from sklearn.feature_extraction.text import CountVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Warning: scikit-learn not installed. Install with: pip install scikit-learn")


class TopicClusterer:
    """
    Discover and track topics using BERTopic

    BERTopic uses transformer embeddings + UMAP + HDBSCAN to automatically
    discover topics in text data without requiring labeled training data.
    """

    # Default candidate topics for zero-shot classification
    DEFAULT_TOPICS = [
        "product quality",
        "customer service",
        "pricing and value",
        "features and functionality",
        "user experience",
        "performance and speed",
        "reliability and bugs",
        "integrations",
        "documentation and support",
        "onboarding and setup"
    ]

    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        candidate_topics: Optional[List[str]] = None,
        device: Optional[str] = None
    ):
        """
        Initialize topic clusterer

        Args:
            embedding_model: Sentence transformer model name
            candidate_topics: Optional list of topic labels for zero-shot
            device: Device to run on ("cpu", "cuda", "mps"). Auto-detected if None.
        """
        self.embedding_model_name = embedding_model
        self.candidate_topics = candidate_topics or self.DEFAULT_TOPICS
        self.device = self._get_device(device)
        self.topic_model = None
        self.embeddings = None
        self.topics = None
        self.probabilities = None
        self.cache = {}

        if BERTOPIC_AVAILABLE and SENTENCE_TRANSFORMERS_AVAILABLE:
            self._init_model()
        else:
            print("⚠️  BERTopic not available. Using keyword-based clustering.")

    def _get_device(self, device: Optional[str]) -> str:
        """Determine best available device"""
        if device:
            return device

        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
        except:
            pass

        return "cpu"

    def _init_model(self):
        """Initialize BERTopic model with zero-shot classification"""
        try:
            print("📥 Loading BERTopic model...")

            # 1. Embedding model
            print(f"  Loading embedding model: {self.embedding_model_name}")
            embedding_model = SentenceTransformer(self.embedding_model_name)

            # 2. Zero-shot representation model
            print("  Setting up zero-shot classification...")
            representation_model = ZeroShotClassification(
                self.candidate_topics,
                model="facebook/bart-large-mnli"
            )

            # 3. Custom vectorizer (better for social media)
            vectorizer_model = CountVectorizer(
                ngram_range=(1, 2),
                stop_words="english",
                min_df=2
            )

            # 4. Initialize BERTopic
            self.topic_model = BERTopic(
                embedding_model=embedding_model,
                representation_model=representation_model,
                vectorizer_model=vectorizer_model,
                min_topic_size=5,  # Minimum documents per topic
                nr_topics="auto",  # Auto-reduce topics
                verbose=False
            )

            print("✅ BERTopic model initialized")

        except Exception as e:
            print(f"❌ Failed to initialize BERTopic: {e}")
            self.topic_model = None

    def discover_topics(
        self,
        documents: List[str],
        min_topic_size: int = 5,
        nr_topics: Optional[int] = None
    ) -> Dict:
        """
        Discover topics in documents

        Args:
            documents: List of text documents
            min_topic_size: Minimum number of documents per topic
            nr_topics: Target number of topics (None for auto)

        Returns:
            Dict with discovered topics and statistics
        """
        if not self.topic_model:
            return self._keyword_based_clustering(documents)

        if len(documents) < min_topic_size:
            return {
                "error": f"Need at least {min_topic_size} documents for topic modeling",
                "topics": []
            }

        try:
            print(f"🔍 Discovering topics in {len(documents)} documents...")

            # Update model parameters
            self.topic_model.min_topic_size = min_topic_size
            if nr_topics:
                self.topic_model.nr_topics = nr_topics

            # Fit model
            topics, probabilities = self.topic_model.fit_transform(documents)

            # Store results
            self.topics = topics
            self.probabilities = probabilities

            # Get topic info
            topic_info = self.topic_model.get_topic_info()

            # Format results
            result = {
                "total_documents": len(documents),
                "num_topics": len(topic_info) - 1,  # Exclude outlier topic (-1)
                "topics": self._format_topics(topic_info),
                "document_topics": self._get_document_topics(documents, topics, probabilities),
                "topic_sizes": self._get_topic_sizes(topic_info)
            }

            print(f"✅ Discovered {result['num_topics']} topics")
            return result

        except Exception as e:
            print(f"❌ Error discovering topics: {e}")
            return self._keyword_based_clustering(documents)

    def _format_topics(self, topic_info) -> List[Dict]:
        """Format topic information"""
        topics = []

        for _, row in topic_info.iterrows():
            topic_id = row['Topic']

            # Skip outlier topic
            if topic_id == -1:
                continue

            # Get topic representation
            topic_words = self.topic_model.get_topic(topic_id)

            topics.append({
                "topic_id": int(topic_id),
                "label": row.get('Name', f'Topic {topic_id}'),
                "size": int(row['Count']),
                "keywords": [word for word, score in topic_words[:10]],
                "top_word": topic_words[0][0] if topic_words else ""
            })

        return topics

    def _get_document_topics(
        self,
        documents: List[str],
        topics: List[int],
        probabilities: np.ndarray
    ) -> List[Dict]:
        """Get topic assignments for each document"""
        doc_topics = []

        for doc, topic, prob in zip(documents[:100], topics[:100], probabilities[:100]):  # Limit for performance
            doc_topics.append({
                "document": doc[:200],  # Truncate long docs
                "topic_id": int(topic),
                "confidence": round(float(prob.max()), 3) if isinstance(prob, np.ndarray) else round(float(prob), 3)
            })

        return doc_topics

    def _get_topic_sizes(self, topic_info) -> Dict:
        """Get distribution of topic sizes"""
        sizes = topic_info[topic_info['Topic'] != -1]['Count'].tolist()

        return {
            "mean": round(np.mean(sizes), 1) if sizes else 0,
            "median": round(np.median(sizes), 1) if sizes else 0,
            "min": min(sizes) if sizes else 0,
            "max": max(sizes) if sizes else 0,
            "total": sum(sizes)
        }

    def get_trending_topics(
        self,
        documents: List[str],
        timestamps: List[datetime],
        time_window_hours: int = 24
    ) -> Dict:
        """
        Identify trending topics over time

        Args:
            documents: List of text documents
            timestamps: List of timestamps (one per document)
            time_window_hours: Rolling window size in hours

        Returns:
            Dict with trending topic analysis
        """
        if not self.topic_model or not self.topics:
            # Need to discover topics first
            self.discover_topics(documents)

        if not self.topics:
            return {"error": "No topics discovered"}

        try:
            # Group documents by time window
            time_windows = self._create_time_windows(timestamps, time_window_hours)

            # Track topic frequency per window
            topic_trends = defaultdict(list)

            for window_start, window_docs in time_windows.items():
                # Count topics in this window
                window_topics = [self.topics[i] for i in window_docs if i < len(self.topics)]
                topic_counts = Counter(window_topics)

                for topic_id in range(max(self.topics) + 1):
                    count = topic_counts.get(topic_id, 0)
                    topic_trends[topic_id].append({
                        "timestamp": window_start,
                        "count": count
                    })

            # Calculate trend velocity
            trending = []
            for topic_id, trend_data in topic_trends.items():
                if topic_id == -1:  # Skip outlier topic
                    continue

                counts = [d["count"] for d in trend_data]
                if len(counts) < 2:
                    continue

                # Calculate velocity (change over time)
                recent = sum(counts[-3:]) if len(counts) >= 3 else counts[-1]
                older = sum(counts[:3]) if len(counts) >= 3 else counts[0]
                velocity = recent - older

                trending.append({
                    "topic_id": topic_id,
                    "velocity": velocity,
                    "recent_count": recent,
                    "trend_direction": "rising" if velocity > 0 else "falling" if velocity < 0 else "stable",
                    "history": trend_data
                })

            # Sort by velocity
            trending.sort(key=lambda x: abs(x["velocity"]), reverse=True)

            return {
                "time_window_hours": time_window_hours,
                "num_windows": len(time_windows),
                "trending_topics": trending[:10],  # Top 10
                "most_rising": max(trending, key=lambda x: x["velocity"]) if trending else None,
                "most_falling": min(trending, key=lambda x: x["velocity"]) if trending else None
            }

        except Exception as e:
            print(f"❌ Error analyzing trends: {e}")
            return {"error": str(e)}

    def _create_time_windows(
        self,
        timestamps: List[datetime],
        window_hours: int
    ) -> Dict[datetime, List[int]]:
        """Create time windows for trending analysis"""
        if not timestamps:
            return {}

        # Find earliest timestamp
        earliest = min(timestamps)
        latest = max(timestamps)

        # Create windows
        windows = {}
        current = earliest
        delta = timedelta(hours=window_hours)

        while current <= latest:
            window_docs = [
                i for i, ts in enumerate(timestamps)
                if current <= ts < current + delta
            ]
            if window_docs:
                windows[current] = window_docs
            current += delta

        return windows

    def find_similar_topics(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Find topics similar to a query

        Args:
            query: Search query
            top_k: Number of similar topics to return

        Returns:
            List of similar topics with similarity scores
        """
        if not self.topic_model:
            return []

        try:
            similar_topics, similarity_scores = self.topic_model.find_topics(query, top_n=top_k)

            results = []
            for topic_id, score in zip(similar_topics, similarity_scores):
                if topic_id == -1:
                    continue

                topic_words = self.topic_model.get_topic(topic_id)

                results.append({
                    "topic_id": int(topic_id),
                    "similarity_score": round(float(score), 3),
                    "keywords": [word for word, _ in topic_words[:5]],
                    "representative": topic_words[0][0] if topic_words else ""
                })

            return results

        except Exception as e:
            print(f"⚠️  Error finding similar topics: {e}")
            return []

    def visualize_topics(self, output_path: str = "outputs/topic_visualization.html"):
        """
        Generate interactive topic visualization

        Args:
            output_path: Path to save HTML visualization
        """
        if not self.topic_model or not self.topics:
            print("⚠️  No topics to visualize. Run discover_topics() first.")
            return None

        try:
            # Create visualization
            fig = self.topic_model.visualize_topics()

            # Save to file
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(output_path)

            print(f"✅ Visualization saved to {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Error creating visualization: {e}")
            return None

    # ==============================================
    # Fallback: Keyword-Based Clustering
    # ==============================================

    def _keyword_based_clustering(self, documents: List[str]) -> Dict:
        """Simple keyword-based topic clustering fallback"""
        print("📦 Using keyword-based clustering")

        # Extract keywords
        from collections import defaultdict
        import re

        # Define topic keywords
        topic_keywords = {
            "performance": ["slow", "fast", "speed", "lag", "performance", "quick"],
            "usability": ["easy", "hard", "difficult", "simple", "intuitive", "confusing"],
            "features": ["feature", "functionality", "capability", "option", "tool"],
            "bugs": ["bug", "error", "crash", "issue", "problem", "broken"],
            "pricing": ["price", "cost", "expensive", "cheap", "value", "pricing"]
        }

        # Classify documents
        topic_counts = defaultdict(int)
        doc_topics = []

        for doc in documents:
            doc_lower = doc.lower()
            scores = {}

            for topic, keywords in topic_keywords.items():
                score = sum(1 for keyword in keywords if keyword in doc_lower)
                if score > 0:
                    scores[topic] = score

            if scores:
                top_topic = max(scores, key=scores.get)
                topic_counts[top_topic] += 1
                doc_topics.append({"document": doc[:200], "topic": top_topic, "confidence": 0.6})
            else:
                doc_topics.append({"document": doc[:200], "topic": "general", "confidence": 0.5})

        # Format topics
        topics = [
            {
                "topic_id": i,
                "label": topic,
                "size": count,
                "keywords": topic_keywords[topic][:5]
            }
            for i, (topic, count) in enumerate(topic_counts.items())
        ]

        return {
            "total_documents": len(documents),
            "num_topics": len(topics),
            "topics": topics,
            "document_topics": doc_topics[:100],
            "topic_sizes": {
                "mean": round(np.mean(list(topic_counts.values())), 1) if topic_counts else 0,
                "total": len(documents)
            },
            "mock_data": True
        }


# ==============================================
# Example Usage / Testing
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🔬 Topic Clustering with BERTopic - Test Suite")
    print("=" * 70 + "\n")

    clusterer = TopicClusterer()

    # Test documents
    test_docs = [
        "This app is so slow! Takes forever to load.",
        "The app crashes every time I try to export data.",
        "Love the new dark mode feature!",
        "UI is very confusing, hard to find settings.",
        "Performance is terrible, constantly freezing.",
        "Great customer support, they helped me quickly.",
        "The price is way too high for what you get.",
        "Missing integration with Slack, would be very useful.",
        "Documentation is unclear, needs more examples.",
        "App works great but could use more features.",
        "Slow loading times are frustrating.",
        "Interface is intuitive and easy to use.",
        "Frequent bugs and errors, very annoying.",
        "Value for money is excellent!",
        "Would like to see better mobile support."
    ]

    print("Test 1: Discovering topics\n")
    topics_result = clusterer.discover_topics(test_docs, min_topic_size=2)

    print(f"Discovered {topics_result['num_topics']} topics from {topics_result['total_documents']} documents\n")

    print("Topics found:")
    for topic in topics_result['topics'][:5]:
        print(f"  Topic {topic['topic_id']}: {topic['label']}")
        print(f"    Size: {topic['size']} documents")
        print(f"    Keywords: {', '.join(topic['keywords'][:5])}")
        print()

    print("\n" + "-" * 70 + "\n")
    print("Test 2: Finding similar topics\n")

    query = "slow performance issues"
    similar = clusterer.find_similar_topics(query, top_k=3)

    if similar:
        print(f"Topics similar to '{query}':")
        for topic in similar:
            print(f"  Topic {topic['topic_id']} (similarity: {topic['similarity_score']})")
            print(f"    Keywords: {', '.join(topic['keywords'])}")
            print()

    print("=" * 70)
    print("✅ All tests complete!")
    print("=" * 70 + "\n")
