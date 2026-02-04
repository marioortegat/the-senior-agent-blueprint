# metrics.py - Business Logic Metric
# The Senior Agent Blueprint - Chapter 04
"""
Defines the custom metric function for DSPy optimization.
This is where you encode your business rules and quality standards.
"""


def business_logic_metric(example, pred, trace=None) -> float:
    """
    Advanced validation metric that combines correctness with business logic.
    
    This metric goes beyond simple accuracy to ensure outputs are
    not just correct, but also logically consistent and useful.
    
    Args:
        example: The ground truth example with expected output
        pred: The model's prediction
        trace: Optional trace for debugging (used by DSPy internally)
    
    Returns:
        float: Score from 0.0 (fail) to 1.0 (pass)
    
    Business Rules Encoded:
        1. High priority (>7) requires detailed reasoning (>=20 chars)
        2. Spam cannot have priority > 3 (logically inconsistent)
        3. Category must match the gold label for correctness
    """
    
    # Safety check: Ensure prediction has the expected structure
    if not hasattr(pred, 'analysis') or pred.analysis is None:
        return 0.0
    
    analysis = pred.analysis
    
    # =========================================================================
    # Rule 1: High Priority Requires Strong Reasoning
    # =========================================================================
    # A high priority score demands accountability. The agent must explain
    # WHY this lead deserves immediate attention to prevent false escalations.
    if analysis.priority_score > 7:
        if len(analysis.reasoning) < 20:
            # Fail: High priority needs detailed justification
            return 0.0
    
    # =========================================================================
    # Rule 2: Spam Cannot Be Urgent
    # =========================================================================
    # This is a logical consistency check. If something is spam, it should
    # never be marked as high priority. This catches hallucinated urgency.
    if analysis.category == "Spam" and analysis.priority_score > 3:
        # Fail: Spam cannot be urgent - this is logically inconsistent
        return 0.0
    
    # =========================================================================
    # Rule 3: Correctness Check (vs Gold Label)
    # =========================================================================
    # Finally, we check if the predicted category matches the expected one.
    # This is the core accuracy metric wrapped in our business logic.
    if hasattr(example, 'analysis') and example.analysis is not None:
        return 1.0 if analysis.category == example.analysis.category else 0.0
    
    # If no gold label available, pass based on logic rules alone
    return 1.0
