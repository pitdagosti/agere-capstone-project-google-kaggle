# 🔐 Environment Setup Guide

## Quick Start

1. **Copy the template:**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` and add your API key:**
   ```bash
   # Required
   GOOGLE_API_KEY=your_actual_api_key_here
   GOOGLE_GENAI_USE_VERTEXAI=FALSE
   ```

3. **Get your API key:**
   - Go to: https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy and paste into `.env`

## Your `.env` File Should Look Like:

```bash
# =============================================================================
# Google AI Configuration (Required for ADK Agents)
# =============================================================================

# Google API Key - Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=AIzaSyB_your_actual_key_here_xxxxxxxxxxxxxxxxxxx

# Use Google AI Studio (FALSE) or Vertex AI (TRUE)
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# =============================================================================
# Application Settings
# =============================================================================

DEBUG_MODE=False
LOG_LEVEL=INFO
```

## What Each Variable Does

### Required Variables:

**`GOOGLE_API_KEY`**
- Your Google AI API key
- Get it from: https://makersuite.google.com/app/apikey
- Used to authenticate with Google's Gemini models

**`GOOGLE_GENAI_USE_VERTEXAI`**
- `FALSE` = Use Google AI Studio (recommended for development)
- `TRUE` = Use Google Cloud Vertex AI (for production/enterprise)

### When using Vertex AI (if `GOOGLE_GENAI_USE_VERTEXAI=TRUE`):

**`GOOGLE_CLOUD_PROJECT`**
- Your Google Cloud Project ID
- Required for Vertex AI

**`GOOGLE_CLOUD_LOCATION`**
- Region for Vertex AI (e.g., `us-central1`)
- Defaults to `us-central1` if not specified

## Verification

After creating your `.env` file, run the notebook and you should see:

```
============================================================
🔧 Environment Configuration
============================================================
✅ GOOGLE_API_KEY: AIzaSyBxxx...xxxx
✅ GOOGLE_GENAI_USE_VERTEXAI: FALSE
   → Using Google AI Studio
============================================================
✅ ADK components and custom tools imported successfully.
✅ CV Analysis Agent defined with custom tools and API key.
```

## Two Ways to Use Google AI

### Option 1: Google AI Studio (Recommended for Development)

**Pros:**
- ✅ Free tier available
- ✅ Easy setup (just need API key)
- ✅ Perfect for development/testing
- ✅ No Google Cloud project needed

**Setup:**
```bash
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=your_key_from_ai_studio
```

**Get API Key:** https://makersuite.google.com/app/apikey

### Option 2: Google Cloud Vertex AI (For Production)

**Pros:**
- ✅ Higher rate limits
- ✅ Better for production
- ✅ Enterprise features
- ✅ Integration with GCP services

**Setup:**
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_API_KEY=your_vertex_ai_key
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

**Additional Steps:**
1. Set up Google Cloud project
2. Enable Vertex AI API
3. Install gcloud CLI
4. Authenticate: `gcloud auth application-default login`

## File Location

**Your `.env` file should be at the project root:**

```
capstone-project-google-kaggle/
├── .env  ← HERE! (create this file)
├── env.example  ← Template (don't edit)
├── agents/
│   ├── agents.py
│   └── test_debug_agents.ipynb
├── tools/
│   └── tools.py
└── main.py
```

## Security

✅ **Safe:**
- `.env` is in `.gitignore` (won't be committed)
- Only exists on your local machine

⚠️ **Never:**
- Commit `.env` to git
- Share your API key
- Hard-code keys in notebooks/code
- Upload `.env` to GitHub/public places

## Troubleshooting

### "WARNING: GOOGLE_API_KEY not found"

**Fix:**
1. Check file is named exactly `.env` (not `.env.txt`)
2. Check file is in project root directory
3. Check format: `GOOGLE_API_KEY=your_key` (no spaces around `=`)
4. Restart Jupyter kernel

### "WARNING: GOOGLE_GENAI_USE_VERTEXAI not set"

**Fix:**
Add this line to your `.env`:
```bash
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

### "Missing key inputs argument"

**Fix:**
1. Verify `.env` file exists and contains `GOOGLE_API_KEY`
2. Run Cell 1 in notebook to load environment
3. Check API key is valid (regenerate if needed)

### API key works but getting rate limit errors

**Fix:**
Consider switching to Vertex AI:
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

## Complete Example `.env` File

```bash
# =============================================================================
# Google AI Configuration (Required for ADK Agents)
# =============================================================================

# Option 1: Using Google AI Studio (Recommended for Development)
GOOGLE_API_KEY=AIzaSyB_your_actual_key_here_xxxxxxxxxxxxxxxxxxx
GOOGLE_GENAI_USE_VERTEXAI=FALSE

# Option 2: Using Vertex AI (Uncomment if using Vertex AI)
# GOOGLE_GENAI_USE_VERTEXAI=TRUE
# GOOGLE_CLOUD_PROJECT=my-gcp-project-id
# GOOGLE_CLOUD_LOCATION=us-central1

# =============================================================================
# Optional: Other Services
# =============================================================================

# OpenAI (if needed)
# OPENAI_API_KEY=sk-your_openai_key

# Anthropic Claude (if needed)
# ANTHROPIC_API_KEY=sk-ant-your_claude_key

# =============================================================================
# Application Settings
# =============================================================================

DEBUG_MODE=False
LOG_LEVEL=INFO
```

## Next Steps

1. ✅ Create `.env` file at project root
2. ✅ Add `GOOGLE_API_KEY=your_key`
3. ✅ Add `GOOGLE_GENAI_USE_VERTEXAI=FALSE`
4. ✅ Run notebook Cell 1 to verify
5. ✅ Check for ✅ messages
6. ✅ Start using your agent!

---

**Resources:**
- Get API Key: https://makersuite.google.com/app/apikey
- ADK Documentation: https://google.github.io/adk-docs/
- Vertex AI Setup: https://cloud.google.com/vertex-ai/docs/start/introduction-unified-platform

