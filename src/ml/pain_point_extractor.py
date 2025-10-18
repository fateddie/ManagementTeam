#!/usr/bin/env python3
"""
Pain Point Extractor
Extracts customer pain points, problems, and frustrations from social media text.

Features:
- Named Entity Recognition (NER) for product/feature mentions
- Sentiment analysis for frustration detection
- Keyword extraction for pain point identification
- Problem categorization (performance, UX, pricing, features, etc.)
- Severity scoring based on emotional intensity

Models Used:
- dslim/bert-base-NER (entity extraction)
- cardiffnlp/twitter-roberta-base-sentiment (sentiment)
- Zero-shot classification for problem categories

Usage:
    from src.ml.pain_point_extractor import PainPointExtractor

    extractor = PainPointExtractor()
    pain_points = extractor.extract_pain_points(
        "This app is so slow! It crashes every time I try to export data. Very frustrating."
    )
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from collections import Counter
from pathlib import Path

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  Warning: transformers not installed. Install with: pip install transformers torch")


class PainPointExtractor:
    """
    Extract and analyze customer pain points from social media text

    Uses NER + sentiment + keyword extraction to identify customer problems,
    frustrations, and areas for product improvement.
    """

    # Models
    NER_MODEL = "dslim/bert-base-NER"
    SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
    CLASSIFIER_MODEL = "facebook/bart-large-mnli"

    # Pain point keywords (ranked by intensity)
    PAIN_KEYWORDS = {
        "high": [
            "hate", "terrible", "awful", "worst", "unusable", "broken",
            "crash", "bug", "error", "fail", "nightmare", "frustrating",
            "useless", "waste", "disappointed", "angry", "furious"
        ],
        "medium": [
            "difficult", "hard", "slow", "confusing", "complicated",
            "annoying", "inconvenient", "issue", "problem", "trouble",
            "struggle", "challenging", "unclear", "missing", "lacking"
        ],
        "low": [
            "would like", "wish", "hope", "prefer", "better if",
            "improve", "enhance", "could be", "needs", "want"
        ]
    }

    # Problem categories for classification
    PROBLEM_CATEGORIES = [
        "performance issue",      # Slow, laggy, crashes
        "usability problem",      # Confusing UI, hard to use
        "missing feature",        # Feature requests
        "pricing concern",        # Too expensive, billing issues
        "integration problem",    # Doesn't work with other tools
        "data issue",             # Data loss, export/import problems
        "reliability issue",      # Crashes, errors, bugs
        "support problem",        # Poor customer service
        "documentation issue"     # Unclear docs, missing info
    ]

    def __init__(self, device: Optional[str] = None):
        """
        Initialize pain point extractor

        Args:
            device: Device to run on ("cpu", "cuda", "mps"). Auto-detected if None.
        """
        self.device = self._get_device(device)
        self.ner_pipeline = None
        self.sentiment_pipeline = None
        self.classifier_pipeline = None
        self.cache = {}

        if TRANSFORMERS_AVAILABLE:
            self._load_models()
        else:
            print("⚠️  Transformers not available. Using keyword-based extraction.")

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

    def _load_models(self):
        """Load required models"""
        try:
            print("📥 Loading pain point extraction models...")

            device_num = 0 if self.device == "cuda" else -1

            # 1. NER for entity extraction
            print(f"  Loading {self.NER_MODEL}...")
            self.ner_pipeline = pipeline(
                "ner",
                model=self.NER_MODEL,
                aggregation_strategy="simple",
                device=device_num
            )

            # 2. Sentiment for frustration detection
            print(f"  Loading {self.SENTIMENT_MODEL}...")
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.SENTIMENT_MODEL,
                device=device_num
            )

            # 3. Zero-shot classifier for problem categorization
            print(f"  Loading {self.CLASSIFIER_MODEL}...")
            self.classifier_pipeline = pipeline(
                "zero-shot-classification",
                model=self.CLASSIFIER_MODEL,
                device=device_num
            )

            print("✅ All models loaded successfully")

        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            self.ner_pipeline = None
            self.sentiment_pipeline = None
            self.classifier_pipeline = None

    def extract_pain_points(self, text: str, context: Optional[Dict] = None) -> Dict:
        """
        Extract pain points from text

        Args:
            text: Text to analyze (post, comment, review)
            context: Optional context (product name, platform, etc.)

        Returns:
            Dict with extracted pain points and analysis
        """
        # Check cache
        cache_key = f"pain_{hash(text)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 1. Extract keywords
        keywords = self._extract_pain_keywords(text)

        # 2. Calculate severity
        severity = self._calculate_severity(text, keywords)

        # 3. Extract entities (products, features mentioned)
        entities = self._extract_entities(text)

        # 4. Analyze sentiment
        sentiment = self._analyze_sentiment(text)

        # 5. Categorize problem type
        problem_type = self._categorize_problem(text)

        # 6. Extract specific problems (sentences containing pain)
        problem_statements = self._extract_problem_statements(text)

        # 7. Generate summary
        summary = self._generate_summary(
            text, keywords, severity, entities, problem_type
        )

        result = {
            "has_pain_point": len(keywords) > 0 or severity > 3,
            "severity_score": severity,  # 0-10 scale
            "severity_level": self._classify_severity(severity),
            "pain_keywords": keywords,
            "entities_mentioned": entities,
            "sentiment": sentiment,
            "problem_category": problem_type,
            "problem_statements": problem_statements,
            "summary": summary,
            "original_text": text,
            "context": context or {}
        }

        self.cache[cache_key] = result
        return result

    def _extract_pain_keywords(self, text: str) -> List[Dict]:
        """Extract pain-related keywords from text"""
        text_lower = text.lower()
        found_keywords = []

        for intensity, keywords in self.PAIN_KEYWORDS.items():
            for keyword in keywords:
                # Use word boundary matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = re.findall(pattern, text_lower)

                for match in matches:
                    found_keywords.append({
                        "keyword": match,
                        "intensity": intensity,
                        "score": {"high": 10, "medium": 6, "low": 3}[intensity]
                    })

        return found_keywords

    def _calculate_severity(self, text: str, keywords: List[Dict]) -> float:
        """Calculate pain point severity (0-10 scale)"""
        if not keywords:
            # Check for ALL CAPS (indicates strong emotion)
            if text.isupper() and len(text) > 10:
                return 5.0  # Moderate severity for shouting
            return 0.0

        # Base score from keywords
        keyword_scores = [kw["score"] for kw in keywords]
        base_score = sum(keyword_scores) / len(keyword_scores)

        # Adjust based on text features
        multiplier = 1.0

        # Multiple exclamation marks
        exclaim_count = text.count('!')
        if exclaim_count >= 3:
            multiplier += 0.3
        elif exclaim_count >= 1:
            multiplier += 0.15

        # ALL CAPS words
        caps_words = sum(1 for word in text.split() if word.isupper() and len(word) > 2)
        if caps_words >= 3:
            multiplier += 0.2

        # Repetition (indicates frustration)
        words = text.lower().split()
        word_freq = Counter(words)
        max_repeat = max(word_freq.values()) if word_freq else 1
        if max_repeat >= 3:
            multiplier += 0.15

        final_score = min(base_score * multiplier, 10.0)
        return round(final_score, 1)

    def _classify_severity(self, score: float) -> str:
        """Classify severity level"""
        if score >= 7.5:
            return "critical"
        elif score >= 5.0:
            return "high"
        elif score >= 2.5:
            return "medium"
        else:
            return "low"

    def _extract_entities(self, text: str) -> List[Dict]:
        """Extract mentioned entities (products, features, companies)"""
        if not self.ner_pipeline:
            # Fallback: simple capitalized word extraction
            return self._simple_entity_extraction(text)

        try:
            entities = self.ner_pipeline(text[:512])  # Limit length

            # Filter and format
            formatted_entities = []
            for entity in entities:
                formatted_entities.append({
                    "text": entity["word"],
                    "type": entity["entity_group"],
                    "confidence": round(entity["score"], 2)
                })

            return formatted_entities

        except Exception as e:
            print(f"⚠️  NER error: {e}")
            return self._simple_entity_extraction(text)

    def _simple_entity_extraction(self, text: str) -> List[Dict]:
        """Simple entity extraction fallback"""
        # Extract capitalized words (likely product/company names)
        words = text.split()
        entities = []

        for word in words:
            # Remove punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)

            # Check if capitalized and not at sentence start
            if clean_word and clean_word[0].isupper() and len(clean_word) > 2:
                entities.append({
                    "text": clean_word,
                    "type": "MISC",
                    "confidence": 0.5
                })

        return entities[:10]  # Limit to top 10

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment for frustration detection"""
        if not self.sentiment_pipeline:
            return {"label": "NEGATIVE" if any(kw in text.lower() for kw in self.PAIN_KEYWORDS["high"]) else "NEUTRAL", "score": 0.6}

        try:
            result = self.sentiment_pipeline(text[:512])[0]
            return {
                "label": result["label"],
                "score": round(result["score"], 2)
            }
        except Exception as e:
            print(f"⚠️  Sentiment error: {e}")
            return {"label": "NEUTRAL", "score": 0.5}

    def _categorize_problem(self, text: str) -> Dict:
        """Categorize problem type using zero-shot classification"""
        if not self.classifier_pipeline:
            return self._simple_categorization(text)

        try:
            result = self.classifier_pipeline(
                text[:512],
                candidate_labels=self.PROBLEM_CATEGORIES
            )

            return {
                "category": result["labels"][0],
                "confidence": round(result["scores"][0], 2),
                "all_categories": list(zip(result["labels"][:3], result["scores"][:3]))
            }

        except Exception as e:
            print(f"⚠️  Classification error: {e}")
            return self._simple_categorization(text)

    def _simple_categorization(self, text: str) -> Dict:
        """Simple problem categorization fallback"""
        text_lower = text.lower()

        # Keyword mapping
        category_keywords = {
            "performance issue": ["slow", "lag", "freeze", "crash", "hang"],
            "usability problem": ["confusing", "unclear", "hard to use", "complicated"],
            "missing feature": ["wish", "would like", "missing", "need", "want"],
            "reliability issue": ["crash", "error", "bug", "broken", "fail"],
            "pricing concern": ["expensive", "price", "cost", "billing", "payment"]
        }

        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score

        if scores:
            top_category = max(scores, key=scores.get)
            return {
                "category": top_category,
                "confidence": 0.6,
                "all_categories": [(cat, score/10) for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]]
            }
        else:
            return {
                "category": "general issue",
                "confidence": 0.5,
                "all_categories": []
            }

    def _extract_problem_statements(self, text: str) -> List[str]:
        """Extract specific problem statements from text"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)

        problem_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Check if sentence contains pain keywords
            sentence_lower = sentence.lower()
            has_pain = any(
                keyword in sentence_lower
                for intensity_keywords in self.PAIN_KEYWORDS.values()
                for keyword in intensity_keywords
            )

            if has_pain:
                problem_sentences.append(sentence)

        return problem_sentences

    def _generate_summary(
        self,
        text: str,
        keywords: List[Dict],
        severity: float,
        entities: List[Dict],
        problem_type: Dict
    ) -> str:
        """Generate human-readable summary"""
        if severity == 0:
            return "No significant pain points detected."

        severity_level = self._classify_severity(severity)
        category = problem_type.get("category", "general issue")

        # Build summary
        summary_parts = []

        # Severity
        summary_parts.append(f"{severity_level.capitalize()} severity {category}")

        # Entities mentioned
        if entities:
            entity_names = [e["text"] for e in entities[:3]]
            summary_parts.append(f"regarding {', '.join(entity_names)}")

        # Top pain keywords
        if keywords:
            top_keywords = sorted(keywords, key=lambda k: k["score"], reverse=True)[:3]
            keyword_list = [k["keyword"] for k in top_keywords]
            summary_parts.append(f"(keywords: {', '.join(keyword_list)})")

        return " ".join(summary_parts)

    def batch_extract(self, texts: List[str]) -> List[Dict]:
        """Extract pain points from multiple texts"""
        return [self.extract_pain_points(text) for text in texts]

    def aggregate_pain_points(self, results: List[Dict]) -> Dict:
        """Aggregate pain points from multiple extractions"""
        total_texts = len(results)
        texts_with_pain = sum(1 for r in results if r["has_pain_point"])

        # Collect all keywords
        all_keywords = []
        for result in results:
            all_keywords.extend([kw["keyword"] for kw in result["pain_keywords"]])

        keyword_freq = Counter(all_keywords)

        # Collect all problem categories
        all_categories = [r["problem_category"]["category"] for r in results]
        category_freq = Counter(all_categories)

        # Calculate average severity
        severities = [r["severity_score"] for r in results if r["has_pain_point"]]
        avg_severity = sum(severities) / len(severities) if severities else 0

        return {
            "total_analyzed": total_texts,
            "texts_with_pain_points": texts_with_pain,
            "pain_point_percentage": round((texts_with_pain / total_texts) * 100, 1) if total_texts > 0 else 0,
            "average_severity": round(avg_severity, 1),
            "top_pain_keywords": keyword_freq.most_common(20),
            "top_problem_categories": category_freq.most_common(10),
            "severity_distribution": {
                "critical": sum(1 for r in results if r["severity_level"] == "critical"),
                "high": sum(1 for r in results if r["severity_level"] == "high"),
                "medium": sum(1 for r in results if r["severity_level"] == "medium"),
                "low": sum(1 for r in results if r["severity_level"] == "low")
            }
        }


# ==============================================
# Example Usage / Testing
# ==============================================
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("💬 Pain Point Extractor - Test Suite")
    print("=" * 70 + "\n")

    extractor = PainPointExtractor()

    # Test texts
    test_texts = [
        "This app is so slow! It crashes every time I try to export data. Very frustrating.",
        "The UI is confusing. I can't figure out where to find the settings.",
        "I wish this had dark mode. Would make it much better.",
        "Love this app! Works perfectly for my needs.",
        "TERRIBLE! Keeps losing my data. This is UNACCEPTABLE!!!",
        "Would be nice if it integrated with Slack. Otherwise pretty good."
    ]

    print("Test 1: Extracting pain points from individual texts\n")
    results = []
    for i, text in enumerate(test_texts, 1):
        result = extractor.extract_pain_points(text)
        results.append(result)

        print(f"Text {i}: {text[:60]}...")
        print(f"  Has pain point: {result['has_pain_point']}")
        print(f"  Severity: {result['severity_score']}/10 ({result['severity_level']})")
        print(f"  Category: {result['problem_category']['category']}")
        print(f"  Keywords: {', '.join([kw['keyword'] for kw in result['pain_keywords'][:3]])}")
        print(f"  Summary: {result['summary']}")
        print()

    print("\n" + "-" * 70 + "\n")
    print("Test 2: Aggregating pain points\n")

    aggregated = extractor.aggregate_pain_points(results)
    print(f"Analyzed {aggregated['total_analyzed']} texts")
    print(f"Pain points found in {aggregated['texts_with_pain_points']} texts ({aggregated['pain_point_percentage']}%)")
    print(f"Average severity: {aggregated['average_severity']}/10")
    print(f"\nTop pain keywords:")
    for keyword, count in aggregated['top_pain_keywords'][:5]:
        print(f"  - {keyword}: {count} mentions")
    print(f"\nTop problem categories:")
    for category, count in aggregated['top_problem_categories'][:5]:
        print(f"  - {category}: {count} occurrences")

    print("\n" + "=" * 70)
    print("✅ All tests complete!")
    print("=" * 70 + "\n")
