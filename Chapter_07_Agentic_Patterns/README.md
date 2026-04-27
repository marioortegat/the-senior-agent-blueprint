# Chapter 07: Agentic Patterns - The Laboratory: State Graph Engineering

This chapter and its respective code bridge orchestration theory and practice using industry-leading tools like LangGraph. Here we abandon the linear pipeline architecture and adopt **Semantically Driven Finite State Machines**, managing crucial issues such as Race Conditions, immutable persistence, algorithmically controlled loops, and strict human safety in the execution loop.

## 🚀 Getting Started

### 1. Prerequisites
Make sure you have Python 3.10+ and a virtual environment (recommended). Included in the requirements are `langchain`, `langgraph`, and `langchain-ollama` for testing with local models.

```bash
# Create and activate environment
python -m venv .venv
.venv\Scripts\activate

# Install core dependencies
pip install -r requirements.txt
```

### 2. Included Patterns
The laboratory implements and demonstrates in functional code the concepts covered in the architectural theory:

1. **The Iterative Reflection Loop (`reflection_agent.py` & `reflection_agent_real.py`)** 
   - "System 1/System 2" or Actor/Critic architecture.
   - Demonstrates the use of `Reducers` to concatenate securely in asynchronous transactional operations using decorators like `Annotated` with `operator.add`.
   - Incorporates the *conditional_edges* syntax acting as thermodynamic Network Circuit Breakers.
   - The `_real` version utilizes `langchain-ollama` to run an actual lightweight local model like Llama 3.2 to run real inference!

2. **Absolute Safety with the HITL Primitive (`hitl_graph.py`)**
   - Implements LangGraph's dynamic intra-node interruption via the `interrupt()` primitive.
   - Showcases persistent memory schemas using `InMemorySaver` Checkpointers.
   - Provisions an **actual in-memory SQLite database**, demonstrating the suspension of the execution thread and requesting literal console `input()` from the human user before permitting a dangerous database mutation (e.g. `DROP TABLE`).
   - Asynchronous resurrection after long supervisory pauses without losing memory by leveraging the `Command` object.

### 3. Execution

To test the full self-correction LLM loop guided by the Critic node (requires Ollama running locally):
```bash
python reflection_agent_real.py
```

To experience the interactive thread "deep hibernation" with real interactive SQLite mutation:
```bash
python hitl_graph.py
```
