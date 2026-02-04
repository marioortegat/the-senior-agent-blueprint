# signatures.py - The DSPy Signature
# The Senior Agent Blueprint - Chapter 04
"""
Defines the DSPy Signature using Typed Predictors.
This is the "contract" between your code and the LLM.
"""

import dspy
from models import LeadOutput


class LeadAssessment(dspy.Signature):
    """
    Analyzes an incoming email to determine routing and priority.
    
    Must extract key intent signals and map to business rules:
    - Sales inquiries should be prioritized for revenue potential
    - Support requests need empathetic and swift handling
    - Partnership opportunities require executive visibility
    - Spam must be filtered with minimal resource expenditure
    """
    
    # Input Field
    email_content: str = dspy.InputField(
        desc="Raw text from the email body, including any signatures or formatting"
    )
    
    # Output Field - The Senior Move: Typed Predictor
    # By using LeadOutput (a Pydantic model), DSPy will automatically
    # validate the LLM output against the schema and retry if invalid
    analysis: LeadOutput = dspy.OutputField(
        desc="Structured assessment following the LeadOutput schema with category, priority, action, and reasoning"
    )
