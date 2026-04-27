"""
Reflection Agent Module

This module demonstrates the structural logic for a Reflection (System 1 / System 2) loop
within a StateGraph using LangGraph. It features a continuous state passed between a Generator
and a Critic node, utilizing Reducers to append history and iterations limits to prevent infinite loops.
"""

from typing import Annotated, Sequence, TypedDict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
import operator

# ==========================================
# Mock Objects for Demonstration Purposes
# ==========================================
class MockLLM:
    def __init__(self, name: str):
        self.name = name
        
    def invoke(self, messages: list) -> BaseMessage:
        return AIMessage(content=f"[{self.name}] Output generated or evaluated based on context.")

llm_generator = MockLLM("Generator")
llm_critic = MockLLM("Critic")

# ==========================================
# 1. Formal Definition of Shared State Memory
# ==========================================
class ReflectionState(TypedDict):
    # Using operator.add ensures that concurrent or sequential messages
    # are concatenated rather than overwritten, preserving the context window.
    messages: Annotated[list, operator.add]
    iterations: int # Fundamental counter to prevent infinite algorithmic loops

# ==========================================
# 2. Generator Node (The Actor / System 1)
# ==========================================
def generate_node(state: ReflectionState):
    # The generative LLM processes the initial request or integrates correction if feedback exists.
    # The 'llm_generator' model is instantiated with a prompt focused on creating the solution.
    response = llm_generator.invoke(state["messages"])
    current_iters = state.get("iterations", 0)
    # Returns a partial dictionary. The framework will merge it using reducers.
    return {"messages": [response], "iterations": current_iters + 1}

# ==========================================
# 3. Critic Node (The Reflector / System 2)
# ==========================================
def reflect_node(state: ReflectionState):
    # The evaluator LLM strictly analyzes the last message emitted by the Generator
    # contrasting it with a predefined rubric of quality and accuracy.
    critique = llm_critic.invoke(state["messages"])
    # Only returns the critique; the iteration counter does not mutate here.
    return {"messages": [critique]}

# ==========================================
# 4. Functional Logic of the Iterative Loop
# ==========================================
def route_reflection(state: ReflectionState):
    # Acts as a Circuit Breaker: imposes a strict maximum limit of attempts
    if state.get("iterations", 0) >= 3:
        return END # Abandons the process to avoid exorbitant costs
    
    # Simplified semantic analysis of the last evaluation to determine convergence
    last_message = state["messages"][-1].content
    if "SUCCESSFULLY_APPROVED" in last_message:
        return END
    
    # If the rubric was not satisfied, obligatorily redirects the flow back to the generator node
    return "generate"

# ==========================================
# 5. Graph Construction and Compilation
# ==========================================
builder = StateGraph(ReflectionState)
builder.add_node("generate", generate_node)
builder.add_node("reflect", reflect_node)

builder.set_entry_point("generate")

# The generator unconditionally passes its work to the critic
builder.add_edge("generate", "reflect")

# The critic drives the conditional route to either generate again or End
builder.add_conditional_edges("reflect", route_reflection)

# Compiling the mathematical structure into an invocable software application
graph = builder.compile()

if __name__ == "__main__":
    print("🚀 Starting Reflection Agent Simulation...\n")
    initial_state = {
        "messages": [HumanMessage(content="Execute the initial analysis task.")],
        "iterations": 0
    }
    
    print("Executing graph...")
    try:
        # Invoking the entire graph
        final_state = graph.invoke(initial_state)
        
        print("\n--- Final Message History ---")
        for idx, msg in enumerate(final_state["messages"]):
            print(f"{idx+1}. {msg.content}")
        print(f"\nTotal iterations reached: {final_state['iterations']}")
        
    except Exception as e:
        print(f"Error during execution: {e}")
