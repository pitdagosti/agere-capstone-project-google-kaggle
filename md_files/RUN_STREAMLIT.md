# 🚀 Running the AGERE Streamlit App

## Quick Start

### 1. Make sure your environment is set up:

```bash
# Activate your virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install requirements (if not already done)
pip install -r requirements.txt
```

### 2. Verify your `.env` file has:

```bash
GOOGLE_API_KEY=your_actual_api_key_here
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

### 3. Run the Streamlit app:

```bash
streamlit run main.py
```

### 4. Open your browser:

The app should automatically open at `http://localhost:8501`

## 🎯 How to Use the App

### Step 1: Upload a CV

1. Click "Browse files" or drag and drop a CV file (PDF or TXT)
2. Supported formats: `.pdf`, `.txt`
3. See file details displayed

### Step 2: Analyze the CV

1. Click the **"🔍 Analyze CV"** button
2. Wait for the AI agent to analyze (usually 5-10 seconds)
3. See comprehensive analysis displayed

### Step 3: Chat with the AI Recruiter

After initial analysis, you can:

- **Ask follow-up questions:**
  - "What are the candidate's strongest skills?"
  - "Is this candidate suitable for a senior position?"
  - "What languages does the candidate speak?"

- **Request specific analysis:**
  - "Compare this candidate to a Senior Python Developer role"
  - "What's the candidate's experience with microservices?"
  - "Assess their leadership capabilities"

- **Get recommendations:**
  - "Should we interview this candidate?"
  - "What questions should we ask in the interview?"
  - "What are potential concerns?"

### Step 4: Clear and Start Over

Click **"🗑️ Clear"** to:
- Remove the uploaded file
- Clear chat history
- Reset for a new candidate

## 📋 Expected Output

### Initial Analysis:

When you click "Analyze CV", the agent will provide:

```
🔍 Initial CV Analysis

**Candidate Information:**
- Name: John Doe
- Email: john.doe@email.com
- Phone: +1 (555) 123-4567
- Location: San Francisco, CA

**Technical Skills:**
- Python: Advanced (5 years)
- Java: Intermediate (3 years)
- Frameworks: Django, Flask, FastAPI, Spring Boot
...

**Work Experience Summary:**
...

**Educational Background:**
...

**Overall Assessment:**
...
```

### Chat Interaction:

```
💬 Chat with AI Recruiter

You: What are the candidate's strongest skills?

🤖 Assistant: Based on the CV analysis, the candidate's strongest 
skills are:
1. Python development (5 years, advanced level)
2. Microservices architecture
3. Leadership (led team of 4 developers)
...
```

## ⚙️ Features

### Current Features ✅

1. **CV Upload** - PDF and TXT support
2. **AI Analysis** - Comprehensive CV analysis using Gemini
3. **Chat Interface** - Interactive Q&A about candidates
4. **File Preview** - View uploaded CV content
5. **Session Management** - Maintains context during chat

### Coming Soon 🚧

1. **Job Matching** - Compare CV against job descriptions
2. **Multiple Candidates** - Compare several candidates
3. **Interview Prep** - Generate interview questions
4. **Assessment Creation** - Create technical assessments
5. **Scheduling** - Interview scheduling assistance

## 🔧 Troubleshooting

### Issue 1: "GOOGLE_API_KEY not found"

**Fix:**
1. Check `.env` file exists in project root
2. Verify it contains `GOOGLE_API_KEY=your_key`
3. Restart the Streamlit app

### Issue 2: Agent doesn't respond

**Symptoms:** Spinner shows but no response appears

**Fix:**
1. Check your internet connection
2. Verify API key is valid
3. Check terminal for error messages
4. Try a more explicit prompt: "Please analyze and write a summary..."

### Issue 3: File upload fails

**Fix:**
1. Check file size (should be < 200MB)
2. Verify file format (PDF or TXT only)
3. Check `temp_uploads/` directory has write permissions

### Issue 4: Chat doesn't maintain context

**Fix:**
- Click "🗑️ Clear" and re-upload the CV
- Restart the Streamlit app
- Check browser console for errors

## 💡 Tips for Best Results

### Writing Good Prompts:

✅ **Good Prompts:**
- "Analyze the candidate's Python experience in detail"
- "Compare this candidate to a Senior Developer role requiring 5+ years experience"
- "What concerns should we have about this candidate?"

❌ **Less Effective:**
- "Skills?" (too vague)
- "Good?" (no context)
- Single word questions

### Getting Better Analysis:

1. **Be specific**: Ask detailed questions
2. **Provide context**: Mention the role or requirements
3. **Follow up**: Ask clarifying questions
4. **Use the chat**: Take advantage of multi-turn conversation

## 🛠️ Advanced Usage

### Analyzing Multiple CVs:

1. Analyze first CV
2. Note down key findings
3. Click "Clear"
4. Upload second CV
5. In chat, mention: "How does this compare to the previous candidate?"

### Custom Analysis:

Ask agent for specific formats:
```
"Create a table comparing the candidate's skills to these requirements:
- Python: 5+ years
- Docker: Required
- Leadership: Preferred"
```

## 📊 Architecture

### How It Works:

```
Streamlit UI
    ↓
Upload CV → Save to temp_uploads/
    ↓
Agent Reads File (using read_cv tool)
    ↓
Gemini API Analyzes Content
    ↓
Response Displayed in Chat
    ↓
User Asks Follow-up → Agent Responds
```

### Session Management:

- `st.session_state.runner`: Agent runner instance
- `st.session_state.messages`: Chat history
- `st.session_state.current_cv_file`: Currently analyzed CV

## 🔒 Security Notes

- ✅ `.env` file not committed (contains API key)
- ✅ `temp_uploads/` directory not committed
- ✅ Uploaded files stored temporarily
- ⚠️ Clean up old files in `temp_uploads/` periodically

## 📱 Deployment (Future)

To deploy to production:

1. **Streamlit Cloud:**
   ```bash
   # Add secrets in Streamlit Cloud dashboard
   GOOGLE_API_KEY = "your_key"
   GOOGLE_GENAI_USE_VERTEXAI = "FALSE"
   ```

2. **Heroku/Railway:**
   - Set environment variables in platform
   - Use build packs for Python
   - Configure startup command: `streamlit run main.py`

3. **Docker:**
   ```dockerfile
   FROM python:3.13
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["streamlit", "run", "main.py"]
   ```

---

**Ready to go! Run `streamlit run main.py` and start analyzing CVs!** 🚀

