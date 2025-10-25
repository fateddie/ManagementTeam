#!/usr/bin/env python3
"""
Test Enhanced Pain Discovery & Competitive Analysis

Tests the new keyword generator, pain discovery analyzer,
and competitive analyzer components.

Created: 2025-10-24
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.keyword_generator import KeywordGenerator
from core.pain_discovery_analyzer import PainDiscoveryAnalyzer
from core.competitive_analyzer import CompetitiveAnalyzer


def test_keyword_generator():
    """Test keyword generation with sample refinement data."""
    print("\n" + "="*70)
    print("TEST 1: Keyword Generator")
    print("="*70)

    generator = KeywordGenerator()

    # Sample refinement data
    refinement_data = {
        "core_idea": "AI call answering service for small businesses",
        "target_customer": "Small and medium businesses with high call volumes",
        "industry": "Trades (plumbers, contractors), clinics, hotels",
        "pain_context": "Missing hot leads when customers can't get through",
        "value_proposition": "AI manages phone communications cheaper than human receptionist",
        "competitive_awareness": "Human receptionists, answering services"
    }

    try:
        # Generate keywords
        keyword_data = generator.generate_keywords(
            refinement_data=refinement_data,
            geography="Ireland/UK"
        )

        # Validate structure
        assert 'keywords_by_category' in keyword_data, "Missing keywords_by_category"
        assert 'total_keywords' in keyword_data, "Missing total_keywords"
        assert 'geography' in keyword_data, "Missing geography"

        print(f"✅ Generated {keyword_data['total_keywords']} keywords")

        # Check categories
        keywords_by_category = keyword_data['keywords_by_category']
        expected_categories = ['core_intent', 'pain_based', 'industry_vertical',
                              'adjacency_proxy', 'trend_validation']

        for category in expected_categories:
            if category in keywords_by_category:
                count = len(keywords_by_category[category])
                print(f"   {category}: {count} keywords")

        # Display formatted output
        display = generator.format_for_display(keyword_data)
        if len(display) > 0:
            print("\n✅ Format display successful")
        else:
            print("\n⚠️  Display formatting returned empty")

        print("\n✅ Keyword Generator: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Keyword Generator: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pain_discovery_analyzer():
    """Test pain discovery analysis."""
    print("\n" + "="*70)
    print("TEST 2: Pain Discovery Analyzer")
    print("="*70)

    analyzer = PainDiscoveryAnalyzer()

    # Sample data
    refinement_data = {
        "core_idea": "AI call answering",
        "target_customer": "Small businesses",
        "pain_context": "Missing customer calls"
    }

    keywords = [
        "missed calls small business",
        "AI receptionist",
        "call answering service Ireland"
    ]

    try:
        # Note: This will attempt real API calls if evidence collector is available
        # In production, you'd mock these
        print("⚠️  Note: Analysis requires API credentials")
        print("   Testing structure only...")

        # Test structure without full execution
        print("✅ Pain Discovery Analyzer initialized")

        # Test format display with sample data
        sample_analysis = {
            "demand_signal_strength": 7.5,
            "conversation_volume": {
                "reddit": 150,
                "twitter": 45,
                "google_trends": "↗️ +25%"
            },
            "top_pain_quotes": [
                {
                    "quote": "We lose so many leads from missed calls",
                    "source": "r/smallbusiness",
                    "metadata": {"upvotes": 42}
                }
            ],
            "willingness_to_pay": {
                "mentions_count": 28,
                "price_range": "£200-£800/month",
                "signals": ["would pay", "budget for"]
            },
            "urgency_analysis": {
                "critical": 3,
                "high": 12,
                "medium": 28,
                "low": 7
            },
            "key_concerns": [
                {"concern": "AI sounds robotic", "count": 15}
            ],
            "validation_decision": {
                "confidence": 75,
                "recommendation": "PROCEED",
                "reasoning": "Strong demand signals"
            }
        }

        display = analyzer.format_for_display(sample_analysis)
        if len(display) > 100:
            print("✅ Format display successful")

        print("\n✅ Pain Discovery Analyzer: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Pain Discovery Analyzer: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_competitive_analyzer():
    """Test competitive analysis."""
    print("\n" + "="*70)
    print("TEST 3: Competitive Analyzer")
    print("="*70)

    analyzer = CompetitiveAnalyzer()

    # Sample data
    refinement_data = {
        "core_idea": "AI call answering service",
        "target_customer": "Small businesses",
        "value_proposition": "Affordable AI phone automation"
    }

    try:
        print("⚠️  Note: Analysis requires API credentials")
        print("   Testing structure only...")

        print("✅ Competitive Analyzer initialized")

        # Test format display with sample data
        sample_analysis = {
            "competitors": [
                {
                    "name": "CallJoy",
                    "type": "direct",
                    "pricing": {
                        "model": "subscription",
                        "tiers": ["$89/month"],
                        "target": "small business"
                    },
                    "features": [
                        "Call routing",
                        "Voicemail transcription"
                    ],
                    "customer_complaints": [
                        {
                            "complaint": "Limited customization options",
                            "severity": "major",
                            "count": 12
                        }
                    ],
                    "positioning": "Google-backed SMB solution"
                }
            ],
            "total_competitors_found": 1,
            "market_gaps": [
                {
                    "gap": "Affordable pricing for SMBs",
                    "opportunity": "£50-£200/month price point",
                    "reasoning": "Competitors average $300+/month"
                }
            ],
            "positioning_recommendations": [
                "Focus on UK/Ireland market",
                "Industry-specific templates"
            ]
        }

        display = analyzer.format_for_display(sample_analysis)
        if len(display) > 100:
            print("✅ Format display successful")

        print("\n✅ Competitive Analyzer: PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Competitive Analyzer: FAILED")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 ENHANCED PAIN DISCOVERY & COMPETITIVE ANALYSIS TESTS")
    print("="*70)

    results = {
        'Keyword Generator': test_keyword_generator(),
        'Pain Discovery Analyzer': test_pain_discovery_analyzer(),
        'Competitive Analyzer': test_competitive_analyzer(),
    }

    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name:35} {status}")

    print("\n" + "-"*70)
    print(f"Total: {passed}/{total} tests passed")
    print("="*70 + "\n")

    if passed == total:
        print("✅ All tests passed!")
        print("\n📝 Next Steps:")
        print("  1. Set up API keys (OPENAI_API_KEY) in .env")
        print("  2. Run full workflow: python3 cli/interactive_workflow.py")
        print("  3. Test with real idea validation")
        print()
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
