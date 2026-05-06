import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import random
import pandas as pd
from langfuse import Langfuse
from langchain_ollama import ChatOllama
from datasets import Dataset

# RAGAS metrics
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from langchain_core.embeddings import FakeEmbeddings

# ---------------------------------------------------------
# Mock Configuration for Langfuse and Ollama
# ---------------------------------------------------------
os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-eeed94dc-7147-452b-95b9-9e73d0d1b345"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-bf374fad-6a9d-4f00-ac77-8482a24defca"
os.environ["LANGFUSE_HOST"] = "http://localhost:3000"

langfuse = Langfuse()

# Local LLM as Judge
evaluator_llm = ChatOllama(model="llama3.2", temperature=0)
# Fake/Fast or local embeddings for RAGAS (RAGAS needs embeddings for some metrics)
from langchain_community.embeddings import HuggingFaceEmbeddings
evaluator_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def fetch_and_sample_traces():
    """
    Simulates retrieving production traces from Langfuse (Batch Scoring).
    """
    print("📥 Retrieving recent traces from Langfuse API...")
    
    # In a real environment you would use langfuse.get_traces() or similar.
    # Here we simulate a sampling extracted from the Golden Dataset or production
    mock_traces = [
        {
            "trace_id": f"trace_{random.randint(1000, 9999)}",
            "question": "What are the operating hours?",
            "contexts": ["The branch is open from 9 AM to 6 PM from Monday to Friday."],
            "answer": "The branch is open from 9 AM to 6 PM, Monday to Friday.",
            "ground_truth": "From Monday to Friday, 9 AM to 6 PM."
        },
        {
            "trace_id": f"trace_{random.randint(1000, 9999)}",
            "question": "Do you have a refund policy?",
            "contexts": ["Refunds are processed in 15 business days if the product is sealed."],
            "answer": "Yes, we do refunds the same day regardless of the product condition.", # Simulating hallucination
            "ground_truth": "Yes, in 15 business days if it is sealed."
        }
    ]
    
    return mock_traces

def run_batch_evaluations(traces):
    """
    Executes Accuracy, Relevance, and Completeness checks with RAGAS.
    """
    print("🧠 Configuring LLM Judge (Ollama) and RAGAS for Batch Scoring...")
    
    # RAGAS expects a specific format (HuggingFace Dataset)
    data = {
        "question": [t["question"] for t in traces],
        "contexts": [t["contexts"] for t in traces],
        "answer": [t["answer"] for t in traces],
        "ground_truth": [t["ground_truth"] for t in traces]
    }
    
    dataset = Dataset.from_dict(data)
    
    print("⚙️ Executing evaluation matrices...")
    
    # Note: RAGAS defaults to OpenAI. By passing langchain_llm and embeddings,
    # we force the use of local models (Open Source).
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,       # Factual correctness (no hallucinations)
            answer_relevancy,   # Completeness and relevance of the answer
        ],
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        raise_exceptions=False
    )
    
    df_results = result.to_pandas()
    return df_results, traces

def inject_scores_to_langfuse(df_results, original_traces):
    """
    Mathematically injects the Judge's results back into Langfuse.
    """
    print("\n📤 Injecting semantic results to Langfuse...")
    
    for idx, row in df_results.iterrows():
        trace_id = original_traces[idx]["trace_id"]
        
        # Faithfulness Score
        f_score = row.get("faithfulness", 0.0)
        
        # Relevancy Score
        r_score = row.get("answer_relevancy", 0.0)
        
        print(f"Trace {trace_id} -> Faithfulness: {f_score:.2f} | Relevancy: {r_score:.2f}")
        
        try:
            # Sync scores to the visual platform
            langfuse.score(
                trace_id=trace_id,
                name="ragas_faithfulness",
                value=f_score,
                comment="Evaluated by Local Judge Llama3.2 Batch Scoring"
            )
            langfuse.score(
                trace_id=trace_id,
                name="ragas_answer_relevancy",
                value=r_score,
                comment="Evaluated by Local Judge Llama3.2 Batch Scoring"
            )
        except Exception as e:
            # Expect failure if no local server is running on port 3000
            pass
            
    langfuse.flush()
    print("✅ Scoring As A Batch completed.")

if __name__ == "__main__":
    sampled_traces = fetch_and_sample_traces()
    eval_results, traces = run_batch_evaluations(sampled_traces)
    inject_scores_to_langfuse(eval_results, traces)
