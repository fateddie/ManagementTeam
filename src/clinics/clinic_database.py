#!/usr/bin/env python3
"""
Clinic Database Module
======================
Extends Supabase memory system with clinic-specific storage and retrieval.
Stores clinic reviews, pain points, and enables semantic search.

Features:
- Inherits Supabase client and embedding generation
- Adds clinic-specific tables (clinics, clinic_reviews, pain_points)
- Semantic search for similar clinics and reviews
- Cross-validation queries

Author: Management Team
Last Updated: 2026-01-04
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import base Supabase functions
from memory.supabase_memory import (
    _get_supabase_client,
    _get_openai_client,
    generate_embedding,
    DEPENDENCIES_AVAILABLE
)


def store_clinic(
    clinic_name: str,
    clinic_type: str,
    location: str,
    google_place_id: Optional[str] = None,
    total_reviews: int = 0,
    average_rating: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Store clinic information in Supabase

    Args:
        clinic_name: Name of the clinic
        clinic_type: Type (physiotherapy, counselling, chiropody)
        location: Location/address
        google_place_id: Google Maps place ID (unique identifier)
        total_reviews: Number of reviews collected
        average_rating: Average star rating
        metadata: Additional structured data

    Returns:
        clinic_id: ID in clinics table

    Example:
        >>> clinic_id = store_clinic(
        ...     "London Physiotherapy Clinic",
        ...     "physiotherapy",
        ...     "London, UK",
        ...     total_reviews=25,
        ...     average_rating=4.2
        ... )
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("supabase package not installed. Run: pip install supabase")

    supabase = _get_supabase_client()

    # Check if clinic already exists (by google_place_id or name+location)
    existing = None
    if google_place_id:
        result = supabase.table("clinics")\
            .select("id")\
            .eq("google_place_id", google_place_id)\
            .execute()
        existing = result.data[0] if result.data else None

    if not existing:
        # Search by name + location
        result = supabase.table("clinics")\
            .select("id")\
            .eq("name", clinic_name)\
            .eq("location", location)\
            .execute()
        existing = result.data[0] if result.data else None

    # Prepare metadata
    meta = metadata or {}
    meta.update({
        "clinic_type": clinic_type,
        "location": location,
        "last_updated": datetime.now().isoformat()
    })

    if existing:
        # Update existing clinic
        clinic_id = existing["id"]
        supabase.table("clinics").update({
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "metadata": meta
        }).eq("id", clinic_id).execute()

        print(f"✅ Updated clinic: {clinic_name} (ID: {clinic_id})")
    else:
        # Insert new clinic
        clinic_result = supabase.table("clinics").insert({
            "name": clinic_name,
            "clinic_type": clinic_type,
            "location": location,
            "google_place_id": google_place_id,
            "total_reviews": total_reviews,
            "average_rating": average_rating,
            "metadata": meta
        }).execute()

        if not clinic_result.data:
            raise Exception("Failed to store clinic in Supabase")

        clinic_id = clinic_result.data[0]["id"]
        print(f"✅ Stored clinic: {clinic_name} (ID: {clinic_id})")

    return clinic_id


def store_clinic_review(
    clinic_id: int,
    review_text: str,
    rating: int,
    review_date: Optional[str] = None,
    source: str = "google",
    reviewer_name: Optional[str] = None,
    pain_points: Optional[List[str]] = None,
    confidence: str = "medium",
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Store clinic review with semantic embedding

    Args:
        clinic_id: ID of the clinic (from clinics table)
        review_text: Full text of the review
        rating: Star rating (1-5)
        review_date: Date of review (ISO format)
        source: Source (google, facebook, etc.)
        reviewer_name: Name of reviewer (optional)
        pain_points: List of pain point keywords extracted
        confidence: Confidence level (high/medium/low)
        metadata: Additional structured data

    Returns:
        review_id: ID in clinic_reviews table

    Example:
        >>> review_id = store_clinic_review(
        ...     clinic_id=123,
        ...     review_text="Long waiting times, but great service",
        ...     rating=3,
        ...     pain_points=["waiting"]
        ... )
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("supabase package not installed. Run: pip install supabase")

    supabase = _get_supabase_client()

    # Generate embedding for semantic search
    embedding = generate_embedding(review_text)

    # Prepare metadata
    meta = metadata or {}
    meta.update({
        "source": source,
        "rating": rating,
        "reviewer": reviewer_name,
        "collected_at": datetime.now().isoformat()
    })

    # Store review
    review_result = supabase.table("clinic_reviews").insert({
        "clinic_id": clinic_id,
        "review_text": review_text,
        "rating": rating,
        "review_date": review_date,
        "source": source,
        "embedding": embedding,
        "pain_points": pain_points or [],
        "confidence": confidence,
        "metadata": meta
    }).execute()

    if not review_result.data:
        raise Exception("Failed to store review in Supabase")

    review_id = review_result.data[0]["id"]
    print(f"✅ Stored review for clinic {clinic_id} (Review ID: {review_id})")

    return review_id


def store_pain_point(
    clinic_id: int,
    pain_point: str,
    keyword: str,
    sources: List[str],
    frequency: int,
    confidence: str,
    sentiment: Optional[float] = None,
    examples: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> int:
    """
    Store identified pain point for a clinic

    Args:
        clinic_id: ID of the clinic
        pain_point: Human-readable pain point description
        keyword: Pain point keyword (for grouping)
        sources: List of sources (google_reviews, reddit, publications)
        frequency: Number of mentions
        confidence: Confidence level (high/medium/low)
        sentiment: Average sentiment score (-1 to 1)
        examples: Example quotes
        metadata: Additional structured data

    Returns:
        pain_point_id: ID in pain_points table

    Example:
        >>> pain_point_id = store_pain_point(
        ...     clinic_id=123,
        ...     pain_point="Long waiting times for appointments",
        ...     keyword="waiting",
        ...     sources=["google_reviews", "reddit"],
        ...     frequency=12,
        ...     confidence="high"
        ... )
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("supabase package not installed. Run: pip install supabase")

    supabase = _get_supabase_client()

    # Prepare metadata
    meta = metadata or {}
    meta.update({
        "keyword": keyword,
        "examples": examples or [],
        "analyzed_at": datetime.now().isoformat()
    })

    # Store pain point
    pain_result = supabase.table("pain_points").insert({
        "clinic_id": clinic_id,
        "pain_point": pain_point,
        "keyword": keyword,
        "sources": sources,
        "frequency": frequency,
        "confidence": confidence,
        "sentiment": sentiment,
        "metadata": meta
    }).execute()

    if not pain_result.data:
        raise Exception("Failed to store pain point in Supabase")

    pain_point_id = pain_result.data[0]["id"]
    print(f"✅ Stored pain point '{keyword}' for clinic {clinic_id}")

    return pain_point_id


