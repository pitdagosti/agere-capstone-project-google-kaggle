# AGERE (Agentic Interview Readiness) - Complete Code Analysis

**Project**: PROJECT AGERE - Agentic Recruiter  
**Framework**: Google ADK (Agent Development Kit) with Gemini 2.5 Flash Lite  
**Frontend**: Streamlit  
**Status**: Phase 1 Complete, Phase 2 In Progress  
**Team**: Pietro D'Agostino, Abdul Basit Memon, Amos Bocelli, Asterios Terzis

---

## 1. PROJECT OVERVIEW

### Purpose
AGERE is an **AI-powered career coaching system** that helps job candidates:
- Analyze their CV/resume
- Match skills to job opportunities
- Validate expertise through assessments
- Schedule interviews with confidence

### Architecture Pattern
- **Hub-and-Spoke Multi-Agent System**: Central Orchestrator coordinates 4 specialized agents
- **Google ADK Framework**: Uses Agent Development Kit with Gemini 2.5 Flash Lite
- **MCP Integration**: Model Context Protocol for Google Calendar scheduling
- **Secure Code Execution**: Sandboxed environment for coding assessments

### Technology Stack
| Category | Technology |
|----------|-----------|
| **Web Framework** | Streamlit 1.39+ |
| **AI Framework** | Google ADK 0.1.0+ |
| **LLM Model** | Gemini 2.5 Flash Lite |
| **PDF Processing** | pdfplumber, PyPDF2 |
| **Code Sandbox** | multiprocessing, resource limits |
| **Calendar API** | Google Calendar API v3, OAuth2 |
| **Backend** | Python 3.10+ |
| **Web Server** | Flask (MCP Server) |

---

## 2. PROJECT STRUCTURE

```
capstone-project-google-kaggle/
├── main.py                          # Entry point - Streamlit UI
├── requirements.txt                 # Python dependencies
├── .env                            # API keys (gitignored)
├── env.example                     # Environment template
│
├── src/                            # Source code
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agents.py              # 4 agents + orchestrator
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tools.py               # CV & job listing tools
│   │   ├── code_sandbox.py        # Secure execution environment
│   │   └── mcp_client.py          # Calendar REST client
│   └── styles/
│       └── custom.css             # Streamlit styling
│
├── mcp_server/
│   ├── __init__.py
│   ├── calendar_server.py         # Flask API for Google Calendar
│   └── calendar.db                # SQLite (placeholder)
│
├── jobs/
│   ├── jobs.db                    # SQLite job database
│   ├── jobs_db.py                 # DB creation script
│   └── read_jobs.py               # DB reader utility
│
├── dummy_files_for_testing/        # Test CVs
│   ├── cv_john_doe.{pdf,txt}
│   └── cv_maria_santos.{pdf,txt}
│
└── test_debug_notebooks/           # Development notebooks
```

---

## 3. CORE COMPONENTS ANALYSIS

### 3.1 MAIN APPLICATION (main.py)
**Status**: ✅ **ACTIVE**

#### Purpose
Entry point for the Streamlit web application. Handles:
- CV file upload (PDF/TXT)
- Session state management
- Agent execution (async/sync)
- Chat interface with AI

#### Key Functions
| Function | Purpose | Status |
|----------|---------|--------|
| `load_css()` | Load external CSS styling | ✅ |
| `log_agent_event()` | Parse and log agent events | ✅ |
| `extract_agent_response()` | Extract text from agent responses | ✅ |
| `run_agent_async()` | Execute agent asynchronously | ✅ |
| `run_agent_sync()` | Synchronous wrapper for agent | ✅ |
| `analyze_cv_with_runner()` | Trigger CV analysis workflow | ✅ |
| `show_analysis_dialog()` | Modal dialog for CV analysis | ✅ |
| `main()` | Main UI application | ✅ |

#### Session State Management
```python
st.session_state.messages         # Chat history
st.session_state.runner           # ADK InMemoryRunner instance
st.session_state.current_cv_file  # Currently loaded CV filename
st.session_state.show_analysis    # Toggle analysis display
st.session_state.uploaded_file_content  # File buffer
```

