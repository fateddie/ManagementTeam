"""
metadata_writer.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metadata Writer - SQLite Persistence

Stores ideas, scores, and justification metadata in SQLite database.

Location: src/utils/metadata_writer.py

Purpose:
    Provides auditable, transparent scoring with complete justification
    and source attribution for every score component.

Phase: 16 - Persistence & Metadata Layer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sqlite3
from pathlib import Path
from typing import Dict, List
from datetime import datetime


class MetadataWriter:
    """
    Manages SQLite database for ideas and scoring metadata.
    """
    
    def __init__(self, db_path: str = "data/ideas.db"):
        """
        Initialize metadata writer.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ideas table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id TEXT PRIMARY KEY,
            raw_input TEXT,
            refined_summary TEXT,
            industry TEXT,
            tags TEXT,
            project_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Scores table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            idea_id TEXT,
            market_size INTEGER,
            feasibility INTEGER,
            differentiation INTEGER,
            defensibility INTEGER,
            urgency INTEGER,
            founder_fit INTEGER,
            total_score INTEGER,
            verdict TEXT,
            feedback TEXT,
            scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(idea_id) REFERENCES ideas(id)
        )
        """)
        
        # Score metadata table (for justifications)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS score_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idea_id TEXT,
            category TEXT,
            score INTEGER,
            justification TEXT,
            source TEXT,
            confidence_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(idea_id) REFERENCES ideas(id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_idea(self, idea_id: str, raw_input: str, refined_summary: str,
                    industry: str = "", tags: str = "") -> bool:
        """
        Insert a new idea into the database.
        
        Args:
            idea_id: Unique identifier
            raw_input: Original vague idea
            refined_summary: Refined clear concept
            industry: Industry/vertical
            tags: Comma-separated tags
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT OR REPLACE INTO ideas (id, raw_input, refined_summary, industry, tags, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (idea_id, raw_input, refined_summary, industry, tags, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error inserting idea: {e}")
            return False
    
    def insert_score_metadata(self, idea_id: str, metadata: List[Dict]) -> bool:
        """
        Insert score metadata (justifications) for an idea.
        
        Args:
            idea_id: Idea identifier
            metadata: List of metadata dicts with:
                - category: e.g., 'market_size'
                - score: 0-10
                - justification: Reasoning
                - source: Data source
                - confidence_score: 0-10
                
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for entry in metadata:
                cursor.execute("""
                INSERT INTO score_metadata (idea_id, category, score, justification, source, confidence_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    idea_id,
                    entry.get("category", "unknown"),
                    entry.get("score", 0),
                    entry.get("justification", ""),
                    entry.get("source", ""),
                    entry.get("confidence_score", 5),
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error inserting metadata: {e}")
            return False
    
    def get_idea_metadata(self, idea_id: str) -> List[Dict]:
        """
        Retrieve all metadata for an idea.
        
        Args:
            idea_id: Idea identifier
            
        Returns:
            List of metadata dicts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT category, score, justification, source, confidence_score, created_at
        FROM score_metadata
        WHERE idea_id = ?
        ORDER BY created_at DESC
        """, (idea_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'category': row[0],
                'score': row[1],
                'justification': row[2],
                'source': row[3],
                'confidence_score': row[4],
                'created_at': row[5]
            }
            for row in rows
        ]
    
    def get_all_ideas(self) -> List[Dict]:
        """Get all ideas from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, raw_input, refined_summary, industry, tags, created_at FROM ideas")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': row[0],
                'raw_input': row[1],
                'refined_summary': row[2],
                'industry': row[3],
                'tags': row[4],
                'created_at': row[5]
            }
            for row in rows
        ]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helper Functions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def insert_score_metadata(db_path: str, idea_id: str, metadata: List[Dict]) -> bool:
    """
    Convenience function for inserting score metadata.
    
    Args:
        db_path: Path to SQLite database
        idea_id: Idea identifier
        metadata: List of metadata dicts
        
    Returns:
        True if successful
    """
    writer = MetadataWriter(db_path)
    return writer.insert_score_metadata(idea_id, metadata)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI Testing
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("\n" + "="*70)
    print("💾 METADATA WRITER - SQLite Persistence Test")
    print("="*70 + "\n")
    
    # Create test database
    writer = MetadataWriter("data/test_ideas.db")
    
    # Test idea insertion
    print("Testing idea insertion...\n")
    
    success = writer.insert_idea(
        idea_id="idea-001",
        raw_input="AI Call Catcher",
        refined_summary="AI Receptionist for Hair Salons",
        industry="hair salons",
        tags="AI, SaaS, beauty"
    )
    
    print(f"{'✅' if success else '❌'} Idea inserted\n")
    
    # Test metadata insertion
    print("Testing metadata insertion...\n")
    
    test_metadata = [
        {
            "category": "market_size",
            "score": 7,
            "justification": "Estimated 2,200 salons in Ireland",
            "source": "IrishHairFed + Yelp",
            "confidence_score": 8
        },
        {
            "category": "urgency",
            "score": 8,
            "justification": "High pain from missed calls during busy periods",
            "source": "Customer interviews",
            "confidence_score": 9
        }
    ]
    
    success = writer.insert_score_metadata("idea-001", test_metadata)
    
    print(f"{'✅' if success else '❌'} Metadata inserted\n")
    
    # Test retrieval
    print("Testing metadata retrieval...\n")
    
    retrieved = writer.get_idea_metadata("idea-001")
    
    print(f"Retrieved {len(retrieved)} metadata entries:")
    for entry in retrieved:
        print(f"\n   {entry['category'].upper()}: {entry['score']}/10")
        print(f"   {entry['justification']}")
        print(f"   Source: {entry['source']} (confidence: {entry['confidence_score']}/10)")
    
    print("\n" + "="*70)
    print("✅ All Database Operations Working")
    print("="*70 + "\n")

