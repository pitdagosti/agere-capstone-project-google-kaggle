# AGENTS FILE 🧑‍🏭

# Packages Import
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import google_search, AgentTool, FunctionTool
from google.genai import types
from google.adk.models.google_llm import Gemini
from src.tools.code_sandbox import execute_code
from google.adk.runners import InMemoryRunner
from pathlib import Path



# Import custom tools
from src.tools import read_cv, list_available_cvs, compare_candidates, job_listing_tool # MODIFICATO: Usiamo l'oggetto FunctionTool 'job_listing_tool'

# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

print("✅ ADK components imported successfully.")
print("✅ ADK will auto-initialize client from environment variables")

# RETRY OPTIONS:
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

# Agents Definition
# ADK will automatically read GOOGLE_API_KEY and GOOGLE_GENAI_USE_VERTEXAI
# from environment variables - no need to create Client explicitly!

# TODO: AGENT TO SCREEN THE RESUME AND CHECK IF IT MATCHES THE JOB DESCRIPTION
CV_analysis_agent = Agent(
    name="CV_analysis_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    description="Professional HR assistant that reads, analyzes, and provides insights on candidate CVs.",
    instruction="""
    You are a professional HR assistant specializing in CV analysis and candidate evaluation.
    
    WORKFLOW:
    When asked to analyze a CV:
    1. Use the read_cv tool with the filename provided (supports both .txt and .pdf files)
    2. Thoroughly review the CV content
    3. Provide a comprehensive assessment structured as follows:
    
    ANALYSIS STRUCTURE:
    
    **1. Candidate Information**
    - Full name
    - Contact details (email, phone, LinkedIn, etc.)
    - Location/residence
    
    **2. Technical Skills**
    - List all technical skills mentioned
    - Note proficiency levels when stated
    - Categorize by type (programming languages, frameworks, tools, etc.)
    
    **3. Languages**
    - Spoken/written languages
    - Proficiency levels (native, fluent, intermediate, basic)
    
    **4. Work Experience**
    - Current/most recent position
    - Previous roles with company names
    - Duration of employment for each role
    - Key responsibilities and achievements
    
    **5. Education**
    - Degrees obtained
    - Institutions attended
    - Graduation dates and honors
    - Relevant certifications
    
    **6. Key Strengths**
    - Top 3-5 strengths based on CV content
    - Unique qualifications
    - Notable achievements or projects
    
    **7. Overall Assessment**
    - Professional evaluation
    - Recommendations for roles/positions
    - Any gaps or areas for improvement

    **8. Output**
    - Return a JSON object with keys: full_name, skills, experience, education
    
    IMPORTANT RULES:
    - Always use the read_cv tool when asked to analyze a CV file
    - Be thorough and extract all relevant information
    - Format responses with clear headers and bullet points
    - Be professional and objective
    - If asked follow-up questions, reference the CV you already analyzed
    - For comparisons, use the compare_candidates tool
    
    You have access to these tools:
    - read_cv: Read and analyze a specific CV file (supports .txt and .pdf formats)
    - list_available_cvs: List all available CV files (mainly for testing)
    - compare_candidates: Compare two CVs based on specific criteria
    
    FILE FORMAT SUPPORT:
    - You can read both .txt and .pdf files using the read_cv tool
    - Simply provide the filename with the correct extension
    - Examples: 'resume.txt', 'cv_candidate.pdf'
    """,
    tools=[read_cv, list_available_cvs, compare_candidates]
)

print("✅ Root Agent defined with custom CV tools.")

# TODO: AGENT TO MATCH THE CANDIDATE TO THE JOB DESCRIPTION
# This agent shuold provide N (say 5) suggestions of jobs that the candidate is a good fit for
# Funzione per leggere i job locali

job_listing_agent = Agent(
    name="job_listing_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    description="Agent Assistant that lists job opportunities from the SQLite database and matches candidate skills.",
    instruction="""
    Agent Assistant that provides job listings to candidates.
    Use the job_listing_tool to fetch jobs from the local SQLite database.
    Always expect to receive a string of skills in 'cv_summary' input to match jobs.
    If cv_summary is empty, fetch jobs without filtering.
    """,
    tools=[job_listing_tool],
)

print("✅ job_listing_agent defined.")

# TODO: AGENT TO CREATE AN ASSESSMENT FOR THE CANDIDATE (CODE INTERVIEW)
# This agent shuold create a code interview assessment for the candidate. 
# The assessment should be written in the language mentioned in the uploaded CV.
# The assessment shuould be ran in a sandbox environment. 
# Provide assessment evaluation and feedback to the candidate.

