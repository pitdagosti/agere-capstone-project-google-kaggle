# 🔧 Troubleshooting: Agent Can't Find GOOGLE_API_KEY

## The Problem

When running the agent, you get an error like:
```
ValueError: Missing key inputs argument! To use the Google AI API, 
provide (`api_key`) arguments.
```

**Even though Cell 1 shows "✅ GOOGLE_API_KEY: OK"**

## Why This Happens

`load_dotenv()` loads variables into **your Python process**, but ADK auto-initialization reads from **system environment variables**. There's a timing issue where:

1. ✅ Cell 1 loads `.env` → Variables available to your code
2. ❌ ADK imports happen → ADK doesn't see the variables yet
3. ❌ Agent runs → ADK tries to auto-initialize → Can't find API key

## The Fix ✅

**Load `.env` BEFORE importing ADK modules!**

### Before (Wrong Order):
```python
# ❌ BAD: Import ADK first
from google.adk.agents import Agent

# Then load .env (too late!)
load_dotenv()
```

### After (Correct Order):
```python
# ✅ GOOD: Load .env FIRST
load_dotenv()

# Explicitly set in os.environ (critical!)
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key

# NOW import ADK (environment is ready)
from google.adk.agents import Agent
```

## What I Changed in Your Notebook

### Cell 1 - Fixed Import Order:

```python
# Step 1: Load .env FIRST
from dotenv import load_dotenv
import os
from pathlib import Path

project_root = Path().absolute().parent
load_dotenv(dotenv_path=project_root / ".env")

# Step 2: Get and SET environment variables
api_key = os.getenv("GOOGLE_API_KEY")
use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")

# CRITICAL: Explicitly set them
os.environ["GOOGLE_API_KEY"] = api_key
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = use_vertexai

# Step 3: NOW import ADK (after environment is set)
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
```

**Key addition:** `os.environ["GOOGLE_API_KEY"] = api_key`

This **explicitly sets** the environment variable, ensuring ADK can read it.

## Verify It Works

After running Cell 1, you should see:

```
============================================================
🔧 Environment Configuration
============================================================
✅ GOOGLE_API_KEY: AIzaSyBxxx...xxxx
✅ GOOGLE_GENAI_USE_VERTEXAI: FALSE
   → Using Google AI Studio
============================================================
✅ ADK components and custom tools imported successfully.
✅ Environment variables set for ADK auto-initialization
```

**Notice the new line:** "✅ Environment variables set for ADK auto-initialization"

## Test It

Now try running your agent (Cell 5):

```python
response = await runner.run_debug("What CV files are available?")
```

**It should work now!** ✅

## Other Possible Issues

### Issue 1: `.env` File Not Found

**Symptom:**
```
⚠️ WARNING: GOOGLE_API_KEY not found!
Looking for .env at: /path/to/project/.env
```

**Fix:**
1. Make sure `.env` file exists in project root
2. Check the path shown in the warning message
3. Create `.env` with: `GOOGLE_API_KEY=your_key`

### Issue 2: Invalid API Key

**Symptom:**
```
google.api_core.exceptions.PermissionDenied: 403 API key not valid
```

**Fix:**
1. Go to https://makersuite.google.com/app/apikey
2. Generate a new API key
3. Update `.env` file
4. Restart Jupyter kernel
5. Re-run Cell 1

### Issue 3: Jupyter Kernel Not Restarted

**Symptom:**
Old environment variables still cached

**Fix:**
1. Restart Jupyter kernel
2. Re-run all cells from the top

## Alternative: Use Explicit Client

If auto-initialization still doesn't work, you can fall back to explicit Client:

```python
from google.genai import Client

# Explicit configuration (always works)
client = Client(api_key=os.getenv("GOOGLE_API_KEY"))

root_agent = Agent(
    ...,
    api_client=client,  # Pass explicitly
)
```

But the fix I implemented should work with auto-initialization!

## Key Takeaway

**Order matters!**

✅ **Correct Order:**
1. Load `.env`
2. Set `os.environ`
3. Import ADK
4. Create Agent

❌ **Wrong Order:**
1. Import ADK
2. Load `.env` (too late!)
3. Create Agent (fails!)

---

Your notebook is now fixed with the correct order! 🎉

