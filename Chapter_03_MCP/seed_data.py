"""
Seed script to populate the leads database with sample data.

Run this script to create test leads for demonstration purposes.
This is useful for testing the MCP server before production use.

Usage:
    python seed_data.py
    or
    uv run seed_data.py
"""

import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "leads.db"

# Sample leads for demonstration
SAMPLE_LEADS = [
    ("Mario Garcia", "mario@example.com", 5000.00, "qualified"),
    ("Sarah Johnson", "sarah.j@techcorp.com", 12500.00, "contacted"),
    ("James Wilson", "jwilson@enterprise.io", 8750.00, "new"),
    ("Emily Chen", "emily.chen@startup.co", 3200.00, "converted"),
    ("Michael Brown", "m.brown@agency.com", 15000.00, "qualified"),
    ("Lisa Martinez", "lisa.m@consulting.net", 7800.00, "contacted"),
    ("David Lee", "david.lee@investments.com", 25000.00, "new"),
    ("Amanda Taylor", "a.taylor@marketing.io", 4500.00, "converted"),
]


def seed_database() -> None:
    """
    Populate the database with sample lead data.
    
    Creates the leads table if it doesn't exist and inserts
    sample data for testing purposes.
    """
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            value REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert sample data (skip duplicates)
    inserted = 0
    for name, email, value, status in SAMPLE_LEADS:
        try:
            cursor.execute(
                "INSERT INTO leads (name, email, value, status) VALUES (?, ?, ?, ?)",
                (name, email, value, status)
            )
            inserted += 1
        except sqlite3.IntegrityError:
            print(f"Skipped (already exists): {email}")
    
    conn.commit()
    conn.close()
    
    print(f"Database seeded successfully!")
    print(f"  - Inserted: {inserted} new leads")
    print(f"  - Database location: {DATABASE_PATH}")


def view_all_leads() -> None:
    """Display all leads currently in the database."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM leads ORDER BY value DESC")
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        print(f"\nTotal leads: {len(rows)}")
        print("-" * 70)
        for row in rows:
            print(f"  [{row['id']}] {row['name']:<20} | {row['email']:<30} | ${row['value']:>10,.2f} | {row['status']}")
    else:
        print("No leads in database.")


if __name__ == "__main__":
    seed_database()
    view_all_leads()
