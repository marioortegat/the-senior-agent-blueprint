# Chapter 08: Monitoring, Tracing, and Evaluations (The Lab)

This directory contains the implementations for "Chapter 08: The Laboratory" of *The Senior Agent Blueprint*. It focuses on transitioning from theoretical abstractions to a production-ready empirical scaffold.

The code here leverages **100% open-source tools and local models**, completely eliminating the need for paid commercial APIs like OpenAI or Anthropic.

## 🛠️ Tech Stack Used

- **Tracing & Observability:** [Langfuse](https://langfuse.com/) (Open Source / Local Docker)
- **State Orchestration:** [LangGraph](https://langchain-ai.github.io/langgraph/)
- **Local Models:** [Ollama](https://ollama.com/) (Llama 3.2)
- **Local Evaluations:** [RAGAS](https://docs.ragas.io/en/latest/) (using local LLM & HF Embeddings)
- **Security & PII:** [Microsoft Presidio](https://microsoft.github.io/presidio/) (Local open-source alternative to Lakera/LLM Guard)
- **Clustering:** `sentence-transformers` & `hdbscan`

## 📂 Lab Files Description

1. **`01_golden_dataset.py`**
   - **Goal:** Constructs the foundation of any rigorous AI Lab: The Golden Dataset.
   - **Details:** Creates a versioned dataset of immutable input/output pairs (including *happy paths*, *edge cases*, and *adversarial* attempts) mapped to their ideal ground truth. Saves the output as CSV and JSONL.

2. **`02_tracing_langgraph.py`**
   - **Goal:** Instruments the LangGraph Orchestrator network with Langfuse telemetry.
   - **Details:** Compiles an inference subgraph and dynamically attaches a `CallbackHandler`. It showcases how to generate hierarchical `trace_ids` and how to capture and attach multimodal assets (like base64 images) to the trace payload.

3. **`03_batch_evals.py`**
   - **Goal:** "Scoring as a Batch" using Local RAGAS.
   - **Details:** Simulates fetching traces from Langfuse, samples them, and evaluates them asynchronously. It uses a local LLM Judge (`llama3.2`) to test *Faithfulness* and *Answer Relevancy*, ultimately injecting these calculated scores back into the Langfuse visual trace using `langfuse.score()`.

4. **`04_synthetic_attacks.py`**
   - **Goal:** Multi-Turn Synthetic Simulations (OpenEvals concept).
   - **Details:** Deploys a simulated "Adversarial Persona" (an aggressive, angry user) that interacts with our production agent over multiple turns. Finally, a Judge LLM assesses if the agent maintained politeness and adhered to safety boundaries.

5. **`05_pii_security.py`**
   - **Goal:** Prompt Injection Inspection and PII Data Security.
   - **Details:** Uses local detector networks (`presidio-analyzer` / `presidio-anonymizer`) to scan prompts for sensitive information (e.g., credit card numbers, names), obfuscating them before passing the payload to the local LLM.

6. **`06_intent_clustering.py`**
   - **Goal:** Unsupervised Intent Classification by Clustering.
   - **Details:** Projects raw logs into embedding maps (`all-mpnet-base-v2`) and groups dense behavior clusters using `HDBSCAN`. A distilled LLM then automatically assigns snake_case descriptive labels to these groups, segmenting thousands of interactions with zero manual data-science intervention.

## 🚀 How to Run and Test

### 1. Prerequisites
- Have **Python 3.12** installed.
- Install [Ollama](https://ollama.com/) and pull the required model:
  ```bash
  ollama run llama3.2
  ```
- *(Optional but recommended)* Launch local **Langfuse** using Docker:
  ```bash
  docker run -d -p 3000:3000 -e DATABASE_URL="postgresql://postgres:postgres@db:5432/postgres" -e NEXTAUTH_SECRET="secret" -e SALT="secret" langfuse/langfuse
  ```

### 2. Environment Setup
Create a virtual environment and install the dependencies:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Execution Order
You can run the files independently to test each isolated concept:
```bash
# 1. Create your Golden Dataset
python 01_golden_dataset.py

# 2. Run the LangGraph agent and see the local Langfuse Trace generated
python 02_tracing_langgraph.py

# 3. Execute the RAGAS local evaluation over dummy traces
python 03_batch_evals.py

# 4. Simulate a furious user fighting your chatbot
python 04_synthetic_attacks.py

# 5. Test PII obfuscation (Credit Card & Names)
python 05_pii_security.py

# 6. Run the HDBSCAN density clustering
python 06_intent_clustering.py
```

## 🔧 Environment & Troubleshooting Notes
During the initial lab setup, several critical dependency alignments and OS-specific fixes were applied to ensure 100% local execution stability:

1. **Langfuse & Langchain Version Alignment:** Langfuse Server v2 (the lightweight docker variant without ClickHouse) requires Langfuse Python SDK `<3.0.0`. To ensure compatibility, `langchain` and its ecosystem (`langchain-core`, `langchain-community`, `langgraph`) were pinned to `0.2.x`, along with `langchain-ollama==0.1.1` and `ragas==0.1.19` (which avoids the `ContextOverflowError` found in newer versions).
2. **Windows PowerShell Emoji Fix:** Added `sys.stdout.reconfigure(encoding='utf-8')` to scripts 02, 03, 04, 05, and 06 to prevent `UnicodeEncodeError: 'charmap'` crashes on Windows terminals when rendering UI emojis.
3. **Microsoft Presidio Luhn Validation:** In script `05_pii_security.py`, a mathematically valid Visa test card (`4111 1111 1111 1111`) is used. Presidio applies the Luhn algorithm to detect credit cards and avoids false positives, meaning it will intentionally ignore random string patterns like `1111 2222`.