#### Workflow
1. User uploads CV (PDF/TXT)
2. File saved to `temp_uploads/`
3. Click "Analyze CV" → Opens modal dialog
4. Orchestrator Agent analyzes CV automatically
5. User can ask follow-up questions in chat
6. Messages logged to `log_files/runner_events.log`

#### Key Issues & Notes
- Async execution wrapped in sync context for Streamlit compatibility
- Log events parsed from ADK response objects (handles None types safely)
- File upload key reset to clear uploader state
- CSS loaded from `src/styles/custom.css`

---

### 3.2 AGENT SYSTEM (src/agents/agents.py)
**Status**: ✅ **IMPLEMENTED** (Core), 🔨 **PLANNED** (Advanced)

#### Agent Hierarchy

##### 1. **CV_analysis_agent** ✅
- **Type**: `Agent` (using Gemini 2.5 Flash Lite)
- **Role**: Analyzes CVs in-depth
- **Tools Available**:
  - `read_cv` - Read PDF/TXT CV files
  - `list_available_cvs` - List test CV files
  - `compare_candidates` - Compare two CVs
- **Workflow**:
  1. Read CV using `read_cv` tool
  2. Extract: name, skills, experience, education
  3. Provide structured analysis with 8 sections
  4. Answer follow-up questions using stored CV data
- **Output Format**: Markdown with clear sections

##### 2. **job_listing_agent** ✅
- **Type**: `Agent` (using Gemini 2.5 Flash Lite)
- **Role**: Match candidates to job opportunities
- **Tools Available**:
  - `job_listing_tool` - Query jobs.db with skill matching
- **Workflow**:
  1. Receive CV summary with extracted skills
  2. Query local SQLite job database
  3. Score jobs by skill overlap
  4. Return top 5 jobs ranked by match
- **Output Format**: Numbered list with company, location, skills

##### 3. **code_assessment_agent** ✅ **READY**
- **Type**: `Agent` (using Gemini 2.5 Flash Lite)
- **Role**: Generate and evaluate coding challenges
- **Tools Available**:
  - `run_code_assignment` - Execute code in sandbox
- **Workflow**:
  1. Generate coding challenge tailored to role
  2. Candidate submits solution
  3. Execute code safely in sandbox
  4. Provide feedback (success/timeout/error/security)
- **Status**: Infrastructure ready, awaiting integration

##### 4. **orchestrator** ✅ **ACTIVE**
- **Type**: `LlmAgent` (central coordinator)
- **Role**: Guide candidate through entire journey
- **Tools Available** (via AgentTool):
  - CV_analysis_agent
  - job_listing_agent
  - code_assessment_agent
- **Workflow**:
  ```
  Step 1: Analyze CV
    ↓ (Extract skills automatically)
  Step 2: Match Jobs
    ↓ (User selects job #)
  Step 3: Code Assessment (if applicable)
    ↓ (Execute and evaluate)
  Step 4: Language Assessment (planned)
    ↓ (Test proficiency)
  Step 5: Schedule Interview (planned)
    ↓ (Book via calendar)
  ```
- **Instruction Set**: 250+ lines of detailed workflow specification

#### Retry Configuration
```python
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)
```
- Handles API rate limits and transient failures
- Exponential backoff strategy

---

### 3.3 TOOLS SYSTEM (src/tools/tools.py)
**Status**: ✅ **ACTIVE**

#### ADK FunctionTools

##### 1. **read_cv** (read_cv_fn)
```python
def read_cv_fn(filename: str) -> str
```
- **Purpose**: Read and extract CV content
- **Supported Formats**: `.txt`, `.pdf`
- **Search Paths**:
  1. `temp_uploads/` (user uploads)
  2. `dummy_files_for_testing/` (test files)
- **Returns**: Full CV text or error message
- **Handles**: PDF parsing via pdfplumber, encoding issues

##### 2. **list_available_cvs** (list_available_cvs_fn)
```python
def list_available_cvs_fn() -> str
```
- **Purpose**: List all test CV files
- **Returns**: Markdown list of available files
- **Use Case**: Testing and debugging

##### 3. **compare_candidates** (compare_candidates_fn)
```python
def compare_candidates_fn(filename1: str, filename2: str, criteria: str) -> str
```
- **Purpose**: Compare two CVs on specific criteria
- **Criteria Examples**: "Python experience", "Management skills"
- **Returns**: Side-by-side comparison text

