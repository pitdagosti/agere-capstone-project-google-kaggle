# 🔑 API Key Setup Guide

## Setting Up Your Google API Key

Your agent needs a Google API key to access Gemini models. Here's how to set it up:

## Step 1: Get Your Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

## Step 2: Create a `.env` File

1. In your project root directory (`capstone-project-google-kaggle/`), create a file named `.env`
2. Add your API key and configuration:

```bash
# .env file (at project root)
GOOGLE_API_KEY=your_actual_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

**Important:** The `GOOGLE_GENAI_USE_VERTEXAI=FALSE` line tells ADK to use Google AI Studio instead of Vertex AI.

**⚠️ IMPORTANT:**
- Never commit the `.env` file to git (it's already in `.gitignore`)
- Never share your API key publicly
- The `.env` file should be at the root of your project

## Step 3: Verify Setup

Run your notebook and check for this message:

```
✅ API Key loaded: AIzaSyBxxx...xxxx
✅ ADK components and custom tools imported successfully.
✅ CV Analysis Agent defined with custom tools and API key.
```

If you see:
```
⚠️ WARNING: GOOGLE_API_KEY not found in .env file!
```

Then check:
1. Is the `.env` file in the project root?
2. Is the file named exactly `.env` (not `.env.txt`)?
3. Is the key name exactly `GOOGLE_API_KEY=`?
4. Is there a value after the `=`?

## Project Structure

```
capstone-project-google-kaggle/
├── .env                    ← Your API key goes here!
├── env.example             ← Template file (don't edit this)
├── agents/
│   └── test_debug_agents.ipynb
├── tools/
│   └── tools.py
└── ...
```

## How It Works

### In Notebooks (`test_debug_agents.ipynb`)

```python
# Cell 1: Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file
api_key = os.getenv("GOOGLE_API_KEY")  # Gets the key

# Cell 2: Pass to agent
from google.genai import Client

client = Client(api_key=os.getenv("GOOGLE_API_KEY"))
root_agent = Agent(
    name="cv_analysis_agent",
    model="gemini-2.0-flash-exp",
    tools=[read_cv, list_available_cvs, compare_candidates],
    api_client=client,  # ← Agent uses your API key
)
```

### In Python Files (`agents/agents.py`)

```python
from dotenv import load_dotenv
import os
from google.genai import Client

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
client = Client(api_key=api_key)

root_agent = Agent(
    ...,
    api_client=client,  # ← API key is passed here
)
```

## Alternative: Using Vertex AI (Google Cloud)

If you have a Google Cloud account, you can use Vertex AI instead:

```python
from google.genai import Client

client = Client(
    vertexai=True,
    project="your-gcp-project-id",
    location="us-central1"
)

root_agent = Agent(
    ...,
    api_client=client,
)
```

For Vertex AI, add to your `.env`:
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

## Troubleshooting

### Error: "Missing key inputs argument!"

**Problem:** Agent can't find API key

**Solutions:**
1. Check `.env` file exists in project root
2. Check key is named `GOOGLE_API_KEY`
3. Restart your Jupyter kernel
4. Re-run Cell 1 to reload environment variables

### Error: "Permission denied" or "Invalid API key"

**Problem:** API key is invalid or expired

**Solutions:**
1. Generate a new API key from Google AI Studio
2. Replace the old key in `.env`
3. Restart your notebook

### The agent isn't responding

**Problem:** API key not passed to agent

**Solution:** Make sure you're passing `api_client=client` when creating the Agent:

```python
root_agent = Agent(
    ...,
    api_client=client,  # ← Don't forget this!
)
```

## Security Best Practices

✅ **DO:**
- Keep `.env` in `.gitignore`
- Use environment variables for all secrets
- Regenerate keys if accidentally exposed
- Use different keys for dev/production

❌ **DON'T:**
- Commit `.env` to git
- Hard-code API keys in code
- Share API keys in screenshots
- Use production keys for testing

## Rate Limits & Costs

- **Google AI Studio (Free Tier):**
  - 60 requests per minute
  - Free for development and testing
  
- **Vertex AI (Google Cloud):**
  - Pay-as-you-go pricing
  - Higher rate limits
  - Better for production

Check current pricing: https://ai.google.dev/pricing

## Quick Checklist

Before running your agent:
- [ ] Created `.env` file in project root
- [ ] Added `GOOGLE_API_KEY=your_key_here`
- [ ] Verified `.env` is not committed to git
- [ ] Imported `load_dotenv()` and `os.getenv()` in notebook
- [ ] Passed `api_client=client` to Agent
- [ ] Ran Cell 1 to load environment variables
- [ ] Checked for "✅ API Key loaded" message

---

**Need help?**
- Google AI Studio: https://makersuite.google.com/
- Documentation: https://ai.google.dev/docs
- Pricing: https://ai.google.dev/pricing

