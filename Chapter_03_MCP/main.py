"""
MCP SQLite Server - A Model Context Protocol server for database operations.

This server demonstrates how to create an MCP server that allows AI agents
to interact with a SQLite database using natural language commands.

The server exposes tools for:
- Adding new leads to the database
- Retrieving lead information by email or name
- Listing all leads
"""

import sqlite3
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field


# =============================================================================
# Block A: Pydantic Models
# =============================================================================
# Pydantic provides strict type validation. When the model expects an "email",
# Pydantic ensures it's a valid string format. This prevents runtime errors
# and gives the LLM clear schemas to work with.

class Lead(BaseModel):
    """Represents a lead in the CRM database."""
    
    name: str = Field(..., description="Full name of the lead")
    email: str = Field(..., description="Email address of the lead")
    value: float = Field(..., description="Monetary value of the lead in USD")
    status: str = Field(default="new", description="Status: new, contacted, qualified, converted")


class LeadCreate(BaseModel):
    """Schema for creating a new lead."""
    
    name: str = Field(..., min_length=1, description="Full name of the lead")
    email: str = Field(..., description="Valid email address")
    value: float = Field(..., ge=0, description="Lead value must be non-negative")


class LeadQuery(BaseModel):
    """Schema for querying leads."""
    
    email: Optional[str] = Field(None, description="Email to search for")
    name: Optional[str] = Field(None, description="Name to search for (partial match)")


# =============================================================================
# Block B: Database Connection
# =============================================================================
# Simple SQLite connection with automatic table creation.
# The database file is created in the same directory as the script.

DATABASE_PATH = Path(__file__).parent / "leads.db"


def get_db_connection() -> sqlite3.Connection:
    """
    Create a connection to the SQLite database.
    
    Returns:
        sqlite3.Connection: Active database connection with Row factory enabled.
    """
    conn = sqlite3.connect(str(DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """
    Initialize the database schema.
    
    Creates the leads table if it doesn't exist. This function is called
    on server startup to ensure the database is ready for operations.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DATABASE_PATH}")


# =============================================================================
# Block C: MCP Server & Tool Definitions (The "Magic")
# =============================================================================
# The @mcp.tool() decorator exposes functions as tools that AI agents can call.
# CRITICAL: The docstring is what the LLM reads to understand how to use
# each tool. Be descriptive and include parameter explanations.

# Initialize the MCP server using FastMCP
mcp = FastMCP("sqlite-leads-server")


@mcp.tool()
def get_lead_by_email(email: str) -> str:
    """
    Retrieve a lead's information by their email address.
    
    Use this tool when you need to look up a specific lead using their
    email address. Returns all available information about the lead
    including their name, value, and status.
    
    Args:
        email: The exact email address of the lead to search for.
        
    Returns:
        A formatted string with the lead's details, or an error message
        if the lead is not found.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, email, value, status, created_at FROM leads WHERE email = ?",
        (email,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return (
            f"Lead Found:\n"
            f"  Name: {row['name']}\n"
            f"  Email: {row['email']}\n"
            f"  Value: ${row['value']:,.2f}\n"
            f"  Status: {row['status']}\n"
            f"  Created: {row['created_at']}"
        )
    else:
        return f"No lead found with email: {email}"


@mcp.tool()
def get_lead_by_name(name: str) -> str:
    """
    Search for leads by name (partial match).
    
    Use this tool when you need to find leads by their name. This performs
    a partial match search, so searching for "Mario" will find "Mario Garcia",
    "Mario Rodriguez", etc.
    
    Args:
        name: The name or partial name to search for (case-insensitive).
        
    Returns:
        A formatted list of matching leads with their details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, email, value, status FROM leads WHERE name LIKE ?",
        (f"%{name}%",)
    )
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        results = [f"Found {len(rows)} lead(s) matching '{name}':\n"]
        for row in rows:
            results.append(
                f"  - {row['name']} ({row['email']}): ${row['value']:,.2f} [{row['status']}]"
            )
        return "\n".join(results)
    else:
        return f"No leads found matching name: {name}"


@mcp.tool()
def add_new_lead(name: str, email: str, value: float) -> str:
    """
    Add a new lead to the CRM database.
    
    Use this tool to create a new lead record. The lead will be created
    with a 'new' status. The email must be unique - if a lead with the
    same email already exists, an error will be returned.
    
    Args:
        name: Full name of the lead (e.g., "John Smith").
        email: Email address of the lead (must be unique in the database).
        value: The monetary value of this lead in USD (e.g., 5000.00).
        
    Returns:
        A confirmation message with the created lead's details,
        or an error message if the operation fails.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO leads (name, email, value, status) VALUES (?, ?, ?, ?)",
            (name, email, value, "new")
        )
        
        conn.commit()
        lead_id = cursor.lastrowid
        conn.close()
        
        return (
            f"Lead created successfully!\n"
            f"  ID: {lead_id}\n"
            f"  Name: {name}\n"
            f"  Email: {email}\n"
            f"  Value: ${value:,.2f}\n"
            f"  Status: new"
        )
    except sqlite3.IntegrityError:
        return f"Error: A lead with email '{email}' already exists in the database."
    except Exception as e:
        return f"Error creating lead: {str(e)}"


@mcp.tool()
def list_all_leads() -> str:
    """
    List all leads in the CRM database.
    
    Use this tool to get an overview of all leads in the system.
    Returns a summary with total count and total value, followed by
    a list of all leads sorted by value (highest first).
    
    Returns:
        A formatted list of all leads with summary statistics.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT name, email, value, status FROM leads ORDER BY value DESC"
    )
    rows = cursor.fetchall()
    conn.close()
    
    if rows:
        total_value = sum(row['value'] for row in rows)
        results = [
            f"Total Leads: {len(rows)}",
            f"Total Pipeline Value: ${total_value:,.2f}",
            "-" * 40
        ]
        for row in rows:
            results.append(
                f"  {row['name']} | {row['email']} | ${row['value']:,.2f} | {row['status']}"
            )
        return "\n".join(results)
    else:
        return "No leads in the database yet."


@mcp.tool()
def update_lead_status(email: str, new_status: str) -> str:
    """
    Update the status of an existing lead.
    
    Use this tool to change a lead's status in the sales pipeline.
    Valid statuses are: new, contacted, qualified, converted, lost.
    
    Args:
        email: The email address of the lead to update.
        new_status: The new status (new/contacted/qualified/converted/lost).
        
    Returns:
        A confirmation message or an error if the lead is not found.
    """
    valid_statuses = {"new", "contacted", "qualified", "converted", "lost"}
    
    if new_status.lower() not in valid_statuses:
        return f"Invalid status. Valid options are: {', '.join(valid_statuses)}"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE leads SET status = ? WHERE email = ?",
        (new_status.lower(), email)
    )
    
    if cursor.rowcount > 0:
        conn.commit()
        conn.close()
        return f"Lead status updated to '{new_status}' for: {email}"
    else:
        conn.close()
        return f"No lead found with email: {email}"


# =============================================================================
# Block D: Server Entry Point
# =============================================================================
# Initialize the database on module load and run via FastMCP's built-in runner.

# Initialize database when module loads
init_database()

if __name__ == "__main__":
    # FastMCP handles the stdio server automatically
    mcp.run()
