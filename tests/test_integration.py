#!/usr/bin/env python3
"""
Test integration of v4 enhanced collector with pain discovery analyzer.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.pain_discovery_analyzer import PainDiscoveryAnalyzer

print("="*80)
print("🧪 TESTING ENHANCED PAIN DISCOVERY INTEGRATION")
print("="*80)

# Test data
refinement_data = {
    "core_idea": "AI receptionist that prevents businesses from missing calls",
    "target_customer": "small to medium businesses with high call volumes",
    "industry": "dental, medical, legal, service businesses"
}

# Initialize analyzer
print("\n📋 Step 1: Initializing Pain Discovery Analyzer...")
analyzer = PainDiscoveryAnalyzer()

# Use same keywords we tested with
keywords = ["virtual receptionist", "AI receptionist", "call answering service"]

print(f"\n📋 Step 2: Running analysis with {len(keywords)} keywords...")

# Run analysis
try:
    results = analyzer.analyze_pain_discovery(
        keywords=keywords,
        refinement_data=refinement_data,
        use_v2=True,
        geography="Ireland/UK"
    )

    print("\n✅ Analysis complete!")

    # Check enriched data
    if 'enriched_analysis' in results:
        print("\n📊 ENRICHED INSIGHTS DETECTED!")
        enriched = results['enriched_analysis']
        print(f"   Posts analyzed: {enriched.get('total_posts_analyzed', 0)}")
        print(f"   ICP confidence: {enriched.get('icp', {}).get('confidence', 0)}%")
        print("\n✅ INTEGRATION TEST PASSED!")
    else:
        print("\n⚠️  Using fallback data collection")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