def run_code_assignment(code: str) -> str:
    """
    Funzione che verrà esposta come tool a un agente.
    Riceve il codice scritto dal candidato, lo esegue in sandbox,
    e restituisce output e valutazione base.
    """
    result = execute_code(code)

    # Analisi del risultato
    if result["status"] == "success":
        feedback = f"✅ Code executed successfully!\nOutput:\n{result['output']}"
    elif result["status"] == "timeout":
        feedback = f"⏱ Timeout: The code took longer than allowed ({result['error_msg']})"
    elif result["status"] == "memory_error":
        feedback = f"💾 Memory limit exceeded: {result['error_msg']}"
    elif result["status"] == "security_violation":
        feedback = f"⚠️ Security violation: {result['output']}"
    else:
        feedback = f"❌ Error during execution:\n{result['error_msg']}\nPartial output:\n{result['output']}"

    return feedback

# Tool ADK che espone la funzione all'agente
code_execution_tool = FunctionTool(func=run_code_assignment)


# --- AGENT ---
code_assessment_agent = Agent(
    name="code_assessment_agent",
    model="gemini-2.5-flash-lite",  # usa lo stesso modello che usi per altri agent
    description="""
Professional coding interviewer assistant. Generates code exercises based on the candidate's profile and job requirements,
executes submitted code in a sandbox environment, and provides feedback on correctness, runtime, and potential issues.
""",
    instruction="""
You are a coding interviewer assistant. Your tasks:
1. Generate a coding assignment based on the candidate's CV and the selected job.
2. Tailor difficulty and topics to the candidate's skills.
3. Specify the programming language explicitly (detect from CV).
4. Ask the candidate to submit their solution.
5. Use the tool `run_code_assignment` to execute their code safely in the sandbox.
6. Evaluate the result and give detailed feedback:
   - Success ✅
   - Timeout ⏱
   - Memory issues 💾
   - Security violations ⚠️
   - Other errors ❌
7. Optionally, suggest improvements or next steps.
""",
    tools=[code_execution_tool]
)

# TODO: AGENT TO CREATE AN ASSESSMENT FOR THE CANDIDATE (LANGUAGE TEST)
# This agent shuold create a language test assessment for the candidate. 
# The assessment should be written in the language mentioned in the uploaded CV.
# The candidate shuold be able to provide a message in the chat window to the agent as response to the assessment.
# Provide assessment evaluation and feedback to the candidate.

# TODO: AGENT TO SCHEDULE THE CANDIDATE FOR THE LIVE INTERVIEW
# If the candidate is a good fit, the agent should schedule a live interview for the candidate.
# PitDagosti's tool leveraging google calendar API should be used to schedule the interview.


# TODO: ORCHESTRATOR AGENT
# --- ORCHESTRATOR AGENT AGGIORNATO ---
orchestrator = LlmAgent(
    name="manager",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
    You are a job applicant assistant orchestrator. Coordinate a team of specialized agents to help 
    candidates find their ideal job match. You MUST delegate tasks to your sub-agents.
    
    WORKFLOW AUTOMATICO:
    
    1. STEP 1: CV Analysis
       - When a user uploads a CV, DELEGATE to 'CV_analysis_agent'.
       - Extract key technical skills from the analysis automatically.
       - Summarize candidate profile for confirmation.
       - Then ask: "Would you like me to find job listings that match your profile?"
    
    2. STEP 2: Job Listings Matching
       - If user agrees, call 'job_listing_agent' passing the extracted skills as `cv_summary`.
       - The agent should return up to 5 jobs ranked by matching skills.
       - Present the jobs to the user numerated (1, 2, 3...) and with clear details: title, company, location, description, responsibilities, required skills.
       - Ask: "Which job interests you most? (Choose by selecting the number)".
       - Map the user's numeric selection to the corresponding job in the list.
       - Store the selected job for the next steps (e.g., code assessment).
    
    CRITICAL RULES:
    - ALWAYS delegate to sub-agents using their exact names.
    - NEVER skip steps.
    - Extract and pass skills automatically from CV analysis to job listing agent.
    - Parse numeric input to select the correct job from the numbered list.
    """,
    tools=[
        AgentTool(CV_analysis_agent), 
        AgentTool(job_listing_agent),
        AgentTool(code_assessment_agent)
    ],
)




# ‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️
# Make sure to add necessary tools to src/tools/tools.py and update respective __init__.py files.