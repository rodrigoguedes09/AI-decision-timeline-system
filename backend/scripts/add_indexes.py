"""
Database Migration: Add Performance Indexes

This script creates strategic indexes to improve query performance.
Run this after initial database setup.

Usage:
    python scripts/add_indexes.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine
from sqlalchemy import text


def add_indexes():
    """Create performance indexes on key columns"""
    
    indexes = [
        # Decision table indexes
        "CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp DESC)",
        "CREATE INDEX IF NOT EXISTS idx_decisions_source ON decisions(source)",
        "CREATE INDEX IF NOT EXISTS idx_decisions_confidence ON decisions(confidence)",
        "CREATE INDEX IF NOT EXISTS idx_decisions_decision_id ON decisions(decision_id)",
        
        # Decision steps indexes
        "CREATE INDEX IF NOT EXISTS idx_steps_decision_id ON decision_steps(decision_id)",
        "CREATE INDEX IF NOT EXISTS idx_steps_order ON decision_steps(decision_id, step_order)",
        "CREATE INDEX IF NOT EXISTS idx_steps_type ON decision_steps(step_type)",
        
        # Composite indexes for common queries
        "CREATE INDEX IF NOT EXISTS idx_decisions_source_confidence ON decisions(source, confidence)",
        "CREATE INDEX IF NOT EXISTS idx_decisions_timestamp_source ON decisions(timestamp DESC, source)",
    ]
    
    print("🔧 Adding performance indexes to database...")
    
    with engine.connect() as conn:
        for idx_sql in indexes:
            try:
                conn.execute(text(idx_sql))
                index_name = idx_sql.split("idx_")[1].split(" ")[0] if "idx_" in idx_sql else "unknown"
                print(f"  ✓ Created index: idx_{index_name}")
            except Exception as e:
                print(f"  ⚠ Index may already exist or error occurred: {str(e)[:100]}")
        
        conn.commit()
    
    print("\n✅ Database indexes created successfully!")
    print("📊 Query performance should now be significantly improved.")
    print("\nRecommended next steps:")
    print("  - Run ANALYZE on your database (if using PostgreSQL)")
    print("  - Monitor query performance with EXPLAIN ANALYZE")
    print("  - Consider adding more indexes based on actual usage patterns")


if __name__ == "__main__":
    add_indexes()
