# models.py - The Data Model
# The Senior Agent Blueprint - Chapter 04
"""
Defines the strict output structure using Pydantic.
This ensures type safety and validation for LLM outputs.
"""

from pydantic import BaseModel, Field
from typing import Literal


class LeadOutput(BaseModel):
    """
    Structured output schema for lead assessment.
    
    The Senior Move: Using Pydantic models with DSPy's Typed Predictor
    ensures that LLM outputs conform to a strict schema, eliminating
    parsing errors and enabling reliable downstream processing.
    """
    
    category: Literal["Sales", "Support", "Partnership", "Spam"] = Field(
        ...,
        description="The primary intent category of the incoming email"
    )
    
    priority_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Priority level from 1 (low) to 10 (immediate attention required)"
    )
    
    suggested_action: str = Field(
        ...,
        description="Recommended next step for the agent (e.g., 'Book Meeting', 'Reply with FAQ', 'Escalate to Manager')"
    )
    
    reasoning: str = Field(
        ...,
        description="Brief justification explaining the category and priority score assignment"
    )
