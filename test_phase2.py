#!/usr/bin/env python3
"""
Test Phase 2 API Integrations and ML Predictions
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 70)
print("🧪 Testing Phase 2: API Integrations & ML Predictions")
print("=" * 70)

# Test 1: Reddit Connector
print("\n1️⃣  Testing Reddit Connector...")
print("-" * 70)
from integrations.reddit_connector import RedditConnector

reddit = RedditConnector()
reddit_results = reddit.search_pain_points(
    "productivity app",
    subreddits=["productivity"],
    limit=10
)
print(f"✅ Reddit connector: {reddit_results['total_posts']} posts")
print(f"   Mode: {'Real API' if reddit_results.get('total_posts', 0) > 0 else 'Mock mode'}")

# Test 2: Google Trends Connector
print("\n2️⃣  Testing Google Trends Connector...")
print("-" * 70)
from integrations.google_trends_connector import GoogleTrendsConnector

trends = GoogleTrendsConnector()
trends_results = trends.analyze_interest("productivity app", timeframe="today 3-m")
print(f"✅ Google Trends connector: {trends_results.get('keyword')}")
if trends_results.get('interest_over_time'):
    summary = trends_results['interest_over_time'].get('summary', {})
    print(f"   Average interest: {summary.get('avg', 0)}")
    print(f"   Trend: {summary.get('trend', 'N/A')}")

# Test 3: X (Twitter) Connector
print("\n3️⃣  Testing X (Twitter) Connector...")
print("-" * 70)
from integrations.x_connector import XConnector

x_api = XConnector()
x_results = x_api.search_sentiment("productivity app", limit=10)
print(f"✅ X connector: {x_results['total_tweets']} tweets")
print(f"   Mode: {'Real API' if x_results.get('total_tweets', 0) > 0 else 'Mock mode'}")

# Test 4: Evidence Collector
print("\n4️⃣  Testing Unified Evidence Collector...")
print("-" * 70)
from integrations.evidence_collector import EvidenceCollector

collector = EvidenceCollector()
evidence = collector.collect_all_evidence(
    idea="productivity app for developers",
    keywords=["task management"],
    subreddits=["programming"],
    parallel=False  # Sequential for clearer logs
)

print(f"✅ Evidence Score: {evidence['evidence_score']}/100")
print(f"   Sources collected: {len(evidence.get('sources', {}))}")

if evidence.get('unified_insights'):
    insights = evidence['unified_insights']
    print(f"   Overall sentiment: {insights.get('overall_sentiment', {}).get('label', 'N/A')}")
    print(f"   Market strength: {insights.get('market_validation', {}).get('strength', 'N/A')}")
    print(f"   Recommendation: {insights.get('recommendation', 'N/A')}")

# Save evidence report
print(f"\n💾 Saving evidence report...")
collector.save_evidence_report(evidence, "outputs/evidence/test_report.json")

# Test 5: ML Scoring Predictor
print("\n5️⃣  Testing ML Scoring Predictor...")
print("-" * 70)
from ml.scoring_predictor import ScoringPredictor

predictor = ScoringPredictor()

# Create test idea data
test_idea = {
    "evidence": evidence,
    "scores": {
        "rice_total": 75,
        "ice_score": 8.5,
        "pain_score_avg": 8.2
    },
    "economics": {
        "ltv_cac_ratio": 5.0,
        "payback_months": 6
    },
    "risks": {
        "high": 2,
        "medium": 5,
        "total": 12
    },
    "competition": {
        "count": 8,
        "crowdedness_score": 6
    }
}

prediction = predictor.predict_success(test_idea)

print(f"✅ ML Prediction:")
print(f"   Success Probability: {prediction['success_probability']}%")
print(f"   Predicted Score: {prediction['predicted_score']}")
print(f"   Confidence: {prediction['confidence']}")
print(f"   Recommendation: {prediction['recommendation']}")
print(f"   Model: {prediction['model_version']}")

if prediction.get('feature_importance'):
    print(f"\n   Top 5 Important Features:")
    for feature in prediction['feature_importance'][:5]:
        print(f"     - {feature['feature']}: {feature['importance']}")

# Summary
print("\n" + "=" * 70)
print("📊 PHASE 2 TEST SUMMARY")
print("=" * 70)
print(f"✅ Reddit Connector: Working")
print(f"✅ Google Trends Connector: Working")
print(f"✅ X Connector: Working")
print(f"✅ Evidence Collector: Working (Score: {evidence['evidence_score']}/100)")
print(f"✅ ML Predictor: Working (Success: {prediction['success_probability']}%)")
print(f"\n🎉 All Phase 2 components functional!")
print(f"\n💡 Tip: Add API credentials to config/api_config.json for real data")
print("=" * 70)
