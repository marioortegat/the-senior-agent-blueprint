# main.py - The Pipeline
# The Senior Agent Blueprint - Chapter 04
"""
Main entry point that combines all components:
- Configures the LLM
- Creates training data
- Compiles the agent with BootstrapFewShot
- Runs inference and inspects the optimized prompt
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import dspy
from dspy.teleprompt import BootstrapFewShot

from models import LeadOutput
from signatures import LeadAssessment
from metrics import business_logic_metric


def create_training_data() -> list[dspy.Example]:
    """
    Creates sample training data for the optimizer.
    
    In production, this would come from your labeled dataset.
    Each example needs both input (email_content) and expected output (analysis).
    """
    
    examples = [
        dspy.Example(
            email_content="""
            Hi there,
            
            I'm the CTO at TechStartup Inc. We're looking to implement an AI solution
            for our customer service team (about 50 agents). We have budget allocated
            and want to move fast - ideally deploy within the next 2 weeks.
            
            Can we schedule a demo this week?
            
            Best,
            Sarah Chen
            CTO, TechStartup Inc.
            """,
            analysis=LeadOutput(
                category="Sales",
                priority_score=9,
                suggested_action="Book Meeting",
                reasoning="Enterprise-level prospect with budget, clear timeline, and decision-maker engagement. High revenue potential."
            )
        ).with_inputs("email_content"),
        
        dspy.Example(
            email_content="""
            Hello,
            
            I've been trying to reset my password for the last hour but the 
            reset link keeps expiring. This is really frustrating as I have 
            a deadline today and can't access my account.
            
            Please help ASAP!
            
            - John
            """,
            analysis=LeadOutput(
                category="Support",
                priority_score=7,
                suggested_action="Reply with FAQ",
                reasoning="User experiencing account access issues with time pressure. Needs immediate technical assistance."
            )
        ).with_inputs("email_content"),
        
        dspy.Example(
            email_content="""
            Dear Partner,
            
            I represent CloudInfra Solutions, a leading cloud provider. We're 
            interested in exploring a strategic partnership where we could 
            integrate your AI capabilities into our platform for our enterprise clients.
            
            Would love to discuss this further with your BD team.
            
            Regards,
            Michael Torres
            VP Business Development
            CloudInfra Solutions
            """,
            analysis=LeadOutput(
                category="Partnership",
                priority_score=8,
                suggested_action="Escalate to Manager",
                reasoning="Strategic partnership opportunity with established company. Requires executive visibility and BD involvement."
            )
        ).with_inputs("email_content"),
        
        dspy.Example(
            email_content="""
            CONGRATULATIONS!!! You have been selected to receive $1,000,000 USD!
            
            Click here to claim your prize now!!! Don't miss this LIMITED TIME OFFER!!!
            
            Act NOW before it's too late!!!
            
            Best regards,
            International Lottery Commission
            """,
            analysis=LeadOutput(
                category="Spam",
                priority_score=1,
                suggested_action="Archive and Ignore",
                reasoning="Classic spam/phishing pattern with unrealistic offers and urgency tactics."
            )
        ).with_inputs("email_content"),
        
        dspy.Example(
            email_content="""
            Hi,
            
            We're a growing e-commerce company processing about 10,000 orders/month.
            Saw your product demo and I'm interested in learning more about pricing
            for teams. We're currently evaluating 3 vendors.
            
            Thanks,
            Alex
            Operations Manager
            """,
            analysis=LeadOutput(
                category="Sales",
                priority_score=6,
                suggested_action="Send Pricing Info",
                reasoning="Mid-market prospect in active evaluation. Good potential but competing with other vendors."
            )
        ).with_inputs("email_content"),
    ]
    
    return examples


def build_agent():
    """
    Builds and compiles the lead assessment agent.
    
    Uses BootstrapFewShot to automatically optimize the prompt
    based on the training examples and business logic metric.
    """
    
    # Create the base predictor using ChainOfThought for better reasoning
    base_agent = dspy.ChainOfThought(LeadAssessment)
    
    # Get training data
    trainset = create_training_data()
    
    # Configure the optimizer
    # BootstrapFewShot will automatically select the best examples
    # and optimize the prompt based on our metric
    optimizer = BootstrapFewShot(
        metric=business_logic_metric,
        max_bootstrapped_demos=3,  # Number of examples to include in prompt
        max_labeled_demos=3,       # Max labeled examples to consider
        max_rounds=1,              # Optimization rounds (increase for better results)
    )
    
    # Compile the agent
    print("🔧 Compiling agent with BootstrapFewShot...")
    compiled_agent = optimizer.compile(base_agent, trainset=trainset)
    print("✅ Agent compiled successfully!")
    
    return compiled_agent


def run_inference(agent, email_content: str) -> LeadOutput:
    """
    Runs the compiled agent on a new email.
    
    Args:
        agent: The compiled DSPy agent
        email_content: Raw email text to analyze
    
    Returns:
        LeadOutput: Structured analysis result
    """
    
    result = agent(email_content=email_content)
    return result.analysis


def main():
    """
    Main entry point - demonstrates the full pipeline.
    """
    
    # =========================================================================
    # Step 1: Configure the LLM
    # =========================================================================
    # Note: Set your API key in environment variable before running
    # export OPENAI_API_KEY="your-key-here"
    
    lm = dspy.LM(
        model="openai/gpt-4o-mini",
        temperature=0.0,  # Deterministic for reproducibility
        max_tokens=1000,
    )
    dspy.configure(lm=lm)
    
    print("=" * 60)
    print("🚀 The Senior Agent Blueprint - Chapter 04: DSPy")
    print("=" * 60)
    
    # =========================================================================
    # Step 2: Build and Compile the Agent
    # =========================================================================
    agent = build_agent()
    
    # =========================================================================
    # Step 3: Test with a New Email
    # =========================================================================
    test_email = """
    Hello,
    
    I'm the Head of AI at Fortune500Corp. We're launching a major initiative 
    to automate our customer interactions across all channels. This is a 
    board-level priority with a $2M budget allocated for this fiscal year.
    
    I'd like to schedule a call with your enterprise team to discuss:
    1. Your platform capabilities
    2. Integration options with our existing stack
    3. Enterprise pricing and SLAs
    
    We're looking to make a decision within the next 30 days.
    
    Best regards,
    Jennifer Walsh
    Head of AI & Automation
    Fortune500Corp
    """
    
    print("\n📧 Analyzing test email...")
    print("-" * 60)
    
    result = run_inference(agent, test_email)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Category:         {result.category}")
    print(f"   Priority Score:   {result.priority_score}/10")
    print(f"   Suggested Action: {result.suggested_action}")
    print(f"   Reasoning:        {result.reasoning}")
    
    # =========================================================================
    # Step 4: Inspect the Optimized Prompt (For the Book!)
    # =========================================================================
    print("\n" + "=" * 60)
    print("📝 OPTIMIZED PROMPT (inspect_history output)")
    print("=" * 60)
    
    # This shows the full DSPy history (for debugging)
    dspy.inspect_history(n=1)
    
    # Save debug log to optimized_prompt.txt
    try:
        history = dspy.settings.lm.history
        if history:
            last_call = history[-1]
            with open("optimized_prompt.txt", "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("OPTIMIZED PROMPT - Generated by DSPy BootstrapFewShot\n")
                f.write("=" * 80 + "\n\n")
                
                if isinstance(last_call, dict):
                    messages = last_call.get("messages", [])
                    for msg in messages:
                        role = msg.get("role", "unknown").upper()
                        content = msg.get("content", "")
                        f.write(f"[{role}]\n{content}\n\n")
                        f.write("-" * 40 + "\n\n")
                    
                    response = last_call.get("response", {})
                    if response:
                        f.write("=" * 80 + "\n")
                        f.write("MODEL RESPONSE\n")
                        f.write("=" * 80 + "\n")
                        if hasattr(response, "choices"):
                            for choice in response.choices:
                                f.write(choice.message.content + "\n")
                        else:
                            f.write(str(response) + "\n")
                else:
                    f.write(str(last_call))
                    
            print("\n💾 Debug log saved to: optimized_prompt.txt")
    except Exception as e:
        print(f"\n⚠️ Could not save debug log: {e}")
    
    # =========================================================================
    # Step 5: Generate PORTABLE PROMPT (Ready to copy to n8n, Playground, etc.)
    # =========================================================================
    try:
        history = dspy.settings.lm.history
        if history:
            last_call = history[-1]
            messages = last_call.get("messages", []) if isinstance(last_call, dict) else []
            
            # Extract the system message (first message)
            system_content = ""
            few_shot_examples = []
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "system":
                    system_content = content
                elif role == "user":
                    few_shot_examples.append({"role": "user", "content": content})
                elif role == "assistant":
                    few_shot_examples.append({"role": "assistant", "content": content})
            
            # Build the portable prompt
            with open("portable_prompt.txt", "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("PORTABLE SYSTEM PROMPT\n")
                f.write("Ready to copy to: n8n, OpenAI Playground, LangChain, any LLM API\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("SYSTEM MESSAGE (copy this to your LLM's system prompt)\n")
                f.write("=" * 80 + "\n\n")
                f.write(system_content)
                f.write("\n\n")
                
                if few_shot_examples:
                    f.write("=" * 80 + "\n")
                    f.write("FEW-SHOT EXAMPLES (include these in your prompt or as messages)\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for i, ex in enumerate(few_shot_examples[:-1]):  # Exclude the last user message (test input)
                        f.write(f"[{ex['role'].upper()}]\n")
                        f.write(ex['content'])
                        f.write("\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("HOW TO USE\n")
                f.write("=" * 80 + "\n")
                f.write("""
1. Copy the SYSTEM MESSAGE above into your LLM's system prompt field
2. The few-shot examples are already embedded in the system message
3. Send user emails as the USER message
4. Parse the JSON response: {"category", "priority_score", "suggested_action", "reasoning"}

Example API call structure:
- messages[0] = {"role": "system", "content": <SYSTEM MESSAGE above>}
- messages[1] = {"role": "user", "content": <your email to analyze>}
""")
            
            print("💾 Portable prompt saved to: portable_prompt.txt")
    except Exception as e:
        print(f"\n⚠️ Could not save portable prompt: {e}")
    
    return result


if __name__ == "__main__":
    main()
