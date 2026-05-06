import sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import hdbscan
from sentence_transformers import SentenceTransformer
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

def cluster_and_label_intents():
    """
    Intent Classification by Clustering.
    Projects raw logs into vector maps (embeddings), delimits dense clouds
    with HDBSCAN, and automatically labels them with a distilled local LLM.
    """
    print("🌌 Starting Vector Clustering and Autonomous Labeling...")

    # 1. Massive raw logs (Simulated)
    raw_logs = [
        "How do I integrate the payment API?",
        "I need the authentication endpoint",
        "Error 500 when calling the user API",
        "I want to cancel my subscription",
        "Do I get my money back if I cancel?",
        "Refund process please",
        "I forgot my password",
        "How do I reset my password",
        "My account is locked",
        # Noise (Outliers)
        "What time is it in Tokyo?",
        "Tell me a chicken recipe"
    ]

    # 2. Dense Embeddings Generation
    print("🧩 Generating vector embeddings (all-mpnet-base-v2)...")
    # We use an open source model specialized in sentences
    embedder = SentenceTransformer('all-mpnet-base-v2')
    embeddings = embedder.encode(raw_logs)

    # 3. Density Clustering with HDBSCAN
    print("🗺️ Clustering densities with HDBSCAN...")
    # min_cluster_size=2 for demonstration, in production usually > 10
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, min_samples=1)
    cluster_labels = clusterer.fit_predict(embeddings)

    # Organize by cluster
    clusters = {}
    for text, label in zip(raw_logs, cluster_labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(text)

    # 4. Descriptive Labeling with LLM
    print("🏷️ Labeling clusters using Distilled LLM (Llama3.2)...")
    llm = ChatOllama(model="llama3.2", temperature=0)
    
    label_prompt = SystemMessage(content=(
        "You are a data analyst. Analyze the following list of user queries "
        "that belong to the same semantic group and return ONE "
        "descriptive label in snake_case format that defines the general intent. "
        "Example: api_technical_query, refund_request, account_management."
        "Respond ONLY with the label, no quotes or explanations."
    ))

    cluster_mappings = {}
    
    for label, texts in clusters.items():
        if label == -1:
            print(f"\n[Cluster -1: Noise / Outliers]")
            for t in texts:
                print(f"  - {t}")
            continue
            
        print(f"\n[Cluster {label}] Analyzing sample...")
        sample_texts = "\n".join([f"- {t}" for t in texts[:5]])
        
        response = llm.invoke([
            label_prompt,
            HumanMessage(content=f"Queries:\n{sample_texts}")
        ])
        
        topic_name = response.content.strip().lower()
        cluster_mappings[label] = topic_name
        
        print(f"👉 Assigned label: {topic_name}")
        for t in texts:
            print(f"  - {t}")

    print("\n✅ Segmented traces ready to be ingested to Langfuse or FinOps observability.")

if __name__ == "__main__":
    cluster_and_label_intents()
