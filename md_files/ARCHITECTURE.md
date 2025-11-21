# 🏗️ AGERE Architecture: Custom Tools & Agents

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    AGERE PROJECT                         │
└─────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
     ┌──────▼─────┐                 ┌──────▼─────┐
     │   AGENTS   │                 │   TOOLS    │
     │            │◄────uses────────│            │
     └──────┬─────┘                 └──────┬─────┘
            │                               │
            │                               │
    agents/agents.py              tools/tools.py
    - root_agent                  - read_cv()
    - [future agents]             - list_available_cvs()
                                  - compare_candidates()
```

## ✅ What Changed (Better Architecture)

### BEFORE ❌ (Manual File Handling)
```python
# Agent with google_search tool it doesn't need
agent = Agent(
    tools=[google_search],
    ...
)

# Manual file reading in notebook
cv_content = Path("cv.txt").read_text()
prompt = f"Analyze this CV: {cv_content}"
response = await runner.run_debug(prompt)
```

### AFTER ✅ (Tool-Driven Architecture)
```python
# Custom tools defined in tools/tools.py
def read_cv(filename: str) -> str:
    """Read CV file from dummy_files_for_testing."""
    # Implementation
    
# Agent with relevant custom tools
agent = Agent(
    tools=[read_cv, list_available_cvs, compare_candidates],
    ...
)

# Simple, natural prompts - agent handles file reading
prompt = "Please read and analyze cv_john_doe.txt"
response = await runner.run_debug(prompt)
```

## 🎯 Key Benefits

### 1. **Separation of Concerns**
- ✅ **Tools** (`tools/tools.py`): Define what the agent CAN do
- ✅ **Agents** (`agents/agents.py`): Define how the agent SHOULD behave
- ✅ **Notebooks**: Test and use agents naturally

### 2. **Agent-Driven Behavior**
- Agent decides WHEN to use tools based on the query
- No manual file handling in prompts
- More natural conversation flow

### 3. **Reusability**
- Tools can be shared across multiple agents
- Easy to test tools independently
- Clean imports via `__init__.py` structure

### 4. **Maintainability**
- One place to define tools: `tools/tools.py`
- One place to define agents: `agents/agents.py`
- Clear project structure

## 📁 Project Structure

```
capstone-project-google-kaggle/
│
├── tools/
│   ├── __init__.py              # Exports: read_cv, list_available_cvs, compare_candidates
│   ├── tools.py                 # Tool implementations
│   └── test_debug_tools.ipynb   # Test tools independently
│
├── agents/
│   ├── __init__.py              # Exports: root_agent, Agent, InMemoryRunner
│   ├── agents.py                # Agent definitions (uses tools from tools/)
│   └── test_debug_agents.ipynb  # Test agents with tools
│
├── dummy_files_for_testing/
│   ├── cv_john_doe.txt
│   ├── cv_john_doe.pdf
│   ├── cv_maria_santos.txt
│   └── cv_maria_santos.pdf
│
└── main.py                      # Streamlit app (can import agents and tools)
```

## 🔧 Custom Tools Available

### 1. `read_cv(filename: str) -> str`
**What it does:** Reads a CV file from `dummy_files_for_testing/` folder

**Tool Function (tools/tools.py):**
```python
def read_cv(filename: Annotated[str, "CV filename"]) -> str:
    """Read a CV file from the dummy_files_for_testing folder."""
    # Handles .txt and .pdf files
    # Returns formatted CV content
```

**Agent uses it when:**
- "Read cv_john_doe.txt"
- "Analyze the CV file cv_maria_santos.txt"
- "What's in John Doe's resume?"

### 2. `list_available_cvs() -> str`
**What it does:** Lists all CV files available for analysis

**Tool Function:**
```python
def list_available_cvs() -> str:
    """List all available CV files."""
    # Scans dummy_files_for_testing/
    # Returns formatted list
```

**Agent uses it when:**
- "What CVs are available?"
- "Show me the candidates"
- "List all resumes"

### 3. `compare_candidates(filename1, filename2, criteria) -> str`
**What it does:** Compares two candidates based on specific criteria

**Tool Function:**
```python
def compare_candidates(
    filename1: str, 
    filename2: str, 
    criteria: str
) -> str:
    """Compare two candidates."""
    # Reads both CVs
    # Provides comparison context
```

**Agent uses it when:**
- "Compare John Doe and Maria Santos"
- "Who has more Python experience between these two?"
- "Compare cv_john_doe.txt and cv_maria_santos.txt"

## 🧑‍🏭 Agent Definition

**Location:** `agents/agents.py`

```python
from tools import read_cv, list_available_cvs, compare_candidates

