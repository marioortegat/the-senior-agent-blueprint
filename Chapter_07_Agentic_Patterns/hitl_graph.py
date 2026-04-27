"""
Real Human-in-the-Loop (HITL) Graph Module

This module demonstrates the dynamic interruption capability in LangGraph to
enforce strict Human-in-the-Loop security checks before executing destructive
backend or database operations on a REAL SQLite database with REAL keyboard input.
"""

import sqlite3
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

# ==========================================
# Real Local Database Setup (SQLite)
# ==========================================
print("📦 Initializing real SQLite database in memory...")
conn = sqlite3.connect(":memory:", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE transactions (id INTEGER PRIMARY KEY, amount REAL, entity TEXT)")
cursor.execute("INSERT INTO transactions (amount, entity) VALUES (150.0, 'Corp A'), (2500.0, 'Evil Corp')")
conn.commit()
print("   [Table 'transactions' populated with 2 active rows]\n")

# ==========================================
# Static memory schema definition
# ==========================================
class AgentState(TypedDict):
    sql_query: str
    db_results: str
    status: str

# The Checkpointer will persist the state between Thread 1 (before input) and Thread 2 (after input)
memory = InMemorySaver()
builder = StateGraph(AgentState)

# ==========================================
# 1. Dangerous Node Definition (HITL)
# ==========================================
def execute_sql_node(state: AgentState):
    proposed_query = state["sql_query"]
    
    # 💥 The framework intercepts Python execution and freezes it exactly on this line. 
    human_decision = interrupt(
        f"OPERATIONAL ALERT: The AI agent wants to execute the following destructive query: '{proposed_query}'"
    )
    
    # Days, minutes, or seconds later, the human responds and the variable acquires the value:
    if human_decision.strip().lower() != "approve":
        return {"status": f"Execution blocked by human decision. Chosen action: '{human_decision}'"}
    
    # If it was approved, finally execute the instruction in the real database
    try:
        cursor.execute(proposed_query)
        conn.commit()
        
        # We validate what happened to the table after executing the query
        try:
            cursor.execute("SELECT * FROM transactions")
            rows = cursor.fetchall()
            res = f"Clean execution. Remaining rows in the table: {len(rows)}"
        except sqlite3.OperationalError:
            res = "Alert: The 'transactions' table has been successfully dropped."
            
    except Exception as e:
        res = f"Database Error: {e}"
        
    return {"db_results": res, "status": "Destructively executed after receiving approval"}

builder.add_node("execute_sql", execute_sql_node)
builder.add_edge(START, "execute_sql")
builder.add_edge("execute_sql", END)

graph = builder.compile(checkpointer=memory)

# ==========================================
# 2. Main Execution (Interactive Loop)
# ==========================================
if __name__ == "__main__":
    print("🚀 Starting REAL Interactive Human-In-The-Loop Simulation...\n")
    
    config = {"configurable": {"thread_id": "audit-real-sqlite-001"}}
    initial_state = {"sql_query": "DROP TABLE transactions;", "db_results": "", "status": "pending"}

    print(">>> (Thread 1) The Agent sends a destructive request and will hit the Pause...")
    graph.invoke(initial_state, config=config)
    
    # We check in what state the graph was saved on disk/memory
    state_snap = graph.get_state(config)
    
    if state_snap.next:
        # We extract the message sent by the `interrupt()` function from inside the graph's guts
        interrupt_payload = state_snap.tasks[0].interrupts[0].value
        
        print("\n=======================================================")
        print("🛑 SYSTEM FROZEN / WAITING FOR EXTERNAL AUDIT 🛑")
        print("=======================================================")
        print(f"\nMessage emitted by the sleeping process:\n-> {interrupt_payload}\n")
        
        print("YOUR TURN (The keyboard is yours):")
        print("Type 'Approve' (to destroy the real table) or anything else to reject it.")
        
        # =========================================
        # THIS IS REAL: THE PROGRAM STOPS HERE
        # =========================================
        user_response = input("Your console command: ")
        
        print(f"\n>>> (Thread 2) Injecting your command ['{user_response}'] directly into the memory guts and resuming execution...")
        
        # The graph wakes up, receives the command, and completes the remaining logical branch
        final_result = graph.invoke(Command(resume=user_response), config=config)

        print("\n✅ Final State Log:")
        print(f"   Status : {final_result.get('status')}")
        if final_result.get('db_results'):
            print(f"   DB Log : {final_result['db_results']}")
