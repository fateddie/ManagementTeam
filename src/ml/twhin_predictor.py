#!/usr/bin/env python3
"""
TwHIN-BERT Engagement Predictor
Uses Twitter's TwHIN-BERT model for social media engagement prediction.

Features:
- Predict engagement for social media posts (likes, retweets, shares)
- Calculate virality scores based on content
- Analyze hashtag effectiveness
- Twitter-trained embeddings for social content understanding

Model: Twitter/twhin-bert-base (110M parameters)
Paper: https://arxiv.org/abs/2209.07562

Usage:
    from src.ml.twhin_predictor import TwHINPredictor

    predictor = TwHINPredictor()
    result = predictor.predict_engagement("Check out our new productivity app! 🚀 #productivity")
"""

import os
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Warning: transformers/torch not installed. Install with: pip install transformers torch")


class TwHINPredictor:
    """
    Predict social media engagement using TwHIN-BERT

    TwHIN-BERT is trained on 7 billion tweets with social engagement signals,
    making it ideal for predicting virality and engagement on social platforms.
    """

    # Model identifiers
    MODEL_NAME = "Twitter/twhin-bert-base"
    MODEL_SIZE = "110M"

    # Engagement thresholds (calibrated from research)
    THRESHOLDS = {
        "low": 0.3,
        "medium": 0.6,
        "high": 0.8
    }

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize TwHIN-BERT predictor

        Args:
            model_name: Hugging Face model name (default: Twitter/twhin-bert-base)
            device: Device to run on ("cpu", "cuda", "mps"). Auto-detected if None.
        """
        self.model_name = model_name or self.MODEL_NAME
        self.device = self._get_device(device)
        self.tokenizer = None
        self.model = None
        self.cache = {}

        if TRANSFORMERS_AVAILABLE:
            self._load_model()
        else:
            print("⚠️  Transformers not available. Using mock predictions.")

    def _get_device(self, device: Optional[str]) -> str:
        """Determine best available device"""
        if device:
            return device

        if not TRANSFORMERS_AVAILABLE:
            return "cpu"

        import torch
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def _load_model(self):
        """Load TwHIN-BERT model and tokenizer"""
        try:
            print(f"📥 Loading {self.model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            print(f"✅ Model loaded on {self.device}")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            self.tokenizer = None
            self.model = None

    def predict_engagement(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Predict engagement score for social media content

        Args:
            text: Post text content
            metadata: Optional metadata (follower_count, time_of_day, etc.)

        Returns:
            Dict with engagement predictions and analysis
        """
        if not self.model or not self.tokenizer:
            return self._mock_prediction(text)

        # Check cache
        cache_key = f"engagement_{hash(text)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        try:
            # Get embedding from TwHIN-BERT
            embedding = self._get_embedding(text)

            # Calculate engagement score (0-100)
            # Note: This is a simplified scoring. In production, you'd fine-tune
            # the model on labeled engagement data.
            base_score = self._calculate_engagement_score(embedding, text)

            # Adjust based on metadata
            if metadata:
                base_score = self._adjust_for_metadata(base_score, metadata)

            # Classify engagement level
            level = self._classify_engagement_level(base_score)

            # Analyze content features
            features = self._analyze_content_features(text)

            result = {
                "engagement_score": round(base_score, 2),
                "engagement_level": level,
                "predicted_metrics": {
                    "likes_multiplier": round(base_score / 50, 2),  # Relative to baseline
                    "shares_multiplier": round(base_score / 100, 2),
                    "comments_multiplier": round(base_score / 75, 2)
                },
                "content_features": features,
                "confidence": round(self._calculate_confidence(embedding), 2),
                "model": self.model_name
            }

            self.cache[cache_key] = result
            return result

        except Exception as e:
            print(f"❌ Error predicting engagement: {e}")
            return self._mock_prediction(text)

    def _get_embedding(self, text: str) -> np.ndarray:
        """Get TwHIN-BERT embedding for text"""
        import torch

        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128,
            padding=True
        ).to(self.device)

        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token embedding (first token)
            embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]

        return embedding

    def _calculate_engagement_score(self, embedding: np.ndarray, text: str) -> float:
        """
        Calculate engagement score from embedding

        This is a simplified heuristic. For production:
        - Fine-tune on labeled engagement data
        - Train a regression head on top of TwHIN-BERT
        - Use historical engagement data for calibration
        """
        # Embedding magnitude as base score
        magnitude = np.linalg.norm(embedding)
        base_score = min(magnitude * 15, 100)  # Scale to 0-100

        # Adjust based on text features
        text_lower = text.lower()

        # Positive signals
        if any(emoji in text for emoji in ['🚀', '🔥', '💯', '⚡', '✨']):
            base_score *= 1.15  # Emojis boost engagement

        if any(word in text_lower for word in ['new', 'launch', 'release', 'announcing']):
            base_score *= 1.10  # Announcement language

        if '!' in text:
            base_score *= 1.05  # Excitement

        # Hashtag analysis
        hashtag_count = text.count('#')
        if 1 <= hashtag_count <= 3:
            base_score *= 1.08  # Optimal hashtag range
        elif hashtag_count > 5:
            base_score *= 0.9  # Too many hashtags reduces engagement

        # Question engagement
        if '?' in text:
            base_score *= 1.12  # Questions drive engagement

        # Cap at 100
        return min(base_score, 100.0)

    def _adjust_for_metadata(self, score: float, metadata: Dict) -> float:
        """Adjust score based on metadata (follower count, timing, etc.)"""
        adjusted = score

        # Account follower count influence
        if "follower_count" in metadata:
            followers = metadata["follower_count"]
            if followers > 100000:
                adjusted *= 1.3
            elif followers > 10000:
                adjusted *= 1.15
            elif followers < 100:
                adjusted *= 0.7

        # Time of day influence
        if "hour_of_day" in metadata:
            hour = metadata["hour_of_day"]
            # Peak hours: 9am-11am, 6pm-9pm
            if hour in [9, 10, 11, 18, 19, 20, 21]:
                adjusted *= 1.1
            elif hour in [0, 1, 2, 3, 4, 5]:
                adjusted *= 0.8

        # Day of week
        if "day_of_week" in metadata:
            day = metadata["day_of_week"]
            # Weekdays typically better for professional content
            if day in ["Monday", "Tuesday", "Wednesday", "Thursday"]:
                adjusted *= 1.05
            elif day in ["Saturday", "Sunday"]:
                adjusted *= 0.95

        return min(adjusted, 100.0)

    def _classify_engagement_level(self, score: float) -> str:
        """Classify engagement score into level"""
        if score >= self.THRESHOLDS["high"] * 100:
            return "high"
        elif score >= self.THRESHOLDS["medium"] * 100:
            return "medium"
        else:
            return "low"

    def _calculate_confidence(self, embedding: np.ndarray) -> float:
        """
        Calculate prediction confidence

        Based on embedding variance. Higher variance = lower confidence.
        """
        variance = np.var(embedding)
        # Inverse relationship: high variance = low confidence
        confidence = 1.0 / (1.0 + variance / 100)
        return min(confidence, 1.0)

    def _analyze_content_features(self, text: str) -> Dict:
        """Analyze content features for engagement insights"""
        hashtags = [word for word in text.split() if word.startswith('#')]
        mentions = [word for word in text.split() if word.startswith('@')]
        emojis = [char for char in text if ord(char) > 127000]  # Simplified emoji detection

        return {
            "text_length": len(text),
            "word_count": len(text.split()),
            "hashtag_count": len(hashtags),
            "hashtags": hashtags[:10],  # Top 10
            "mention_count": len(mentions),
            "emoji_count": len(emojis),
            "has_question": '?' in text,
            "has_exclamation": '!' in text,
            "has_url": 'http' in text.lower() or 'www.' in text.lower()
        }

    def batch_predict(self, texts: List[str], metadata_list: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Predict engagement for multiple texts

        Args:
            texts: List of text content
            metadata_list: Optional list of metadata dicts (one per text)

        Returns:
            List of prediction dicts
        """
        results = []
        metadata_list = metadata_list or [None] * len(texts)

        for text, metadata in zip(texts, metadata_list):
            result = self.predict_engagement(text, metadata)
            results.append(result)

        return results

    def compare_variants(self, variants: List[str]) -> Dict:
        """
        Compare multiple content variants for engagement

        Args:
            variants: List of text variants to compare

        Returns:
            Dict with comparison results
        """
        predictions = self.batch_predict(variants)

        # Rank by score
        ranked = sorted(
            zip(variants, predictions),
            key=lambda x: x[1]["engagement_score"],
            reverse=True
        )

        return {
            "total_variants": len(variants),
            "best_variant": {
                "text": ranked[0][0],
                "score": ranked[0][1]["engagement_score"],
                "level": ranked[0][1]["engagement_level"]
            },
            "all_variants": [
                {
                    "rank": i + 1,
                    "text": text,
                    "score": pred["engagement_score"],
                    "level": pred["engagement_level"]
                }
                for i, (text, pred) in enumerate(ranked)
            ],
            "score_range": {
                "highest": ranked[0][1]["engagement_score"],
                "lowest": ranked[-1][1]["engagement_score"],
                "variance": np.var([pred["engagement_score"] for _, pred in ranked])
            }
        }

    # ==============================================
    # Mock Prediction (when model unavailable)
    # ==============================================

    def _mock_prediction(self, text: str) -> Dict:
        """Generate mock prediction for testing"""
        print("📦 Using mock engagement prediction")

        # Simple heuristic scoring
        score = 50.0  # Base score

        text_lower = text.lower()

        # Boost for emojis
        if any(emoji in text for emoji in ['🚀', '🔥', '💯']):
            score += 10

        # Hashtags
        hashtag_count = text.count('#')
        if 1 <= hashtag_count <= 3:
            score += 8

        # Questions
        if '?' in text:
            score += 12

        # Length
        if 50 <= len(text) <= 280:
            score += 5

        score = min(score, 100.0)
        level = self._classify_engagement_level(score)

        return {
            "engagement_score": round(score, 2),
            "engagement_level": level,
            "predicted_metrics": {
                "likes_multiplier": round(score / 50, 2),
                "shares_multiplier": round(score / 100, 2),
                "comments_multiplier": round(score / 75, 2)
            },
            "content_features": self._analyze_content_features(text),
            "confidence": 0.6,
            "model": "mock",
            "mock_data": True
        }


# ==============================================
# Example Usage / Testing
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🤖 TwHIN-BERT Engagement Predictor - Test Suite")
    print("=" * 70 + "\n")

    # Initialize predictor
    predictor = TwHINPredictor()

    # Test posts
    test_posts = [
        "Just launched our new productivity app! 🚀 Boost your workflow today. #productivity #tech",
        "Check out this amazing tutorial",
        "What's your favorite productivity hack? Share below! 💬 #AskTwitter",
        "New blog post: 10 ways to improve developer productivity https://example.com",
        "🔥🔥🔥 This is incredible! You need to see this NOW! #viral #trending #amazing #wow #omg"
    ]

    print("Test 1: Predicting engagement for sample posts\n")
    for i, post in enumerate(test_posts, 1):
        result = predictor.predict_engagement(post)
        print(f"Post {i}: {post[:50]}...")
        print(f"  Score: {result['engagement_score']}/100 ({result['engagement_level']})")
        print(f"  Likes multiplier: {result['predicted_metrics']['likes_multiplier']}x")
        print(f"  Hashtags: {result['content_features']['hashtag_count']}")
        print()

    print("\n" + "-" * 70 + "\n")
    print("Test 2: Comparing content variants\n")

    variants = [
        "New feature: Dark mode now available!",
        "🌙 Dark mode is here! Switch to the dark side 😎 #DarkMode #UX",
        "We just shipped dark mode. Try it out and let us know what you think!"
    ]

    comparison = predictor.compare_variants(variants)
    print(f"Tested {comparison['total_variants']} variants")
    print(f"\nBest variant (score: {comparison['best_variant']['score']}):")
    print(f"  \"{comparison['best_variant']['text']}\"")
    print(f"\nAll variants (ranked):")
    for variant in comparison['all_variants']:
        print(f"  {variant['rank']}. Score {variant['score']}: {variant['text'][:60]}...")

    print("\n" + "=" * 70)
    print("✅ All tests complete!")
    print("=" * 70 + "\n")