root_agent = Agent(
    name="cv_analysis_agent",
    model="gemini-2.0-flash-exp",
    description="Agent to read and analyze CVs.",
    instruction="""
    You are a helpful assistant to the human resources department.
    
    Your capabilities:
    - Read CV files using the read_cv tool
    - List available CVs using the list_available_cvs tool
    - Compare candidates using the compare_candidates tool
    
    When analyzing CVs, provide thorough and professional analysis.
    """,
    tools=[read_cv, list_available_cvs, compare_candidates],  # ← Custom tools!
)
```

**Key Points:**
- ✅ Uses custom tools, not `google_search`
- ✅ Clear instructions on tool capabilities
- ✅ Tools handle file access automatically

## 🚀 Usage Examples

### Example 1: List Available CVs
```python
from agents import root_agent, InMemoryRunner

runner = InMemoryRunner(agent=root_agent)
response = await runner.run_debug("What CV files are available?")
```

**What happens:**
1. Agent sees query about available CVs
2. Agent calls `list_available_cvs()` tool
3. Tool returns list of files
4. Agent formats response for user

### Example 2: Analyze Single CV
```python
prompt = """
Please analyze cv_john_doe.txt for a Senior Python Developer role.
Requirements:
- 5+ years Python
- Microservices experience
"""

response = await runner.run_debug(prompt)
```

**What happens:**
1. Agent sees query about analyzing specific CV
2. Agent calls `read_cv("cv_john_doe.txt")`
3. Tool returns CV content
4. Agent analyzes against requirements
5. Agent provides assessment

### Example 3: Compare Candidates
```python
prompt = "Compare John Doe and Maria Santos for Python expertise"
response = await runner.run_debug(prompt)
```

**What happens:**
1. Agent determines comparison needed
2. Agent calls `compare_candidates()` tool
3. Tool reads both CVs
4. Agent analyzes and compares
5. Agent provides recommendation

## 💡 How to Add New Tools

### Step 1: Define Tool in `tools/tools.py`

```python
from typing import Annotated

def assess_coding_skills(
    filename: Annotated[str, "CV filename"],
    language: Annotated[str, "Programming language to assess"]
) -> str:
    """
    Assess candidate's coding skills in a specific language.
    Agent can use this to evaluate technical proficiency.
    """
    cv_content = read_cv(filename)
    
    # Your assessment logic here
    assessment = analyze_coding_experience(cv_content, language)
    
    return f"Coding assessment for {language}: {assessment}"
```

### Step 2: Export in `tools/__init__.py`

```python
from .tools import (
    read_cv,
    list_available_cvs,
    compare_candidates,
    assess_coding_skills,  # ← Add new tool
)

__all__ = [
    'read_cv',
    'list_available_cvs',
    'compare_candidates',
    'assess_coding_skills',  # ← Add new tool
]
```

### Step 3: Add to Agent's Tools

```python
from tools import (
    read_cv, 
    list_available_cvs, 
    compare_candidates,
    assess_coding_skills,  # ← Import new tool
)

root_agent = Agent(
    name="cv_analysis_agent",
    tools=[
        read_cv, 
        list_available_cvs, 
        compare_candidates,
        assess_coding_skills,  # ← Add to agent
    ],
    ...
)
```

### Step 4: Test It

```python
# In test_debug_agents.ipynb
prompt = "Assess John Doe's Python coding skills"
response = await runner.run_debug(prompt)
```

## 📝 Best Practices

### ✅ DO:
1. **Define tools in `tools/tools.py`** with clear docstrings
2. **Use `Annotated` type hints** to describe parameters
3. **Return strings** that the agent can easily understand
4. **Handle errors gracefully** with friendly error messages
5. **Test tools independently** in `test_debug_tools.ipynb`
6. **Give agents clear instructions** about tool capabilities

### ❌ DON'T:
1. Don't include tools the agent doesn't need (like `google_search` for CV analysis)
2. Don't manually read files in prompts - let tools do it
3. Don't return complex objects - return formatted strings
4. Don't forget to export tools in `__init__.py`
5. Don't skip error handling in tools

## 🎓 Summary

**Old Way (Manual):**
```python
# Read file manually
cv = Path("cv.txt").read_text()
# Paste content in prompt
prompt = f"Analyze: {cv}"
```

**New Way (Tool-Driven):**
```python
# Just ask naturally
prompt = "Analyze cv_john_doe.txt"
# Agent uses tools automatically!
```

This architecture makes your code:
- 🧹 **Cleaner** - Separation of concerns
- 🔄 **Reusable** - Tools work across agents
- 🧪 **Testable** - Test tools independently
- 📈 **Scalable** - Easy to add new tools/agents
- 💬 **Natural** - Conversational interactions

---

**Next Steps:**
1. Run `test_debug_agents.ipynb` to see agent + tools in action
2. Run `test_debug_tools.ipynb` to test tools independently
3. Add new tools for your specific use cases
4. Create specialized agents for different HR tasks

