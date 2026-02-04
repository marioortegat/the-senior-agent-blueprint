# Chapter 04 - DSPy: The Senior Move

> **Stop Prompt Engineering. Start Programming.**

This chapter demonstrates the "Senior Move" pattern using DSPy - a framework that treats prompts as code, not strings.

## 🎯 What You'll Learn

1. **Typed Predictors** - Using Pydantic models to enforce strict output schemas
2. **Signatures** - Defining contracts between your code and the LLM
3. **Business Logic Metrics** - Encoding domain rules into optimization
4. **BootstrapFewShot** - Automatic prompt engineering through compilation
5. **Portable Prompts** - Export optimized prompts for use in n8n, Playground, etc.

## 📁 File Structure

```
Chapter_04_DSPy/
├── __init__.py           # Package initialization
├── models.py             # Pydantic data models (LeadOutput)
├── signatures.py         # DSPy Signature definitions
├── metrics.py            # Business logic validation metric
├── main.py               # Pipeline orchestration & execution
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your API keys (gitignored)
├── optimized_prompt.txt  # Full DSPy debug logs (generated)
├── portable_prompt.txt   # Clean prompt for n8n/Playground (generated)
└── README.md             # This file
```

## 🚀 Quick Start

### 1. Create Virtual Environment

```bash
cd Chapter_04_DSPy
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Your API Key

```bash
# Copy the example and add your key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 4. Run the Pipeline

```bash
python main.py
```

## 📤 Output Files

After running, you'll get:

| File | Purpose |
|------|---------|
| `optimized_prompt.txt` | Full DSPy history/logs for debugging |
| `portable_prompt.txt` | **Clean prompt ready to copy to n8n, Playground, or any LLM** |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                              │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │ Training    │ → │ BootstrapFS  │ → │ Compiled Agent  │  │
│  │ Examples    │   │ Optimizer    │   │ (Optimized)     │  │
│  └─────────────┘   └──────────────┘   └─────────────────┘  │
│         ↓                 ↓                    ↓            │
│  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐  │
│  │ LeadOutput  │   │ business_    │   │ LeadAssessment  │  │
│  │ (Pydantic)  │   │ logic_metric │   │ (Signature)     │  │
│  └─────────────┘   └──────────────┘   └─────────────────┘  │
│    models.py        metrics.py         signatures.py       │
└─────────────────────────────────────────────────────────────┘
                              ↓
                    portable_prompt.txt
                    (Ready for n8n, Playground, etc.)
```

## 💡 The Senior Pattern

### Why Typed Predictors?

```python
# ❌ The Junior Way - String parsing, hope it works
response = llm.complete("Analyze this email...")
category = parse_somehow(response)  # 🤞

# ✅ The Senior Way - Type-safe, validated, guaranteed
class LeadOutput(BaseModel):
    category: Literal["Sales", "Support", "Partnership", "Spam"]
    priority_score: int = Field(ge=1, le=10)
    
analysis: LeadOutput = dspy.OutputField()  # 🎯 Always valid
```

### Why Custom Metrics?

Standard accuracy isn't enough. We encode **business rules**:

1. **High priority (>7) requires detailed reasoning** - Prevents lazy escalations
2. **Spam cannot be urgent** - Catches logical inconsistencies
3. **Category correctness** - Core accuracy metric

## 🔧 Customization

- Add more training examples in `main.py:create_training_data()`
- Extend business rules in `metrics.py:business_logic_metric()`
- Modify the output schema in `models.py:LeadOutput`

---

*Part of "The Senior Agent Blueprint" book series.*
