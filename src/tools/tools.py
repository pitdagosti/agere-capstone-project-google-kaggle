# Custom tools for agents.
from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
from typing import Dict, Union, Optional, Any
from google.genai import types
from google.adk.tools import FunctionTool
import sqlite3
import json
from .code_sandbox import execute_code
from datetime import datetime, timedelta, timezone
from dateutil import parser
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os
import pytz


# Try to import Context. If not available, a mock ToolContext is used for compatibility.
try:
    from google.adk.tools import ToolContext
    CONTEXT_AVAILABLE = True
except ImportError:
    CONTEXT_AVAILABLE = False
    # Create a mock ToolContext for backwards compatibility
    class ToolContext:
        def __init__(self):
            self._data = {}
        def set(self, key, value):
            self._data[key] = value
        def get(self, key, default=None):
            return self._data.get(key, default)


# =============================================================================
# Custom ADK Functions
# =============================================================================

# --- Calendar Tools ---

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")  # Set your Gmail calendar ID here.

def get_calendar_service():
    """
    Returns an authenticated Google Calendar service using OAuth credentials from .env.
    """
    # Check if credentials are configured
    try:
        refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if not all([refresh_token, client_id, client_secret]):
            raise ValueError(
                "Google Calendar credentials not configured. "
                "Please set GOOGLE_REFRESH_TOKEN, GOOGLE_CLIENT_ID, and GOOGLE_CLIENT_SECRET in .env file."
            )
        
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        service = build('calendar', 'v3', credentials=creds)
        return service
    
    except Exception as e:
        print("RAW ERROR:", repr(e))


def calendar_get_busy_fn(start: str, end: str) -> str:
    """
    Query busy slots directly from Google Calendar.
    
    Args:
        start: ISO format datetime string with timezone (e.g., 2025-11-30T10:00:00+01:00)
        end: ISO format datetime string with timezone

    Returns:
        JSON string with busy slots or detailed error.
    """
    try:
        CALENDAR_ID = os.getenv("CALENDAR_ID")
        if not CALENDAR_ID:
            raise ValueError(
                "CALENDAR_ID not configured. Please set CALENDAR_ID in your .env file."
            )
        
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        busy_slots = [
            {
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "summary": event.get('summary', '')
            }
            for event in events_result.get('items', [])
        ]

        return json.dumps({
            "status": "success",
            "start": start,
            "end": end,
            "busy_slots": busy_slots
        }, indent=2)

    except ValueError as ve:
        return json.dumps({
            "status": "error",
            "type": "CALENDAR_NOT_CONFIGURED",
            "message": str(ve)
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "type": "CALENDAR_API_ERROR",
            "error_type": type(e).__name__,
            "message": str(e)
        }, indent=2)

def calendar_book_slot_fn(start: str, end: str, summary: str = "Interview", attendee_email: str = None) -> str:
    """
    Books an event directly on Google Calendar, only for today or future dates.

    Args:
        start: ISO format start datetime string with timezone
        end: ISO format end datetime string with timezone
        summary: Event title
        attendee_email: Optional email of the attendee

    Returns:
        JSON string with booking result or detailed error.
    """
    try:
        # Ensure CALENDAR_ID is configured
        CALENDAR_ID = os.getenv("CALENDAR_ID")
        if not CALENDAR_ID:
            raise ValueError("CALENDAR_ID not configured. Please set CALENDAR_ID in your .env file.")

        # Convert start/end to datetime objects in Rome timezone
        rome_tz = pytz.timezone("Europe/Rome")
        start_dt = datetime.fromisoformat(start).astimezone(rome_tz)
        end_dt = datetime.fromisoformat(end).astimezone(rome_tz)
        now_dt = datetime.now(rome_tz)

        if start_dt < now_dt:
            raise ValueError(f"Cannot book in the past. Next available start datetime is after {now_dt.isoformat()}")

        service = get_calendar_service()

        event = {
            "summary": summary,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Europe/Rome"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Europe/Rome"},
        }

        if attendee_email:
            event["attendees"] = [{"email": attendee_email}]

        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

        return json.dumps({
            "status": "success",
            "event_id": created_event.get("id"),
            "summary": created_event.get("summary"),
            "start": created_event['start'].get('dateTime'),
            "end": created_event['end'].get('dateTime')
        }, indent=2)

    except ValueError as ve:
        return json.dumps({
            "status": "error",
            "type": "CALENDAR_NOT_CONFIGURED" if "CALENDAR_ID" in str(ve) else "INVALID_DATE",
            "message": str(ve)
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "type": "CALENDAR_BOOKING_ERROR",
            "error_type": type(e).__name__,
            "message": str(e)
        }, indent=2)



