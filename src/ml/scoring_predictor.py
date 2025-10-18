#!/usr/bin/env python3
"""
ML-Based Scoring Predictor
Uses machine learning to predict idea success probability based on historical data.

Features:
- Multi-factor scoring model
- Historical pattern recognition
- Success rate prediction
- Feature importance analysis
- Continuous learning from outcomes

Usage:
    from src.ml.scoring_predictor import ScoringPredictor

    predictor = ScoringPredictor()
    prediction = predictor.predict_success(idea_features)
"""

import json
import pickle
from typing import Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  Warning: scikit-learn not installed. Install with: pip install scikit-learn")


class ScoringPredictor:
    """ML-based idea scoring and success prediction"""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize ML predictor

        Args:
            model_path: Path to saved model (optional)
        """
        self.model_path = model_path or "data/ml_models/scoring_model.pkl"
        self.scaler_path = model_path.replace(".pkl", "_scaler.pkl") if model_path else "data/ml_models/scoring_scaler.pkl"

        self.classifier = None
        self.regressor = None
        self.scaler = None
        self.feature_names = None

        if SKLEARN_AVAILABLE:
            self._init_models()
        else:
            print("⚠️  ML predictions disabled - scikit-learn not available")

    def _init_models(self):
        """Initialize or load models"""
        model_file = Path(self.model_path)
        scaler_file = Path(self.scaler_path)

        if model_file.exists() and scaler_file.exists():
            try:
                self.classifier = joblib.load(model_file)
                self.regressor = joblib.load(model_file.with_name(model_file.stem + "_regressor.pkl"))
                self.scaler = joblib.load(scaler_file)
                print("✅ ML models loaded")
            except Exception as e:
                print(f"⚠️  Failed to load models: {e}")
                self._create_default_models()
        else:
            self._create_default_models()

    def _create_default_models(self):
        """Create default untrained models"""
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.regressor = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42
        )
        self.scaler = StandardScaler()
        print("✅ Default ML models created (untrained)")

    def extract_features(self, idea_data: Dict) -> Dict[str, float]:
        """
        Extract ML features from idea data

        Args:
            idea_data: Complete idea data with evidence and scores

        Returns:
            Dict of numerical features
        """
        features = {}

        # Evidence-based features
        evidence = idea_data.get('evidence', {})
        features['evidence_score'] = evidence.get('evidence_score', 0) / 100

        # Reddit features
        reddit = evidence.get('sources', {}).get('reddit', {})
        features['reddit_posts'] = min(reddit.get('total_posts', 0), 200) / 200
        features['reddit_pain_points'] = min(len(reddit.get('pain_points', [])), 50) / 50
        features['reddit_sentiment'] = (reddit.get('sentiment', {}).get('avg_polarity', 0) + 1) / 2

        # Google Trends features
        trends = evidence.get('sources', {}).get('google_trends', {})
        interest = trends.get('interest_summary', {})
        features['trends_avg_interest'] = interest.get('avg', 0) / 100
        features['trends_current_interest'] = interest.get('current', 0) / 100

        trend_map = {'rising': 1.0, 'stable': 0.5, 'declining': 0.0}
        features['trends_direction'] = trend_map.get(interest.get('trend', 'stable'), 0.5)

        # X (Twitter) features
        x_data = evidence.get('sources', {}).get('x', {})
        features['x_tweets'] = min(x_data.get('total_tweets', 0), 200) / 200
        x_sentiment = x_data.get('sentiment', {}).get('avg_polarity', 0)
        features['x_sentiment'] = (x_sentiment + 1) / 2
        features['x_engagement'] = min(x_data.get('sentiment', {}).get('total_engagement', 0), 10000) / 10000

        # Scoring features
        scores = idea_data.get('scores', {})
        features['rice_score'] = scores.get('rice_total', 0) / 100
        features['ice_score'] = scores.get('ice_score', 0) / 10
        features['pain_score'] = scores.get('pain_score_avg', 0) / 10

        # Economic features
        economics = idea_data.get('economics', {})
        features['ltv_cac_ratio'] = min(economics.get('ltv_cac_ratio', 0), 10) / 10
        payback = economics.get('payback_months', 12)
        features['payback_months_normalized'] = max(0, 1 - (payback / 24))  # Lower is better

        # Risk features
        risks = idea_data.get('risks', {})
        features['risk_high'] = min(risks.get('high', 0), 5) / 5
        features['risk_medium'] = min(risks.get('medium', 0), 10) / 10
        features['risk_total'] = min(risks.get('total', 0), 20) / 20

        # Competitive features
        competition = idea_data.get('competition', {})
        features['competitors_count'] = min(competition.get('count', 0), 20) / 20
        features['market_crowdedness'] = competition.get('crowdedness_score', 5) / 10

        self.feature_names = list(features.keys())
        return features

    def predict_success(self, idea_data: Dict) -> Dict:
        """
        Predict success probability and score for an idea

        Args:
            idea_data: Complete idea data

        Returns:
            Dict with predictions and confidence
        """
        if not SKLEARN_AVAILABLE or self.classifier is None:
            return self._mock_prediction(idea_data)

        print("\n🤖 Running ML prediction...")

        # Extract features
        features = self.extract_features(idea_data)
        feature_vector = np.array([list(features.values())]).reshape(1, -1)

        # Scale features
        try:
            feature_vector_scaled = self.scaler.transform(feature_vector)
        except:
            # If scaler not fitted, use raw features
            feature_vector_scaled = feature_vector

        # Predict
        try:
            # Classification: success/failure
            if hasattr(self.classifier, 'predict_proba'):
                success_proba = self.classifier.predict_proba(feature_vector_scaled)[0]
                success_probability = success_proba[1] if len(success_proba) > 1 else 0.5
            else:
                success_probability = 0.5

            # Regression: predicted score
            if hasattr(self.regressor, 'predict'):
                predicted_score = self.regressor.predict(feature_vector_scaled)[0]
                predicted_score = max(0, min(100, predicted_score))
            else:
                predicted_score = 50.0

        except Exception as e:
            print(f"⚠️  Prediction error: {e}")
            return self._mock_prediction(idea_data)

        # Calculate feature importance
        feature_importance = self._calculate_feature_importance(features)

        # Generate confidence
        confidence = self._calculate_confidence(feature_vector_scaled, features)

        prediction = {
            "success_probability": round(success_probability * 100, 1),
            "predicted_score": round(predicted_score, 1),
            "confidence": round(confidence, 2),
            "recommendation": self._generate_ml_recommendation(success_probability, predicted_score),
            "feature_importance": feature_importance,
            "model_version": "1.0",
            "features_used": len(features),
            "predicted_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }

        print(f"✅ Prediction complete - Success probability: {prediction['success_probability']}%")

        return prediction

    def _calculate_feature_importance(self, features: Dict[str, float]) -> List[Dict]:
        """Calculate importance of each feature"""
        if not hasattr(self.classifier, 'feature_importances_'):
            return []

        try:
            importances = self.classifier.feature_importances_
            feature_importance = [
                {
                    "feature": name,
                    "importance": round(float(imp), 3),
                    "value": round(val, 3)
                }
                for name, imp, val in zip(self.feature_names or features.keys(), importances, features.values())
            ]

            # Sort by importance
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)

            return feature_importance[:10]  # Top 10

        except Exception as e:
            print(f"⚠️  Feature importance calculation failed: {e}")
            return []

    def _calculate_confidence(self, feature_vector: np.ndarray, features: Dict) -> float:
        """Calculate prediction confidence"""
        # Based on feature completeness and model certainty
        feature_completeness = sum(1 for v in features.values() if v > 0) / len(features)

        # If we have probability distribution, use entropy
        if hasattr(self.classifier, 'predict_proba'):
            try:
                proba = self.classifier.predict_proba(feature_vector)[0]
                # Lower entropy = higher confidence
                entropy = -sum(p * np.log(p + 1e-10) for p in proba)
                max_entropy = np.log(len(proba))
                confidence = (1 - entropy / max_entropy) if max_entropy > 0 else 0.5
            except:
                confidence = 0.5
        else:
            confidence = 0.5

        # Combine with feature completeness
        final_confidence = (confidence * 0.7 + feature_completeness * 0.3)

        return final_confidence

    def _generate_ml_recommendation(self, success_prob: float, predicted_score: float) -> str:
        """Generate recommendation based on ML prediction"""
        if success_prob > 0.75 and predicted_score > 70:
            return "🚀 HIGH CONFIDENCE GO - ML model predicts strong success"
        elif success_prob > 0.6 and predicted_score > 60:
            return "✅ GO - Model shows positive indicators"
        elif success_prob > 0.45 and predicted_score > 50:
            return "🟡 CONDITIONAL GO - Mixed ML signals, validate further"
        elif success_prob < 0.35 or predicted_score < 40:
            return "❌ NO GO - Model predicts low success probability"
        else:
            return "⚠️ UNCERTAIN - Model confidence low, gather more data"

    def train_model(self, training_data: List[Dict]):
        """
        Train the ML model on historical data

        Args:
            training_data: List of idea data with outcomes
        """
        if not SKLEARN_AVAILABLE:
            print("❌ Cannot train - scikit-learn not available")
            return

        print(f"\n🎓 Training ML model on {len(training_data)} examples...")

        # Extract features and labels
        X = []
        y_class = []  # Success/failure
        y_score = []  # Final score

        for idea in training_data:
            features = self.extract_features(idea)
            X.append(list(features.values()))

            # Labels
            outcome = idea.get('outcome', {})
            y_class.append(1 if outcome.get('success', False) else 0)
            y_score.append(outcome.get('final_score', 50))

        X = np.array(X)
        y_class = np.array(y_class)
        y_score = np.array(y_score)

        # Split data
        X_train, X_test, y_class_train, y_class_test, y_score_train, y_score_test = train_test_split(
            X, y_class, y_score, test_size=0.2, random_state=42
        )

        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train classifier
        self.classifier.fit(X_train_scaled, y_class_train)
        class_score = self.classifier.score(X_test_scaled, y_class_test)

        # Train regressor
        self.regressor.fit(X_train_scaled, y_score_train)
        reg_score = self.regressor.score(X_test_scaled, y_score_test)

        print(f"✅ Training complete")
        print(f"  Classification accuracy: {class_score:.2%}")
        print(f"  Regression R²: {reg_score:.2f}")

        # Save models
        self._save_models()

    def _save_models(self):
        """Save trained models"""
        model_file = Path(self.model_path)
        model_file.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(self.classifier, model_file)
        joblib.dump(self.regressor, model_file.with_name(model_file.stem + "_regressor.pkl"))
        joblib.dump(self.scaler, self.scaler_path)

        print(f"💾 Models saved to {model_file.parent}")

    def _mock_prediction(self, idea_data: Dict) -> Dict:
        """Return mock prediction when ML is not available"""
        # Simple heuristic-based prediction
        evidence_score = idea_data.get('evidence', {}).get('evidence_score', 50)
        rice_score = idea_data.get('scores', {}).get('rice_total', 50)

        avg_score = (evidence_score + rice_score) / 2
        success_prob = min(95, max(5, avg_score))

        return {
            "success_probability": round(success_prob, 1),
            "predicted_score": round(avg_score, 1),
            "confidence": 0.5,
            "recommendation": self._generate_ml_recommendation(success_prob / 100, avg_score),
            "feature_importance": [],
            "model_version": "heuristic",
            "features_used": 0,
            "predicted_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "note": "Mock prediction - ML not available"
        }


if __name__ == "__main__":
    # Test the predictor
    predictor = ScoringPredictor()

    # Mock idea data
    test_idea = {
        "evidence": {
            "evidence_score": 75,
            "sources": {
                "reddit": {"total_posts": 50, "pain_points": ["problem1", "problem2"], "sentiment": {"avg_polarity": 0.2}},
                "google_trends": {"interest_summary": {"avg": 60, "current": 70, "trend": "rising"}},
                "x": {"total_tweets": 80, "sentiment": {"avg_polarity": 0.3, "total_engagement": 500}}
            }
        },
        "scores": {"rice_total": 65, "ice_score": 7.5, "pain_score_avg": 8.2},
        "economics": {"ltv_cac_ratio": 4.5, "payback_months": 6},
        "risks": {"high": 2, "medium": 5, "total": 12},
        "competition": {"count": 8, "crowdedness_score": 6}
    }

    prediction = predictor.predict_success(test_idea)

    print(f"\n📊 ML Prediction Results:")
    print(f"  Success Probability: {prediction['success_probability']}%")
    print(f"  Predicted Score: {prediction['predicted_score']}")
    print(f"  Confidence: {prediction['confidence']}")
    print(f"  Recommendation: {prediction['recommendation']}")