##### 4. **job_listing_tool** (list_jobs_from_db)
```python
def list_jobs_from_db(cv_summary: str = None, max_results: int = 5) -> str
```
- **Purpose**: Match jobs from SQLite database
- **Algorithm**:
  1. Query all jobs from `jobs/jobs.db`
  2. Parse skills JSON for each job
  3. Calculate match score (skill overlap)
  4. Sort by score (descending)
  5. Return top N jobs as numbered list
- **Example Output**:
  ```
  1. Senior ML Engineer at TechCorp
     Location: Remote
     Required Skills: Python, PyTorch, Docker
  ```

#### Helper Functions (not exposed as tools)

##### 1. **read_cv_file**
- Helper to read CV from given path
- Used by test scripts and helpers

##### 2. **load_all_cvs**
- Load entire folder of CVs
- Returns dictionary of CV contents
- Used for batch processing

---

### 3.4 CODE SANDBOX (src/tools/code_sandbox.py)
**Status**: ✅ **READY**

#### Architecture
- **Isolation**: Python `multiprocessing` creates separate process
- **Security**: Restricted `__builtins__` whitelist
- **Resource Limits**: Memory (128MB), CPU time, timeout (3s)
- **Cross-Platform**: Unix support + Windows fallback

#### Security Features

##### Forbidden Keywords (Static Check)
```python
forbidden_keywords = ["import", "os", "sys", "subprocess", "open", "input", "eval", "exec"]
```
- Regex-based whole-word matching
- Prevents import attacks
- Fast-path rejection before execution

##### Safe Builtins Whitelist
```python
safe_builtins = {
    "print", "range", "len", "sum",
    "min", "max", "abs", "round",
    "int", "str", "list", "dict", 
    "tuple", "set", "float", "bool",
    "sorted", "enumerate", "zip"
}
```
- Only basic functions available
- No file I/O, networking, or system calls

##### Resource Limits (Unix only)
```python
resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))  # Memory limit
```
- 128MB memory cap per execution
- Prevents memory exhaustion attacks

##### Timeout Mechanism
```python
p.join(timeout)  # Default: 3 seconds
if p.is_alive():
    p.terminate()  # Kill if exceeds timeout
```

#### Function: execute_code()
```python
def execute_code(code_string: str, timeout: int = 3) -> dict
```

**Returns**:
```python
{
    "status": "success" | "timeout" | "memory_error" | "error" | "security_violation",
    "output": "...stdout captured...",
    "error_msg": "...traceback if error...",
    "execution_time": 2.1234  # seconds
}
```

**Status Flow**:
1. Security scan → blocks forbidden keywords
2. Create child process
3. Start process + timer
4. Wait up to timeout
5. Return results or kill process

#### Example
```python
result = execute_code("""
for i in range(5):
    print(i * 2)
""")
# Returns: {"status": "success", "output": "0\n2\n4\n6\n8\n", ...}
```

---

### 3.5 MCP CLIENT (src/tools/mcp_client.py)
**Status**: ✅ **READY** (Server-side integration pending)

#### CalendarClient Class
```python
class CalendarClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5000")
    
    def get_busy_slots(self, time_min: str, time_max: str) -> List[Dict]
    def book_slot(self, start_time: str, end_time: str, 
                  candidate_email: str, summary: str) -> Optional[Dict]
```

#### Features
- **ISO 8601 datetime validation**: Ensures proper format
- **Timeout handling**: 10s timeout per request
- **Error reporting**: Graceful failures with error messages

#### Methods

##### get_busy_slots()
- **Endpoint**: `GET /slots`
- **Parameters**: `timeMin`, `timeMax` (ISO 8601)
- **Returns**: List of busy time slots
- **Use**: Find available slots for interview

##### book_slot()
- **Endpoint**: `POST /book`
- **Payload**:
  ```json
  {
    "start": "2025-02-01T10:00:00+01:00",
    "end": "2025-02-01T11:00:00+01:00",
    "summary": "Smart-Hire AI Technical Interview",
    "attendee_email": "candidate@example.com"
  }
  ```
- **Returns**: Event ID, HTML link, summary
- **Use**: Create interview appointment

---

### 3.6 MCP SERVER (mcp_server/calendar_server.py)
**Status**: ✅ **READY** (Orchestrator integration pending)