def run_code_assignment(code: str, expected_output: str = None, context: Optional[object] = None) -> str:
    """
    Executes the candidate's code submission in a secure sandbox environment.
    Used by the code_assessment_agent to evaluate solutions. Returns a structured
    string indicating success or failure. Supports Context for reliable output comparison.

    Args:
        code: The Python code string submitted by the candidate.
        expected_output: (Optional) If provided, stores this as the expected output in context.
                        If not provided, retrieves expected output from context and compares.
        context: (Optional) ToolContext for storing/retrieving expected outputs.

    Returns:
        A string with the execution result, prefixed with '✅' for success
        or '❌' for errors, timeouts, or security violations.
        If context is available and expected_output was stored:
        - Compares actual output with expected output
        - Returns detailed pass/fail message
    """
    
    # Execute code in sandbox.
    result = execute_code(code)
    
    # MODE 1: Store expected output (for problem generation).
    if expected_output is not None:
        if context:
            context.set("last_expected_output", expected_output)
            context.set("problem_generated", True)
        # Return normal execution result
        if result["status"] == "success":
            feedback = f"✅ Expected output stored successfully!"
        elif result["status"] == "timeout":
            feedback = f"❌ Timeout Error: {result.get('error_msg', 'Execution timed out.')}"
        elif result["status"] == "security_violation":
             feedback = f"❌ Security Error: {result.get('error_msg', 'A security violation was detected.')}"
        else:
            feedback = f"❌ Execution Error:\n{result.get('error_msg', 'An unknown error occurred.')}"
        return feedback
    
    # MODE 2: Compare with stored expected output (for evaluation).
    if context and context.get("problem_generated"):
        expected = context.get("last_expected_output", "")
        
        # First check if execution succeeded
        if result["status"] != "success":
            if result["status"] == "timeout":
                return f"❌ FAIL: Timeout Error - {result.get('error_msg', 'Execution timed out.')}"
            elif result["status"] == "security_violation":
                return f"❌ FAIL: Security Error - {result.get('error_msg', 'A security violation was detected.')}"
            else:
                return f"❌ FAIL: Execution Error - {result.get('error_msg', 'An unknown error occurred.')}"
        
        # Execution succeeded - compare outputs
        actual = result['output'].strip()
        expected = expected.strip()
        
        if actual == expected:
            return f"✅ PASS: Code executed successfully and output matches expected!\nOutput:\n{actual}"
        else:
            return f"❌ FAIL: Output mismatch\nExpected:\n{expected}\n\nActual:\n{actual}"
    
    # MODE 3: Backwards compatible - no context or expected output.
    # This is the old behavior for existing code.
    if result["status"] == "success":
        feedback = f"✅ Code executed successfully!\nOutput:\n{result['output']}"
    elif result["status"] == "timeout":
        feedback = f"❌ Timeout Error: {result.get('error_msg', 'Execution timed out.')}"
    elif result["status"] == "security_violation":
         feedback = f"❌ Security Error: {result.get('error_msg', 'A security violation was detected.')}"
    else:
        feedback = f"❌ Execution Error:\n{result.get('error_msg', 'An unknown error occurred.')}"
    
    return feedback


def present_coding_problem_fn(job_title: str = "default", context: Optional[object] = None) -> str:
    """
    Presents a coding problem from templates based on job category.
    Automatically stores expected output for later evaluation.
    
    Args:
        job_title: The job title to determine the appropriate problem.
        context: ToolContext for storing expected output.
        
    Returns:
        Formatted problem statement with test cases and instructions.
    """
    # Import here to avoid circular dependency.
    from ..agents.agents import get_coding_problem
    
    # Get the appropriate problem.
    problem = get_coding_problem(job_title)
    
    # Store the expected output in context for later comparison.
    if context:
        context.set("last_expected_output", problem['expected_output'])
        context.set("problem_generated", True)
    
    # Format the problem for display.
    formatted_problem = f"""**Coding Assessment: {problem['title']}**

**Problem Description:**
{problem['description']}

**Test Cases:**
```python
{problem['test_code']}
```

**Instructions:**
- Write your solution function
- Include the test cases at the end of your code
- DO NOT use import statements
- Only use built-in functions: print, range, len, sum, min, max, abs, round, int, str, list, dict, tuple, set, float, bool, sorted, enumerate, zip, reversed

**Please submit your complete code (function + test cases).**"""

    return formatted_problem


def read_cv_fn(filename: str) -> str:
    """
    Reads a CV file that has been uploaded for analysis.
    
    Args:
        filename: Name of the CV file to read and analyze (supports .txt and .pdf formats).
    
    Returns:
        A readable text output of the CV content.
    """
    base_path = Path(__file__).parent.parent.parent
    temp_uploads_path = base_path / "temp_uploads" / filename
    dummy_files_path = base_path / "dummy_files_for_testing" / filename
    
    if temp_uploads_path.exists():
        file_path = temp_uploads_path
    elif dummy_files_path.exists():
        file_path = dummy_files_path
    else:
        return f"❌ Error: Could not find the CV file '{filename}'. Please ensure the file was uploaded successfully."
    
    try:
        if file_path.suffix == '.txt':
            content = file_path.read_text(encoding='utf-8')
            if not content.strip():
                content = "Not provided"
            return f"✅ Successfully read {filename}:\n\n{content}"
        
        elif file_path.suffix == '.pdf':
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                if not text.strip():
                    text = "Not provided"
                return f"✅ Successfully read {filename}:\n\n{text}"
            except ImportError:
                return "⚠️ PDF reading requires pdfplumber. Install with: pip install pdfplumber"
        else:
            return f"❌ Unsupported file type: {file_path.suffix}. Supported types: .txt, .pdf"
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"

