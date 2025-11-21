# 🚀 Quick Start Guide - Tool-Driven Architecture

## What We Built

You now have a **professional tool-driven agent architecture** where:
- ✅ Custom tools are defined once in `tools/tools.py`
- ✅ Agents use these tools via `tools=[...]` parameter
- ✅ No manual file handling needed - agent does it automatically!

## 📦 What's Available

### 3 Custom Tools:
1. **`read_cv(filename)`** - Read any CV file
2. **`list_available_cvs()`** - List all available CVs
3. **`compare_candidates(file1, file2, criteria)`** - Compare two candidates

### 1 AI Agent:
- **`root_agent`** - CV Analysis Agent with all 3 tools

### Test Files:
- `cv_john_doe.txt` / `.pdf`
- `cv_maria_santos.txt` / `.pdf`

## 🎯 How to Use

### Step 1: Run Test Notebooks

**Test Tools First:**
```bash
# Open and run: tools/test_debug_tools.ipynb
# This tests each tool independently
```

**Then Test Agent:**
```bash
# Open and run: agents/test_debug_agents.ipynb
# This tests the agent using the tools
```

### Step 2: Try These Prompts

In `agents/test_debug_agents.ipynb`:

```python
# Cell 4: List available CVs
"What CV files are available for analysis?"

# Cell 5: Analyze single CV
"Please read and analyze cv_john_doe.txt for a Senior Python Developer role"

# Cell 6: Compare candidates
"Compare John Doe and Maria Santos for Python expertise"

# Cell 8: Open-ended (agent chooses tools)
"I need to hire a Senior Python Developer. Help me find the best candidate."
```

## 🏗️ Architecture

```
Your Query
    ↓
Agent (with tools=[read_cv, list_available_cvs, compare_candidates])
    ↓
Agent decides which tool to use
    ↓
Tool reads file from dummy_files_for_testing/
    ↓
Tool returns content
    ↓
Agent analyzes and responds
```

## 🔑 Key Differences

### OLD WAY ❌
```python
# Manual file reading
cv_content = open("cv.txt").read()
prompt = f"Analyze this: {cv_content}"  # Paste entire file!
response = await runner.run_debug(prompt)
```

### NEW WAY ✅
```python
# Agent handles everything
prompt = "Analyze cv_john_doe.txt"  # Just the filename!
response = await runner.run_debug(prompt)
# Agent automatically uses read_cv tool
```

## 📝 File Locations

```
📁 capstone-project-google-kaggle/
│
├── 📁 tools/
│   ├── tools.py                 ⭐ DEFINE TOOLS HERE
│   ├── __init__.py              (exports tools)
│   └── test_debug_tools.ipynb   (test tools)
│
├── 📁 agents/
│   ├── agents.py                ⭐ DEFINE AGENTS HERE (use tools)
│   ├── __init__.py              (exports agents)
│   └── test_debug_agents.ipynb  ⭐ START HERE - Test everything
│
├── 📁 dummy_files_for_testing/
│   ├── cv_john_doe.txt          📄 Test data
│   ├── cv_john_doe.pdf          📄 Test data
│   ├── cv_maria_santos.txt      📄 Test data
│   └── cv_maria_santos.pdf      📄 Test data
│
└── 📄 Documentation:
    ├── ARCHITECTURE.md          (detailed architecture docs)
    ├── HOW_TO_USE_FILES.md      (how to include files)
    └── QUICK_START.md           (this file)
```

## ✨ Benefits of This Approach

### 1. **Clean Code**
- Tools in one place: `tools/tools.py`
- Agents in one place: `agents/agents.py`
- Clear separation of concerns

### 2. **Natural Conversations**
```python
# Just talk naturally to the agent:
"What candidates do you have?"
"Analyze John Doe's CV"
"Compare John and Maria for Python skills"
```

### 3. **Reusable**
```python
# Same tool, multiple agents:
agent1 = Agent(tools=[read_cv, ...])
agent2 = Agent(tools=[read_cv, ...])
agent3 = Agent(tools=[read_cv, ...])
```

### 4. **Easy to Test**
```python
# Test tool directly:
result = read_cv("cv_john_doe.txt")
print(result)

# Test agent with tool:
response = await runner.run_debug("Read cv_john_doe.txt")
```

## 🚦 Next Steps

1. **✅ Run `agents/test_debug_agents.ipynb`** - See it in action
2. **✅ Run `tools/test_debug_tools.ipynb`** - Test tools independently
3. **📖 Read `ARCHITECTURE.md`** - Understand the system deeply
4. **🔧 Add your own tools** - Follow the pattern in `tools/tools.py`
5. **🤖 Create specialized agents** - For different HR tasks

## 💡 Pro Tips

1. **Tools should return strings** - Makes it easy for agents to understand
2. **Use Annotated type hints** - Helps agent know what parameters mean
3. **Write clear docstrings** - Agent reads these to understand the tool
4. **Handle errors gracefully** - Return friendly error messages
5. **Test tools independently first** - Before using in agents

## 🆘 Troubleshooting

**Problem:** "No module named 'tools'"
```python
# Solution: Add parent to path (already in notebooks)
import sys
from pathlib import Path
project_root = Path().absolute().parent
sys.path.insert(0, str(project_root))
```

**Problem:** "File not found"
```python
# Solution: Use just the filename, not full path
# ✅ Correct: "cv_john_doe.txt"
# ❌ Wrong: "../dummy_files_for_testing/cv_john_doe.txt"
```

**Problem:** Agent not using tools
```python
# Solution: Be explicit in your prompt
# ✅ "Please read cv_john_doe.txt and analyze it"
# Rather than: "Tell me about John Doe"
```

## 🎓 Learning Path

1. **Start Here:** `agents/test_debug_agents.ipynb` Cell 4
2. **Understand:** See how agent uses `list_available_cvs` automatically
3. **Experiment:** Try Cell 5 - agent uses `read_cv` automatically
4. **Advanced:** Try Cell 8 - open-ended query, agent chooses tools
5. **Create:** Add your own tool following the pattern

---

**🎉 You're all set! Your agent can now intelligently use custom tools to analyze CVs!**

Start with `agents/test_debug_agents.ipynb` and run the cells to see it in action.