#### Flask REST API

##### Authentication
```python
credentials = Credentials(
    token=None,
    refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    token_uri='https://oauth2.googleapis.com/token',
    scopes=['https://www.googleapis.com/auth/calendar']
)
```
- Uses OAuth2 with refresh token
- Credentials auto-refreshed on each request

##### Endpoints

###### 1. GET / (Health Check)
```bash
curl http://127.0.0.1:5000/
```
**Response**:
```json
{
  "status": "Server running",
  "calendar_connection": "OK",
  "endpoints": ["/slots", "/book"]
}
```

###### 2. GET /slots (Get Busy Slots)
```bash
curl "http://127.0.0.1:5000/slots?timeMin=2025-02-01T00:00:00Z&timeMax=2025-02-02T00:00:00Z"
```
**Response**:
```json
{
  "calendar_id": "your@email.com",
  "busy_slots": [
    {"start": "2025-02-01T10:00:00Z", "end": "2025-02-01T11:00:00Z"}
  ]
}
```

###### 3. POST /book (Create Interview)
```bash
curl -X POST http://127.0.0.1:5000/book \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2025-02-01T14:00:00+01:00",
    "end": "2025-02-01T15:00:00+01:00",
    "attendee_email": "candidate@example.com"
  }'
```
**Response**:
```json
{
  "status": "success",
  "event_id": "abc123def456",
  "htmlLink": "https://calendar.google.com/calendar/...",
  "summary": "Smart-Hire AI Technical Interview"
}
```

#### Conflict Detection
- Queries calendar for busy slots in requested timeframe
- Rejects overlapping bookings (HTTP 409)
- Includes candidate as attendee

---

## 4. DATA FLOW ARCHITECTURE

### CV Upload & Analysis Flow
```
┌─────────────────────────────────────────────────┐
│ User uploads CV (PDF/TXT) via Streamlit UI      │
└────────────────┬────────────────────────────────┘
                 ↓
         ┌───────────────────┐
         │ temp_uploads/     │
         │ [cv_file.pdf]     │
         └────────┬──────────┘
                  ↓
         ┌─────────────────────────────┐
         │ InMemoryRunner initialized  │
         │ agent = orchestrator        │
         └────────┬────────────────────┘
                  ↓
    ┌─────────────────────────────────┐
    │ Orchestrator receives prompt:    │
    │ "Analyze cv_john_doe.pdf"       │
    └────────┬──────────────────────────┘
             ↓
    ┌──────────────────────┐
    │ DELEGATES TO:        │
    │ CV_analysis_agent    │
    └────────┬─────────────┘
             ↓
    ┌───────────────────────────────────┐
    │ CV_analysis_agent:                 │
    │ 1. Call read_cv("cv_john_doe.pdf")│
    │ 2. Parse content                  │
    │ 3. Extract skills, experience     │
    │ 4. Return structured analysis     │
    └────────┬──────────────────────────┘
             ↓
    ┌────────────────────────────────────┐
    │ Analysis shown in Streamlit chat   │
    │ Messages stored in session_state   │
    │ Logged to runner_events.log        │
    └────────────────────────────────────┘
```

### Job Matching Flow
```
User says: "Show me jobs I'm qualified for"
        ↓
Orchestrator parses request
        ↓
Extracts skills from previous CV analysis
        ↓
DELEGATES TO: job_listing_agent
        ↓
job_listing_agent calls job_listing_tool
        ↓
list_jobs_from_db() executes:
  1. Query jobs.db
  2. Score each job by skill overlap
  3. Sort by score (highest first)
  4. Return top 5 as numbered list
        ↓
User selects: "I want job #2"
        ↓
Orchestrator extracts job details
        ↓
(Next: Code Assessment or Language Test)
```

### Code Assessment Flow
```
User selects a technical role
        ↓
Orchestrator DELEGATES TO: code_assessment_agent
        ↓
code_assessment_agent:
  1. Reads job requirements
  2. Reads CV (from earlier analysis)
  3. Generates difficulty-matched coding challenge
        ↓
Agent presents challenge to user
        ↓
User submits code solution in chat
        ↓
code_assessment_agent calls run_code_assignment()
        ↓
execute_code() in sandbox:
  1. Security scan (forbidden keywords)
  2. Create child process
  3. Restrict builtins, memory, timeout
  4. Execute code
  5. Capture stdout
  6. Return status + output
        ↓
code_assessment_agent provides feedback:
  - ✅ Success with output
  - ⏱ Timeout error
  - 💾 Memory limit exceeded
  - ⚠️ Security violation
  - ❌ Syntax/runtime error
        ↓
Feedback shown to user
```