def search_similar_reviews(
    query: str,
    clinic_type: Optional[str] = None,
    limit: int = 10,
    min_similarity: float = 0.7
) -> List[Dict]:
    """
    Search for reviews similar to query using semantic search

    Args:
        query: Natural language query (e.g., "waiting times complaints")
        clinic_type: Filter by clinic type (optional)
        limit: Maximum number of results
        min_similarity: Minimum cosine similarity (0.0 to 1.0)

    Returns:
        List of matching reviews with similarity scores

    Example:
        >>> results = search_similar_reviews(
        ...     "booking appointment difficulties",
        ...     clinic_type="physiotherapy"
        ... )
        >>> for r in results:
        ...     print(f"{r['similarity']:.2f} - {r['review_text'][:100]}")
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("supabase package not installed. Run: pip install supabase")

    supabase = _get_supabase_client()
    query_embedding = generate_embedding(query)

    # Note: This requires a custom RPC function in Supabase
    # For Stage 0/1, we can do client-side filtering
    # For Stage 2+, implement search_clinic_reviews RPC function

    # Simplified approach: Get all reviews and filter client-side
    query_builder = supabase.table("clinic_reviews").select("*, clinics(name, clinic_type, location)")

    if clinic_type:
        # Join with clinics table to filter by type
        query_builder = query_builder.eq("clinics.clinic_type", clinic_type)

    result = query_builder.limit(100).execute()  # Get top 100 for filtering

    if not result.data:
        return []

    # Client-side similarity calculation (for POC)
    # TODO: Move to Supabase RPC function in Stage 2
    import numpy as np

    def cosine_similarity(a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    matches = []
    for review in result.data:
        if review.get("embedding"):
            similarity = cosine_similarity(query_embedding, review["embedding"])
            if similarity >= min_similarity:
                matches.append({
                    **review,
                    "similarity": float(similarity)
                })

    # Sort by similarity and limit
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    return matches[:limit]


def get_clinic_pain_points(
    clinic_id: int,
    min_confidence: str = "low"
) -> List[Dict]:
    """
    Get all pain points for a specific clinic

    Args:
        clinic_id: ID of the clinic
        min_confidence: Minimum confidence level (high/medium/low)

    Returns:
        List of pain points ordered by importance
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("supabase package not installed. Run: pip install supabase")

    supabase = _get_supabase_client()

    # Map confidence to numeric values for filtering
    confidence_map = {"high": 3, "medium": 2, "low": 1}
    min_conf_value = confidence_map.get(min_confidence, 1)

    result = supabase.table("pain_points")\
        .select("*")\
        .eq("clinic_id", clinic_id)\
        .execute()

    if not result.data:
        return []

    # Filter by confidence and sort by frequency
    filtered = [
        p for p in result.data
        if confidence_map.get(p.get("confidence", "low"), 1) >= min_conf_value
    ]

    filtered.sort(key=lambda x: x.get("frequency", 0), reverse=True)
    return filtered


