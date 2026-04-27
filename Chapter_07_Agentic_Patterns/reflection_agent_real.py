"""
Real Reflection Agent Module (Local / Ollama)

This module demonstrates the Reflection loop using an ACTUAL LLM running LOCALLY via Ollama.
No API keys are required.

Requirements: 
1. Install Ollama on your machine (https://ollama.com)
2. Ensure you have downloaded a lightweight model, e.g., run: `ollama pull llama3.2` or `ollama pull qwen2.5:0.5b`
3. The pip package `langchain-ollama` must be installed.
"""

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
import operator

# ==========================================
# LLM Initialization (Ollama Local)
# ==========================================
try:
    from langchain_ollama import ChatOllama
    # Initialize a lightweight local model.
    # llama3.2 is highly recommended for semantic and coding tasks locally.
    llm = ChatOllama(model="llama3.2", temperature=0.0) 
except ImportError:
    print("Please install the package via: pip install langchain-ollama")
    exit(1)

# ==========================================
# 1. State Memory
# ==========================================
class ReflectionState(TypedDict):
    messages: Annotated[list, operator.add]
    iterations: int

# ==========================================
# 2. Generator Node
# ==========================================
def generate_node(state: ReflectionState):
    print("-> Executing: Generator (System 1)")
    
    # Instruct the model on its task:
    generator_instructions = SystemMessage(
        content="You are an expert Python programmer. Generate a Python function to calculate the factorial of a number. Respond ONLY with the code, without markdown blocks."
    )
    
    # We prepare the context messages
    messages_to_send = [generator_instructions] + state["messages"]
    
    response = llm.invoke(messages_to_send)
    current_iters = state.get("iterations", 0)
    
    return {"messages": [response], "iterations": current_iters + 1}

# ==========================================
# 3. Critic Node
# ==========================================
def reflect_node(state: ReflectionState):
    print("-> Executing: Critic (System 2)")
    
    evaluator_instructions = SystemMessage(
        content=(
            "You are a strict code inspector.\n"
            "Check if the LAST generated message is valid Python code to calculate a factorial.\n"
            "If it is perfect code and has NO conversational text, respond EXACTLY with 'SUCCESSFULLY_APPROVED'.\n"
            "If there are errors, bugs, or conversational text, explain concisely what the developer must correct."
        )
    )
    
    messages_to_send = [evaluator_instructions] + state["messages"]
    critique = llm.invoke(messages_to_send)
    
    return {"messages": [critique]}

# ==========================================
# 4. Iterative Loop Logic
# ==========================================
def route_reflection(state: ReflectionState):
    current_iters = state.get("iterations", 0)
    
    if current_iters >= 3:
        print("🛑 CIRCUIT BREAKER: Maximum iterations limit reached.")
        return END 
    
    last_message = state["messages"][-1].content
    
    # We validate if the Critic AI gave us the green light
    if "SUCCESSFULLY_APPROVED" in last_message:
        print("✅ APPROVED: Mathematical convergence reached.")
        return END
    
    print("🔁 REJECTED: Returning to the generator to correct flaws...")
    return "generate"

# ==========================================
# 5. Graph Compilation
# ==========================================
builder = StateGraph(ReflectionState)
builder.add_node("generate", generate_node)
builder.add_node("reflect", reflect_node)

builder.set_entry_point("generate")
builder.add_edge("generate", "reflect")
builder.add_conditional_edges("reflect", route_reflection)

graph = builder.compile()

if __name__ == "__main__":
    print("🚀 Starting Reflection Agent with LOCAL LLM (Ollama)...\n")
    initial_state = {
        "messages": [HumanMessage(content="Write the factorial_calc(n) function.")],
        "iterations": 0
    }
    
    try:
        final_state = graph.invoke(initial_state)
        print("\n--- Final History ---")
        for i, msg in enumerate(final_state["messages"]):
            role = "USER" if isinstance(msg, HumanMessage) else "AI"
            print(f"[{role}]: {msg.content}\n")
            
    except Exception as e:
        print(f"Error: {e}. Make sure Ollama is running in the background.")