### Calendar Integration Flow (Planned)
```
User wants to schedule interview
        ↓
Orchestrator (planned): DELEGATES TO scheduler_agent
        ↓
scheduler_agent:
  1. Get user's available time (from UI)
  2. Recruiter's email (from job details)
        ↓
scheduler_agent calls CalendarClient
        ↓
CalendarClient.get_busy_slots()
  - Queries MCP Server at /slots
  - MCP Server queries Google Calendar API
  - Returns busy periods
        ↓
Find free slot
        ↓
CalendarClient.book_slot()
  - Sends booking request to /book
  - MCP Server validates and creates event
  - Returns calendar link
        ↓
User receives confirmation
  - Event created
  - Calendar invites sent
  - Meeting details displayed
```

---

## 5. DATABASE SCHEMA

### jobs.db (SQLite)
```sql
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,              -- e.g., "Senior ML Engineer"
    company TEXT,                     -- e.g., "TechCorp"
    location TEXT,                    -- e.g., "Remote"
    description TEXT,                 -- Job overview
    responsibilities TEXT,            -- Bullet points
    skills_required TEXT              -- JSON array: ["Python", "PyTorch", ...]
)
```

**Sample Data**:
```
ID | Title | Company | Location | Skills
1  | ML Engineer – Computer Vision | TechCorp | Remote | ["Python", "PyTorch", "TensorFlow", "Docker"]
```

**Usage**:
- Populated via `jobs/jobs_db.py`
- Queried by `list_jobs_from_db()` for skill matching
- Can be expanded with more job listings

---

## 6. CONFIGURATION & ENVIRONMENT

### .env Variables (Required)
```bash
# Core API
GOOGLE_API_KEY=your_api_key_here                    # For Gemini & ADK
GOOGLE_GENAI_USE_VERTEXAI=FALSE                     # Use standard Google AI

# Calendar Integration (Optional, for MCP Server)
GOOGLE_REFRESH_TOKEN=your_refresh_token             # OAuth2 refresh token
GOOGLE_CLIENT_ID=your_client_id                     # OAuth2 client ID
GOOGLE_CLIENT_SECRET=your_client_secret             # OAuth2 client secret
CALENDAR_ID=your@email.com                          # Gmail address
```

### File Upload Locations
```
/temp_uploads/        → User-uploaded CVs (auto-cleaned)
/dummy_files_for_testing/  → Test CVs (persistent)
/log_files/           → runner_events.log
/jobs/                → jobs.db
```

---

## 7. KEY IMPLEMENTATION DETAILS

### Session State Lifecycle
```python
# Initial state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# CV upload triggers
if uploaded_file:
    st.session_state.current_cv_file = filename
    st.session_state.runner = InMemoryRunner(orchestrator, "agents")

# Chat update
st.session_state.messages.append({"role": "user", "content": prompt})
st.session_state.messages.append({"role": "assistant", "content": response})

# Reset functionality
st.session_state.messages = []
st.session_state.current_cv_file = None
# Also deletes files from temp_uploads/
```

### Async/Sync Pattern
```python
async def run_agent_async(runner, prompt):
    response = await runner.run_debug(prompt)
    return extract_agent_response(response)

def run_agent_sync(runner, prompt):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(run_agent_async(runner, prompt))
    loop.close()
    return result
```
- ADK's `run_debug()` is async
- Streamlit requires sync context
- Wrapped with event loop management

### Event Logging
```python
def log_agent_event(event):
    log_entry = {
        "timestamp": datetime.now().timestamp(),
        "agent_name": getattr(event, "agent_name", "Orchestrator"),
        "tool_name": None,
        "input_text": None,
        "output_text": None,
        "type": "unknown"
    }
    # Parse event.content.parts for Tool/Text/FunctionCall
    # Write to log_files/runner_events.log as JSON
```
- Captures: text responses, tool calls, tool results
- JSON format for analysis
- Safely handles None types

