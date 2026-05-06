import sys
sys.stdout.reconfigure(encoding='utf-8')
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import time

def process_secure_prompt():
    """
    PII Inspection and obfuscation using Presidio (Open Source)
    before sending the payload to the LLM engine (Ollama).
    """
    print("🛡️ Starting Data Security Shield (PII Scanner)...")
    
    # 1. Initialize Presidio engines
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    
    # 2. User input with sensitive data
    user_input = "Hello, my name is John Doe and my credit card is 4111 1111 1111 1111. I want to check my balance."
    print(f"\n👤 Original Input (Unsafe): {user_input}")
    
    # 3. Detect PII
    start_time = time.time()
    results = analyzer.analyze(
        text=user_input,
        entities=["PERSON", "CREDIT_CARD"],
        language='en'
    )
    
    # 4. Anonymize text
    anonymized_result = anonymizer.anonymize(
        text=user_input,
        analyzer_results=results
    )
    safe_input = anonymized_result.text
    latency = time.time() - start_time
    
    print(f"🔒 Anonymized Input (Safe): {safe_input}")
    print(f"⏱️ Scanner overhead: {latency:.4f} seconds")
    
    # 5. Send securely to the LLM (prevents leaks in telemetry or logs)
    print("\n🧠 Sending safe context to the Agent...")
    llm = ChatOllama(model="llama3.2", temperature=0)
    
    response = llm.invoke([
        HumanMessage(content=safe_input)
    ])
    
    print(f"🤖 Agent Response: {response.content}")
    
    # Note: If the agent needs to use the real name in the final response,
    # deanonymization dictionaries would be used to revert tokens like <PERSON>
    # at the output layer.

if __name__ == "__main__":
    process_secure_prompt()
