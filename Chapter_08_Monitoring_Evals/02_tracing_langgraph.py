import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import base64
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langfuse.callback import CallbackHandler
from langfuse import Langfuse
import json

# ---------------------------------------------------------
# Langfuse Configuration (Local/Open Source Mode)
# ---------------------------------------------------------
# To run locally: `docker run -d -p 3000:3000 -e DATABASE_URL=... langfuse/langfuse`
os.environ["LANGFUSE_PUBLIC_KEY"] = os.getenv("LANGFUSE_PUBLIC_KEY", "pk-lf-eeed94dc-7147-452b-95b9-9e73d0d1b345")
os.environ["LANGFUSE_SECRET_KEY"] = os.getenv("LANGFUSE_SECRET_KEY", "sk-lf-bf374fad-6a9d-4f00-ac77-8482a24defca")
os.environ["LANGFUSE_HOST"] = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

# Initialize Langfuse client and callback
langfuse = Langfuse()
langfuse_handler = CallbackHandler()

# ---------------------------------------------------------
# Local Model (Ollama)
# ---------------------------------------------------------
llm = ChatOllama(model="llama3.2", temperature=0)

# ---------------------------------------------------------
# LangGraph State
# ---------------------------------------------------------
class AgentState(TypedDict):
    messages: list
    contexts: list
    trace_id: str
    metadata: dict

# ---------------------------------------------------------
# Graph Nodes
# ---------------------------------------------------------
def retrieval_node(state: AgentState):
    """Simulates a vector search."""
    print("🔍 [Node] Retrieving context...")
    query = state["messages"][-1].content
    
    # Mock RAG database
    db = {
        "hours": "The branch is open from 9 AM to 6 PM.",
        "refunds": "Refunds are processed within 15 business days."
    }
    
    contexts = []
    if "hour" in query.lower() or "time" in query.lower():
        contexts.append(db["hours"])
    if "refund" in query.lower():
        contexts.append(db["refunds"])
        
    return {"contexts": contexts}

def generation_node(state: AgentState):
    """Generates the response based on context, injecting the Langfuse callback."""
    print("🧠 [Node] Generating response...")
    
    system_prompt = "You are a corporate assistant. Use the following context to answer:\n"
    system_prompt += "\n".join(state.get("contexts", []))
    if not state.get("contexts"):
        system_prompt += "If you don't know the answer, say so clearly."
        
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    
    # This is where the tracking "magic" happens. The langfuse callback is injected.
    # We use .invoke with the configuration.
    response = llm.invoke(
        messages, 
        config={"callbacks": [langfuse_handler]}
    )
    
    return {"messages": [response]}

# ---------------------------------------------------------
# Helper Function: Multimodal Capture to Base64
# ---------------------------------------------------------
def capture_multimodal_asset(file_path: str, langfuse_trace_id: str):
    """
    Simulates the ingestion of an image/audio into the Langfuse trace.
    """
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
        
    # We attach the file as metadata to the manual trace
    print(f"📸 Multimodal asset encoded (Base64, size: {len(encoded)} bytes)")
    langfuse.trace(
        id=langfuse_trace_id,
        metadata={"image_payload": f"data:image/jpeg;base64,{encoded[:50]}..."} # Truncated for visualization
    )
    return encoded

# ---------------------------------------------------------
# Graph Assembly
# ---------------------------------------------------------
workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieval_node)
workflow.add_node("generate", generation_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Starting Orchestrator with Langfuse Tracing...")
    
    # User input
    user_input = "What are the operating hours?"
    
    # 1. Execute the pipeline
    final_state = app.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "metadata": {"source": "web_chat"}
        },
        config={"callbacks": [langfuse_handler]} # Global trace
    )
    
    print("\n🤖 Agent Response:")
    print(final_state["messages"][-1].content)
    
    # 2. Retrieve the generated trace ID
    # In newer Langfuse versions, we can get the last trace ID from the handler
    try:
        trace_id = getattr(langfuse_handler, "last_trace_id", "Not available")
        print(f"\n🆔 Trace ID Generated: {trace_id}")
    except Exception:
        pass
        
    # 3. Flush data to Langfuse to prevent IO blocks
    print("📡 Synchronizing traces with Langfuse server...")
    langfuse.flush()
    print("✅ Completed.")