---

## 8. SECURITY ANALYSIS

### Code Execution Safety
✅ **Multi-layer protection**:
1. **Keyword blacklist**: Blocks `import`, `open`, `os`, etc.
2. **Restricted builtins**: Only safe functions allowed
3. **Process isolation**: Separate process, can kill
4. **Resource limits**: 128MB memory, 3s timeout
5. **Output capture**: Can't escape via stdout

### API Security
✅ **Google ADK**:
- Automatic client initialization from env vars
- No hardcoded credentials
- Retry with exponential backoff

✅ **MCP Server**:
- OAuth2 with refresh tokens
- No plaintext password storage
- Conflict detection prevents double-booking

### File Upload Security
✅ **CV Upload**:
- Stored in isolated `temp_uploads/` directory
- Only `.pdf` and `.txt` allowed
- File size: up to 200MB
- Auto-cleanup recommended
- pdfplumber handles malformed PDFs

### Session Security
✅ **Streamlit**:
- Session state isolated per user (browser session)
- No persistent file storage across sessions
- HTTPS recommended in production

---

## 9. IMPLEMENTATION STATUS

### ✅ COMPLETE (Phase 1)
- [x] Streamlit UI with file upload
- [x] Google ADK integration
- [x] Orchestrator Agent
- [x] CV Analysis Agent
- [x] Job Listing Agent
- [x] CV Tools (read, list, compare)
- [x] Code Sandbox infrastructure
- [x] MCP Server infrastructure
- [x] MCP Client (CalendarClient)
- [x] Custom CSS styling
- [x] Chat interface
- [x] Session state management
- [x] Event logging

### 🔨 IN PROGRESS (Phase 2)
- [ ] Scheduler Agent (integrate MCP)
- [ ] Language Assessment Agent
- [ ] Tech Assessor Agent (generate challenges)
- [ ] Assessment feedback system
- [ ] Skill gap analysis
- [ ] Interview prep tips
- [ ] Mock interviews
- [ ] Progress tracking

### 📋 PLANNED (Phase 3)
- [ ] Multiple CV versions
- [ ] Application tracking
- [ ] Company culture analysis
- [ ] Salary negotiation prep
- [ ] Post-interview follow-up
- [ ] Skill learning paths
- [ ] Network mapping
- [ ] Success analytics
- [ ] Mobile app

---

## 10. ERROR HANDLING & EDGE CASES

### CV Upload Errors
| Error | Handling |
|-------|----------|
| File not found | Returns error message to agent |
| PDF parse error | Falls back gracefully with available text |
| Empty file | Returns "Not provided" |
| Unsupported format | Rejects with error message |

### Agent Errors
| Error | Handling |
|-------|----------|
| API timeout | Retry logic (5 attempts, exp. backoff) |
| No response | Returns warning message to user |
| Tool execution fails | Gracefully reports error to user |
| Rate limiting | Automatic retry with delay |

### Code Sandbox Errors
| Status | Response |
|--------|----------|
| Success | Stdout captured |
| Timeout | 3s limit exceeded message |
| Memory | 128MB limit exceeded message |
| Security | Forbidden keyword detected |
| Runtime | Exception traceback + partial output |

### Calendar Integration Errors
| Error | Response |
|-------|----------|
| Server unreachable | CalendarClient returns None |
| Auth failure | "Calendar service not initialized" |
| Slot conflict | Returns 409 Conflict error |
| Invalid datetime | Returns 400 Bad Request |

---

## 11. PERFORMANCE CONSIDERATIONS

### API Quotas
- **Gemini 2.5 Flash Lite**: Generous free tier quotas
- Retry strategy handles rate limits (429 errors)
- Exponential backoff: 1s → 7s → 49s

### File Processing
- **PDF parsing**: pdfplumber extracts text from all pages
- **Large files**: 200MB limit, may be slow
- **CV analysis**: ~5-10 seconds per analysis

### Database Performance
- **jobs.db**: Linear scan for skill matching
- Should index on skills_required for scale
- Current: 1 job entry (sample data)

### Memory Usage
- **Code sandbox**: 128MB per execution
- **Streamlit session**: Stores chat history + runner
- **Log file**: Grows indefinitely (consider rotation)

