# ⚡ Quick Setup Instructions

## Create Your `.env` File NOW!

**Step 1:** Copy the template:
```bash
cp env.example .env
```

**Step 2:** Edit `.env` and add these two lines:

```bash
GOOGLE_API_KEY=your_actual_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

**Step 3:** Get your Google API key from:
👉 https://makersuite.google.com/app/apikey

**Step 4:** Paste your API key into the `.env` file

## Your `.env` File Should Look Like:

```bash
# =============================================================================
# Google AI Configuration (Required)
# =============================================================================

GOOGLE_API_KEY=AIzaSyB_your_actual_key_xxxxxxxxxxxxxxxxxxx
GOOGLE_GENAI_USE_VERTEXAI=FALSE

DEBUG_MODE=False
LOG_LEVEL=INFO
```

## That's It!

Now run your notebook and you should see:

```
============================================================
🔧 Environment Configuration
============================================================
✅ GOOGLE_API_KEY: AIzaSyBxxx...xxxx
✅ GOOGLE_GENAI_USE_VERTEXAI: FALSE
   → Using Google AI Studio
============================================================
✅ ADK components and custom tools imported successfully.
🌐 Initialized Google AI Studio Client
✅ CV Analysis Agent defined with custom tools and API key.
✅ Runner created.
```

## Need Help?

- **Full guide:** Read `ENV_SETUP.md`
- **API key help:** Read `API_KEY_SETUP.md`
- **Can't find .env:** Make sure it's in the project root directory!

---

**⚠️ Important:**
- File must be named exactly `.env` (not `.env.txt`)
- File must be in project root (same folder as `main.py`)
- Never commit `.env` to git (it's already in `.gitignore`)

