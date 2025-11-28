# CUSTOM TOOLS FOR AGENTS 🔧

from pathlib import Path
from typing import Dict, Union
from google.genai import types
from google.adk.tools import FunctionTool
import sqlite3
import json
from .code_sandbox import execute_code
from datetime import datetime, timedelta
from dateutil import parser
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()
import os


# =============================================================================
# CUSTOM ADK FUNCTIONS
# =============================================================================

# --- CALENDAR TOOLS ---

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")  # puoi mettere il tuo calendario Gmail qui

def get_calendar_service():
    """
    Restituisce un servizio Google Calendar autenticato usando le credenziali OAuth dal .env.
    """
    creds = Credentials(
        None,
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token",
    )
    service = build('calendar', 'v3', credentials=creds)
    return service


def calendar_get_busy_fn(start: str, end: str) -> str:
    """
    Query busy slots direttamente da Google Calendar.

    Args:
        start: ISO format datetime string
        end: ISO format datetime string

    Returns:
        Busy slots in JSON format as string
    """
    try:
        service = get_calendar_service()
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        busy_slots = []
        for event in events_result.get('items', []):
            busy_slots.append({
                "start": event['start'].get('dateTime', event['start'].get('date')),
                "end": event['end'].get('dateTime', event['end'].get('date')),
                "summary": event.get('summary', '')
            })

        return f"Busy slots between {start} and {end}:\n{busy_slots}"

    except Exception as e:
        return f"Exception while fetching busy slots: {str(e)}"


def calendar_book_slot_fn(start: str, end: str, summary: str = "Interview", attendee_email: str = None) -> str:
    """
    Prenota un evento direttamente su Google Calendar.

    Args:
        start: ISO format start datetime string
        end: ISO format end datetime string
        summary: Event summary/title
        attendee_email: Optional candidate email

    Returns:
        Result of booking (success/failure)
    """
    try:
        service = get_calendar_service()
        event = {
            "summary": summary,
            "start": {"dateTime": start, "timeZone": "Europe/Rome"},
            "end": {"dateTime": end, "timeZone": "Europe/Rome"},
        }
        if attendee_email:
            event["attendees"] = [{"email": attendee_email}]

        created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return f"✅ Booking successful: Event ID {created_event['id']}, starts at {created_event['start']['dateTime']}"

    except Exception as e:
        return f"Exception while booking slot: {str(e)}"




def run_code_assignment(code: str) -> str:
    """
    Executes the candidate's code submission in a secure sandbox environment.
    This tool is used by the code_assessment_agent to evaluate solutions.
    It returns a structured string indicating success or failure.

    Args:
        code: The Python code string submitted by the candidate.

    Returns:
        A string with the execution result, prefixed with '✅' for success
        or '❌' for errors, timeouts, or security violations.
    """

    # Call the actual sandbox execution function you created
    result = execute_code(code)

    # Format the dictionary output into a clean string for the agent
    if result["status"] == "success":
        feedback = f"✅ Code executed successfully!\nOutput:\n{result['output']}"
    elif result["status"] == "timeout":
        feedback = f"❌ Timeout Error: {result.get('error_msg', 'Execution timed out.')}"
    elif result["status"] == "security_violation":
         feedback = f"❌ Security Error: {result.get('error_msg', 'A security violation was detected.')}"
    else: # Covers 'error', 'memory_error', etc.
        feedback = f"❌ Execution Error:\n{result.get('error_msg', 'An unknown error occurred.')}"

    return feedback


def read_cv_fn(filename: str) -> str:
    """
    Read a CV file that has been uploaded for analysis.
    
    Args:
        filename: Name of the CV file to read and analyze (supports .txt and .pdf formats)
    
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
    List all available CV files in dummy_files_for_testing folder.
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
    Compare two candidate CVs based on specific criteria.
    
    Args:
        filename1: First CV filename
        filename2: Second CV filename
        criteria: Comparison criteria (e.g., 'Python experience')
    
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
    List jobs from SQLite DB, ranked by skills match. Returns numbered list for selection.
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
# HELPER FUNCTIONS
# =============================================================================

def read_cv_file(file_path: Union[str, Path]) -> str:
    """
    Helper function to read CV file (not an ADK tool)
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
    Helper function to load all CVs from a folder
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
calendar_get_busy = FunctionTool(func=calendar_get_busy_fn)
calendar_book_slot = FunctionTool(func=calendar_book_slot_fn)