### Concurrency
- **Streamlit**: Single-threaded per user session
- **MCP Server**: Single Flask instance, can add workers
- **Code sandbox**: Multiprocessing per execution

---

## 12. CODE QUALITY ASSESSMENT

### Strengths
✅ Clear separation of concerns (agents, tools, UI)  
✅ Type hints used throughout  
✅ Comprehensive error handling  
✅ Detailed docstrings and comments  
✅ Modular tool design  
✅ Good use of ADK patterns  
✅ Session state properly managed  
✅ Secure code execution environment  

### Areas for Improvement
⚠️ **Logging**: Basic JSON logging, consider structured logging library  
⚠️ **Testing**: No automated tests visible (test notebooks are manual)  
⚠️ **Database**: jobs.db has minimal data, needs population  
⚠️ **Error messages**: Some could be more user-friendly  
⚠️ **Documentation**: Some functions lack docstrings  
⚠️ **MCP integration**: Not yet integrated into orchestrator  
⚠️ **Caching**: Could cache CV analysis to speed up job matching  
⚠️ **Memory**: Log file grows unbounded  

### Code Standards Met
✅ PEP 8 naming conventions  
✅ Logical module organization  
✅ DRY principle applied  
✅ Single responsibility per function  
✅ Clear variable names  

---

## 13. RUNNING THE APPLICATION

### Prerequisites
```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Configuration
```bash
cp env.example .env
# Edit .env with GOOGLE_API_KEY
```

### Start Application
```bash
# Terminal 1: Streamlit app
streamlit run main.py

# Terminal 2 (optional): MCP Calendar Server
cd mcp_server
python calendar_server.py
```

### Usage
1. Open http://localhost:8501
2. Upload CV (PDF or TXT)
3. Click "Analyze CV"
4. Ask questions in chat
5. View job matches
6. (Future) Take assessments

---

## 14. TESTING & DEBUGGING

### Manual Testing
- **Test CVs**: `dummy_files_for_testing/cv_john_doe.{pdf,txt}`
- **Notebooks**: `test_debug_notebooks/`
  - main.ipynb
  - test_debug_agents.ipynb
  - test_debug_tools.ipynb

### Debugging Tools
```python
# Check logs
tail -f log_files/runner_events.log

# Test agent directly
from src.agents import orchestrator
from google.adk.runners import InMemoryRunner
runner = InMemoryRunner(orchestrator, "agents")
response = await runner.run_debug("Test prompt")

# Test sandbox
from src.tools.code_sandbox import execute_code
result = execute_code("print('hello')")
```

### Common Issues
| Issue | Solution |
|-------|----------|
| "GOOGLE_API_KEY not found" | Set in .env file |
| "PDF reading requires pdfplumber" | pip install pdfplumber |
| "MCP Server connection failed" | Start calendar_server.py in another terminal |
| "Agent not responding" | Check API quota, verify key validity |

---

## 15. SUMMARY & KEY TAKEAWAYS

### What This Project Does Well
1. **Clean multi-agent architecture** using Google ADK
2. **Secure code execution** with proper resource limits
3. **Practical MCP integration** for calendar scheduling
4. **Professional Streamlit UI** with custom CSS
5. **Comprehensive CV analysis** with structured output
6. **Skill-based job matching** with scoring algorithm
7. **Modular tool design** for easy extension

### Key Design Patterns
- **Hub-and-Spoke**: Orchestrator coordinates agents
- **Tool Pattern**: FunctionTool wraps Python functions
- **Async/Sync Bridge**: Handles Streamlit compatibility
- **Process Isolation**: Multiprocessing for security
- **Resource Management**: Memory/timeout limits
- **Session State**: Streamlit chat continuity

### Next Steps for Development
1. Implement Scheduler Agent (integrate MCP)
2. Build Language Assessment Agent
3. Create Tech Assessor with challenge generation
4. Expand jobs.db with real job data
5. Add automated testing suite
6. Implement structured logging
7. Add user database (track applications)
8. Build progress dashboard
9. Mobile app (React Native)

---

**Analysis Generated**: 2025-11-28  
**Codebase Status**: Stable, Production-Ready for Phase 1  
**Recommendation**: Ready to expand Phase 2 features
