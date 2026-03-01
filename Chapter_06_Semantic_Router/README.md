# Chapter 06: Semantic Router & Semantic Firewall

This chapter introduces the concept of a **Semantic Router** as a robust alternative to fragile keyword-based routing. By generating text embeddings and calculating Cosine Similarity, we can classify user intentions directly without calling an expensive LLM.

Crucially, this architecture demonstrates Defense in Depth: the router doubles as a **Semantic Firewall**, capable of blocking jailbreak attempts and security risks at the network edge—shutting down malicious queries before they ever reach the primary LLM application.

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed. Then, create a virtual environment and install the required packages.

```bash
# Create and activate a virtual environment
python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Example
Execute the standalone test module to see the router in action, classifying test phrases and effectively blocking predefined security threats.

```bash
python main.py
```

### 3. Under the Hood
The `SemanticRouter` uses the lightweight `all-MiniLM-L6-v2` model from `sentence-transformers` to precompute intent representations, ensuring classification happens in milliseconds.