def list_available_cvs_fn() -> str:
    """
    Lists all available CV files in the dummy_files_for_testing folder.
    """
    base_path = Path(__file__).parent.parent.parent / "dummy_files_for_testing"
    
    if not base_path.exists():
        return "❌ dummy_files_for_testing folder not found"
    
    txt_files = list(base_path.glob("*.txt"))
    pdf_files = list(base_path.glob("*.pdf"))
    
    result = "📁 Available CV files:\n\n"
    
    if txt_files:
        result += "Text files (.txt):\n"
        for f in txt_files:
            result += f"  - {f.name}\n"
    
    if pdf_files:
        result += "\nPDF files (.pdf):\n"
        for f in pdf_files:
            result += f"  - {f.name}\n"
    
    if not txt_files and not pdf_files:
        result += "No CV files found"
    
    return result

def compare_candidates_fn(
    filename1: str,
    filename2: str,
    criteria: str
) -> str:
    """
    Compares two candidate CVs based on specific criteria.
    
    Args:
        filename1: First CV filename.
        filename2: Second CV filename.
        criteria: Comparison criteria (e.g., 'Python experience').
    
    Returns:
        A comparison of both candidates based on the specified criteria.
    """
    cv1 = read_cv_fn(filename1)
    cv2 = read_cv_fn(filename2)
    
    return f"""
Comparing two candidates on: {criteria}

=== CANDIDATE 1: {filename1} ===
{cv1}

=== CANDIDATE 2: {filename2} ===
{cv2}

Please compare these candidates specifically on: {criteria}
"""

def list_jobs_from_db(cv_summary: str = None, max_results: int = 5) -> str:
    """
    Lists jobs from SQLite DB, ranked by skills match. Returns a numbered list for selection.
    """
    try:
        conn = sqlite3.connect("jobs/jobs.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, company, location, description, responsibilities, skills_required FROM jobs")
        jobs = cursor.fetchall()
    except Exception as e:
        return f"❌ Could not read jobs.db: {e}"
    finally:
        conn.close()

    matched_jobs = []

    for job in jobs:
        job_id, title, company, location, description, responsibilities, skills_json = job
        try:
            skills = json.loads(skills_json)
        except Exception:
            skills = []

        score = 0
        if cv_summary:
            cv_skills = [s.strip().lower() for s in cv_summary.split(",")]
            score = len(set(cv_skills) & set([s.lower() for s in skills]))
        else:
            score = 1

        if score > 0:
            matched_jobs.append((score, {
                "id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "responsibilities": responsibilities,
                "skills": skills
            }))

    matched_jobs.sort(key=lambda x: x[0], reverse=True)
    if not matched_jobs:
        return "❌ No matching jobs found."

    response = ""
    for i, (_, job) in enumerate(matched_jobs[:max_results], start=1):
        response += (
            f"{i}. {job['title']} at {job['company']}\n"
            f"   Location: {job['location']}\n"
            f"   Description: {job['description']}\n"
            f"   Responsibilities: {job['responsibilities']}\n"
            f"   Required Skills: {', '.join(job['skills']) or 'Not provided'}\n\n"
        )
    
    response += "Please choose the job you are interested in by typing its number (1, 2, 3, ...)."
    return response


# =============================================================================
# Helper Functions
# =============================================================================

def read_cv_file(file_path: Union[str, Path]) -> str:
    """
    Helper function to read a CV file (not an ADK tool).
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.suffix == '.txt':
        return file_path.read_text(encoding='utf-8')
    
    elif file_path.suffix == '.pdf':
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text or "Not provided"
        except ImportError:
            return "⚠️ PDF reading requires pdfplumber. Install with: pip install pdfplumber"
    
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")


def load_all_cvs(folder_path: Union[str, Path] = "dummy_files_for_testing") -> Dict[str, str]:
    """
    Helper function to load all CVs from a folder.
    """
    folder = Path(folder_path)
    cvs = {}
    
    for cv_file in folder.glob("*.txt"):
        cvs[cv_file.stem] = read_cv_file(cv_file)
    
    for cv_file in folder.glob("*.pdf"):
        try:
            cvs[cv_file.stem] = read_cv_file(cv_file)
        except Exception as e:
            cvs[cv_file.stem] = f"Error reading {cv_file.name}: {str(e)}"
    
    return cvs


# =============================================================================
# ADK FunctionTool Definitions
# =============================================================================

read_cv = FunctionTool(func=read_cv_fn)
list_available_cvs = FunctionTool(func=list_available_cvs_fn)
compare_candidates = FunctionTool(func=compare_candidates_fn)
job_listing_tool = FunctionTool(func=list_jobs_from_db)
code_execution_tool = FunctionTool(func=run_code_assignment)
problem_presenter_tool = FunctionTool(func=present_coding_problem_fn)
calendar_get_busy = FunctionTool(func=calendar_get_busy_fn)
calendar_book_slot = FunctionTool(func=calendar_book_slot_fn)