def get_clinic_type_aggregated_pain_points(
    clinic_type: str,
    min_frequency: int = 3,
    limit: int = 20
) -> List[Dict]:
    """
    Get aggregated pain points across all clinics of a type

    Args:
        clinic_type: Type of clinic (physiotherapy, counselling, chiropody)
        min_frequency: Minimum total frequency across clinics
        limit: Maximum number of results

    Returns:
        List of aggregated pain points with clinic counts
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("supabase package not installed. Run: pip install supabase")

    supabase = _get_supabase_client()

    # Get all pain points for clinics of this type
    result = supabase.table("pain_points")\
        .select("*, clinics(clinic_type)")\
        .eq("clinics.clinic_type", clinic_type)\
        .execute()

    if not result.data:
        return []

    # Aggregate by keyword
    aggregated = {}
    for pain in result.data:
        keyword = pain.get("keyword")
        if keyword not in aggregated:
            aggregated[keyword] = {
                "keyword": keyword,
                "pain_point": pain.get("pain_point"),
                "total_frequency": 0,
                "clinic_count": 0,
                "clinic_ids": set(),
                "avg_sentiment": [],
                "sources": set()
            }

        agg = aggregated[keyword]
        agg["total_frequency"] += pain.get("frequency", 0)
        agg["clinic_ids"].add(pain.get("clinic_id"))
        agg["clinic_count"] = len(agg["clinic_ids"])
        agg["sources"].update(pain.get("sources", []))

        if pain.get("sentiment") is not None:
            agg["avg_sentiment"].append(pain["sentiment"])

    # Convert to list and filter
    aggregated_list = []
    for keyword, data in aggregated.items():
        if data["total_frequency"] >= min_frequency:
            aggregated_list.append({
                "keyword": keyword,
                "pain_point": data["pain_point"],
                "total_frequency": data["total_frequency"],
                "clinic_count": data["clinic_count"],
                "sources": list(data["sources"]),
                "avg_sentiment": sum(data["avg_sentiment"]) / len(data["avg_sentiment"]) if data["avg_sentiment"] else None,
                "importance_score": data["total_frequency"] * data["clinic_count"]
            })

    # Sort by importance and limit
    aggregated_list.sort(key=lambda x: x["importance_score"], reverse=True)
    return aggregated_list[:limit]


def get_clinic_stats(clinic_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics about stored clinic data

    Args:
        clinic_type: Filter by clinic type (optional)

    Returns:
        Dictionary with counts and statistics
    """
    if not DEPENDENCIES_AVAILABLE:
        raise ImportError("supabase package not installed. Run: pip install supabase")

    supabase = _get_supabase_client()

    # Count clinics
    clinic_query = supabase.table("clinics").select("id", count="exact")
    if clinic_type:
        clinic_query = clinic_query.eq("clinic_type", clinic_type)
    clinic_result = clinic_query.execute()

    # Count reviews
    review_query = supabase.table("clinic_reviews").select("id", count="exact")
    review_result = review_query.execute()

    # Count pain points
    pain_query = supabase.table("pain_points").select("id", count="exact")
    pain_result = pain_query.execute()

    return {
        "total_clinics": clinic_result.count if hasattr(clinic_result, 'count') else 0,
        "total_reviews": review_result.count if hasattr(review_result, 'count') else 0,
        "total_pain_points": pain_result.count if hasattr(pain_result, 'count') else 0,
        "clinic_type_filter": clinic_type
    }


def bulk_store_clinic_evidence(
    clinic_name: str,
    clinic_type: str,
    location: str,
    evidence_data: Dict
) -> Dict[str, int]:
    """
    Bulk store clinic + reviews + pain points from ClinicsEvidenceCollector output

    Args:
        clinic_name: Name of the clinic
        clinic_type: Type of clinic
        location: Location
        evidence_data: Output from ClinicsEvidenceCollector.collect_clinic_evidence()

    Returns:
        Dict with IDs (clinic_id, review_ids, pain_point_ids)

    Example:
        >>> from src.clinics.clinics_evidence_collector import ClinicsEvidenceCollector
        >>> collector = ClinicsEvidenceCollector()
        >>> evidence = collector.collect_clinic_evidence("London Physio", "physiotherapy")
        >>> ids = bulk_store_clinic_evidence("London Physio", "physiotherapy", "London", evidence)
    """
    print(f"\n💾 Bulk storing evidence for: {clinic_name}")

    # 1. Store clinic
    google_reviews_data = evidence_data.get("sources", {}).get("google_reviews", {})
    business_info = google_reviews_data.get("business_info", {})

    clinic_id = store_clinic(
        clinic_name=clinic_name,
        clinic_type=clinic_type,
        location=location,
        total_reviews=google_reviews_data.get("total_reviews", 0),
        average_rating=business_info.get("average_rating"),
        metadata={
            "evidence_collected_at": evidence_data.get("collected_at"),
            "evidence_score": evidence_data.get("evidence_score")
        }
    )

    # 2. Store reviews
    review_ids = []
    for review in google_reviews_data.get("top_reviews", []):
        try:
            review_id = store_clinic_review(
                clinic_id=clinic_id,
                review_text=review.get("text", ""),
                rating=review.get("rating", 0),
                review_date=review.get("date"),
                reviewer_name=review.get("reviewer"),
                metadata={"review_source_id": review.get("id")}
            )
            review_ids.append(review_id)
        except Exception as e:
            print(f"⚠️  Failed to store review: {e}")

    # 3. Store pain points (from pain point analysis)
    pain_point_ids = []
    if "unified_insights" in evidence_data:
        insights = evidence_data["unified_insights"]
        if "clinic_specific" in insights:
            clinic_specific = insights["clinic_specific"]

            # Store cross-validated pain points
            cross_validated = clinic_specific.get("cross_validated_pain_points", {})
            for keyword in cross_validated.get("keywords", []):
                try:
                    # Find pain point details
                    pain_detail = next(
                        (p for p in google_reviews_data.get("pain_points", [])
                         if p.get("keyword") == keyword),
                        None
                    )

                    if pain_detail:
                        pain_point_id = store_pain_point(
                            clinic_id=clinic_id,
                            pain_point=keyword.replace("_", " ").title(),
                            keyword=keyword,
                            sources=["google_reviews", "social"],  # Cross-validated
                            frequency=pain_detail.get("frequency", 0),
                            confidence=cross_validated.get("confidence", "medium"),
                            sentiment=pain_detail.get("avg_sentiment"),
                            examples=[e.get("text", "")[:200] for e in pain_detail.get("examples", [])[:3]]
                        )
                        pain_point_ids.append(pain_point_id)
                except Exception as e:
                    print(f"⚠️  Failed to store pain point {keyword}: {e}")

    print(f"✅ Bulk store complete: {len(review_ids)} reviews, {len(pain_point_ids)} pain points")

    return {
        "clinic_id": clinic_id,
        "review_ids": review_ids,
        "pain_point_ids": pain_point_ids
    }


# ============================================
# CLI Commands (for testing)
# ============================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Clinic Database CLI")
    parser.add_argument("command", choices=["store_clinic", "search", "stats", "test"])
    parser.add_argument("--name", help="Clinic name")
    parser.add_argument("--type", choices=["physiotherapy", "counselling", "chiropody"], help="Clinic type")
    parser.add_argument("--location", help="Location")
    parser.add_argument("--query", help="Search query")

    args = parser.parse_args()

    if args.command == "store_clinic":
        if not args.name or not args.type or not args.location:
            print("❌ --name, --type, and --location required")
            sys.exit(1)

        clinic_id = store_clinic(
            args.name,
            args.type,
            args.location
        )
        print(f"Clinic ID: {clinic_id}")

    elif args.command == "search":
        if not args.query:
            print("❌ --query required")
            sys.exit(1)

        results = search_similar_reviews(
            args.query,
            clinic_type=args.type
        )
        print(f"\n🔍 Found {len(results)} results:\n")
        for r in results:
            print(f"  {r['similarity']:.2f} - {r['review_text'][:100]}...")
            print(f"           Rating: {r['rating']}/5, Clinic: {r.get('clinics', {}).get('name', 'N/A')}\n")

    elif args.command == "stats":
        stats = get_clinic_stats(clinic_type=args.type)
        print("\n📈 Clinic Database Statistics:")
        print(f"   Total clinics: {stats['total_clinics']}")
        print(f"   Total reviews: {stats['total_reviews']}")
        print(f"   Total pain points: {stats['total_pain_points']}")
        if stats['clinic_type_filter']:
            print(f"   Filtered by: {stats['clinic_type_filter']}")
        print()

    elif args.command == "test":
        print("🧪 Testing clinic database...")
        try:
            # Test Supabase connection
            client = _get_supabase_client()
            print("✅ Supabase connected")

            # Test embedding generation
            print("🧪 Testing embedding generation...")
            embedding = generate_embedding("Test review text")
            print(f"✅ Generated {len(embedding)}-dimensional embedding")

            # Test clinic storage (mock)
            print("🧪 Testing clinic storage...")
            clinic_id = store_clinic(
                "Test Clinic",
                "physiotherapy",
                "Test Location",
                metadata={"test": True}
            )
            print(f"✅ Created test clinic (ID: {clinic_id})")

            print("\n✅ All tests passed!")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)
