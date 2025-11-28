# AGENTS FILE 🧑‍🏭

# Packages Import
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import google_search, AgentTool, FunctionTool
from google.genai import types
from google.adk.models.google_llm import Gemini
from src.tools.code_sandbox import execute_code
from google.adk.runners import InMemoryRunner
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


from src.tools import (
    read_cv, 
    list_available_cvs, 
    compare_candidates, 
    job_listing_tool,
    calendar_get_busy,
    calendar_book_slot,
    code_execution_tool,
    problem_presenter_tool,
)

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
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
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
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
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

# --- AGENT ---

# =============================================================================
# CODE ASSESSMENT: PROBLEM TEMPLATES (100% RELIABLE)
# =============================================================================

CODING_PROBLEMS = {
    "backend": {
        "title": "User Data Aggregation",
        "description": """Write a function `sum_even_user_values(users)` that takes a list of dictionaries. 
Each dictionary has 'id' and 'value' keys. Sum the 'value' for users with even 'id'. 
If the sum exceeds 1000, return double the sum. Otherwise, return the sum as is.""",
        "test_code": """# Test Case 1: Basic test
users1 = [{'id': 1, 'value': 100}, {'id': 2, 'value': 200}, {'id': 3, 'value': 300}, {'id': 4, 'value': 400}]
print(sum_even_user_values(users1))

# Test Case 2: Sum exceeds 1000
users2 = [{'id': 2, 'value': 500}, {'id': 4, 'value': 600}, {'id': 6, 'value': 700}]
print(sum_even_user_values(users2))

# Test Case 3: No even IDs
users3 = [{'id': 1, 'value': 100}, {'id': 3, 'value': 300}, {'id': 5, 'value': 500}]
print(sum_even_user_values(users3))

# Test Case 4: Empty list
users4 = []
print(sum_even_user_values(users4))

# Test Case 5: Sum equals 1000
users5 = [{'id': 2, 'value': 500}, {'id': 3, 'value': 100}, {'id': 4, 'value': 500}]
print(sum_even_user_values(users5))""",
        "expected_output": "600\n3400\n0\n0\n1000"
    },
    "fullstack": {
        "title": "Text Statistics Calculator",
        "description": """Write a function `calculate_text_stats(text)` that returns a dictionary with:
- 'word_count': total words (space-separated)
- 'char_count': total characters including spaces
- 'avg_word_length': average word length (0 if no words)
- 'most_frequent_word': most frequent word (alphabetically first if tie, None if empty)""",
        "test_code": """# Test Case 1
print(calculate_text_stats("hello world hello"))

# Test Case 2
print(calculate_text_stats("one two three four five"))

# Test Case 3
print(calculate_text_stats(""))

# Test Case 4
print(calculate_text_stats("repeat repeat test test test"))""",
        "expected_output": "{'word_count': 3, 'char_count': 17, 'avg_word_length': 5.0, 'most_frequent_word': 'hello'}\n{'word_count': 5, 'char_count': 23, 'avg_word_length': 3.6, 'most_frequent_word': 'five'}\n{'word_count': 0, 'char_count': 0, 'avg_word_length': 0, 'most_frequent_word': None}\n{'word_count': 5, 'char_count': 29, 'avg_word_length': 4.0, 'most_frequent_word': 'test'}"
    },
    "datascience": {
        "title": "List Statistics",
        "description": """Write a function `analyze_numbers(numbers)` that returns a dictionary with:
- 'sum': sum of all numbers
- 'min': minimum (None if empty)
- 'max': maximum (None if empty)
- 'average': average (None if empty)""",
        "test_code": """# Test Case 1
print(analyze_numbers([1, 2, 3, 4, 5]))

# Test Case 2
print(analyze_numbers([-10, 0, 10, 20]))

# Test Case 3
print(analyze_numbers([100]))

# Test Case 4
print(analyze_numbers([]))""",
        "expected_output": "{'sum': 15, 'min': 1, 'max': 5, 'average': 3.0}\n{'sum': 20, 'min': -10, 'max': 20, 'average': 5.0}\n{'sum': 100, 'min': 100, 'max': 100, 'average': 100.0}\n{'sum': 0, 'min': None, 'max': None, 'average': None}"
    },
    "default": {
        "title": "List Sum Calculator",
        "description": """Write a function `sum_list(nums)` that returns the sum of all numbers in a list.""",
        "test_code": """# Test Case 1
print(sum_list([1, 2, 3]))

# Test Case 2
print(sum_list([10, 20, 30]))

# Test Case 3
print(sum_list([]))

# Test Case 4
print(sum_list([-5, 5]))""",
        "expected_output": "6\n60\n0\n0"
    }
}

def get_coding_problem(job_category="default"):
    """Helper to get appropriate problem based on job type"""
    # Map job keywords to problem categories
    job_lower = job_category.lower()
    if "backend" in job_lower or "api" in job_lower or "microservice" in job_lower:
        return CODING_PROBLEMS["backend"]
    elif "fullstack" in job_lower or "full-stack" in job_lower or "full stack" in job_lower:
        return CODING_PROBLEMS["fullstack"]
    elif "data" in job_lower or "scientist" in job_lower or "ml" in job_lower or "machine learning" in job_lower:
        return CODING_PROBLEMS["datascience"]
    else:
        return CODING_PROBLEMS["default"]

# =============================================================================
# CODE EVALUATOR AGENT (SIMPLE & FOCUSED)
# =============================================================================

code_evaluator_agent = Agent(
    name="code_evaluator_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="""Evaluates submitted code by executing it and comparing output.""",
    instruction="""You are a code evaluator. Your job is VERY SIMPLE.

**STEP 1**: Call the tool `run_code_assignment` with the code provided in the request.

**STEP 2**: Read the tool's response:
- If it contains "✅ PASS" → respond with exactly: pass
- If it contains "❌ FAIL" or "❌" or "FAIL" → respond with exactly: not pass

**YOUR RESPONSE MUST BE EXACTLY ONE WORD**: either `pass` or `not pass`

No explanations. No extra text. Just one word.
""",
    tools=[code_execution_tool]
)

# Language Assessment Agent
language_assessment_agent = Agent(
    name="language_assessment_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="""
        Professional language proficiency assessment agent. Creates a simple language test
        based on the candidate's CV languages, evaluates their response, and provides proficiency feedback.
        """,
    instruction="""
    You are an expert language assessment agent. You have two distinct modes of operation.

    **MODE 1: Language Test Generation**
    - You will be given information about a candidate's language skills from their CV.
    - **Your Task:**
      1. Select ONE language from the CV that the candidate claims proficiency in (preferably not their native language).
      2. Create a SIMPLE conversational prompt in that language.
      3. The prompt should be appropriate for the proficiency level claimed (e.g., if they claim B1, use B1-level language).
    
    - **Assessment Guidelines:**
      * **A1-A2 (Basic):** Simple introduction, daily activities
      * **B1-B2 (Intermediate):** Describe experience, opinions, short scenarios
      * **C1-C2 (Advanced):** Complex topics, abstract concepts, professional situations
    
    - **Good Examples:**
      * Spanish (B1): "Por favor, describe tu experiencia laboral más reciente y qué responsabilidades tenías."
        (Please describe your most recent work experience and what responsibilities you had.)
      
      * German (C1): "Bitte erläutern Sie, wie Sie mit technischen Herausforderungen in Ihrem letzten Projekt umgegangen sind."
        (Please explain how you dealt with technical challenges in your last project.)
      
      * French (B2): "Pouvez-vous décrire un projet récent sur lequel vous avez travaillé et quel était votre rôle?"
        (Can you describe a recent project you worked on and what was your role?)
    
    - After generating the prompt, clearly state:
      * Which language you're testing
      * What proficiency level you're assessing
      * Ask the candidate to respond in that language

    **MODE 2: Response Evaluation**
    - When the candidate provides their response, evaluate it based on:
      1. **Appropriateness:** Did they respond in the correct language?
      2. **Comprehension:** Did they understand the prompt?
      3. **Grammar and Vocabulary:** Quality of language use for the claimed level
      4. **Completeness:** Did they fully address the question?
    
    - **Your Evaluation Response:**
      * Provide a brief assessment (2-3 sentences)
      * State whether the response demonstrates the claimed proficiency level
      * Final verdict: `proficiency_confirmed` or `proficiency_needs_improvement`
    
    - **Example Evaluation:**
      "Your response demonstrates good comprehension and appropriate vocabulary for B1 level Spanish. 
      Grammar is mostly correct with minor errors typical of this level. The response fully addresses 
      the question about work experience. Verdict: proficiency_confirmed"

    **IMPORTANT RULES:**
    - Be encouraging and professional in your feedback
    - Consider that candidates may be nervous
    - Minor errors are acceptable if overall communication is effective
    - Only test ONE language per assessment
    - If they respond in the wrong language, note this in evaluation
    """,
    tools=[]  # No tools needed for language assessment
)

# TODO: AGENT TO SCHEDULE THE CANDIDATE FOR THE LIVE INTERVIEW
# If the candidate is a good fit, the agent should schedule a live interview for the candidate.
# PitDagosti's tool leveraging google calendar API should be used to schedule the interview.

scheduler_agent = Agent(
    name="scheduler_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Agent that schedules interviews using Google Calendar.",
    instruction="""
    You schedule interviews only AFTER receiving 'assignment_result: pass'.

    WORKFLOW:
    1. If assignment_result = 'failed', respond: 'The assessment was not passed. No scheduling will occur.'
    2. If assignment_result = 'pass':
       - Call the tool `calendar_get_busy` with appropriate start/end times (e.g., next 7 days).
       - **CRITICAL ERROR HANDLING**: Check the tool's response:
         * If response starts with "❌ CALENDAR_NOT_CONFIGURED" → Display the configuration error to the user with clear instructions.
         * If response starts with "❌ CALENDAR_API_ERROR" → Inform the user that Calendar integration is not available and suggest manual scheduling.
         * If response starts with "✅ Successfully fetched" → Parse busy slots and propose free times.
       - If calendar is configured correctly:
         * Propose 3-5 free time slots to the candidate.
         * Ask the candidate to pick one.
         * When the candidate confirms a time, use `calendar_book_slot` to create the event.
         * After booking, confirm the booking details.
       - If calendar is NOT configured:
         * Inform the user: "Google Calendar integration is not currently configured. Please contact the interviewer directly to schedule your interview."

    RULES:
    - Do NOT infer busy slots manually; always call the tool first.
    - If the tool returns an error (starts with ❌), display the error message to the user clearly.
    - Continue asking the user until they confirm a specific time (only if calendar is configured).
    - Validate ISO datetime formats before booking.
    - Always check tool responses for success (✅) or error (❌) indicators.
    """,
    tools=[calendar_get_busy, calendar_book_slot]
)

# --- ORCHESTRATOR AGENT ---

orchestrator = LlmAgent(
    name="manager",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
You are a job applicant assistant orchestrator. Coordinate a team of specialized agents to help 
candidates find their ideal job match. You MUST delegate tasks to your sub-agents.

WORKFLOW AUTOMATICO:

1. STEP 1: CV Analysis
   - When a user uploads a CV, DELEGATE to 'CV_analysis_agent'.
   - **CRITICAL**: The agent will return a detailed analysis. You MUST display the FULL analysis to the user.
     Show ALL sections: Candidate Information, Technical Skills, Languages, Work Experience, Education, Key Strengths, Overall Assessment.
   - After showing the full analysis, extract key technical skills from it automatically.
   - Provide a brief summary of the candidate's profile.
   - Then ask: "Would you like me to find job listings that match your profile?"

2. STEP 2: Job Listings Matching
   - If user agrees, call 'job_listing_agent' passing the extracted skills as `cv_summary`.
   - The agent will return job listings. You MUST format and display them properly.
   - **CRITICAL**: Display jobs in this EXACT format:
   
   1. **Job Title** at Company
      - Location: [location]
      - Description: [description]
      - Responsibilities: [responsibilities]
      - Required Skills: [skills]
   
   2. **Job Title** at Company
      - Location: [location]
      - Description: [description]
      - Responsibilities: [responsibilities]
      - Required Skills: [skills]
   
   - After displaying ALL jobs with numbers, ask: "Which job interests you most? (Choose by selecting the number)".
   - When user provides a number, map it to the corresponding job and proceed to code assessment.

3. STEP 3: Code Assessment (TWO-PHASE PROCESS - 100% RELIABLE)
   - **MANDATORY**: ALL software/engineering jobs require a code assessment. Do NOT skip this step.
   
   **PHASE 1: Present Coding Problem**
   - After user selects a job number, you will AUTOMATICALLY generate and present a coding problem.
   - **AUTOMATIC PROCESS (NO AGENT CALL NEEDED)**:
     1. Identify the job category from the selected job title
     2. Call the helper function to get the appropriate problem template
     3. Store the expected output using: `run_code_assignment(code="# Setup", expected_output="<expected_output>")`
     4. Display the problem to the user in this format:
     
     **Coding Assessment: [Problem Title]**
     
     **Problem Description:**
     [problem description]
     
     **Test Cases:**
     ```python
     [test code]
     ```
     
     **Instructions:**
     - Write your solution function
     - Include the test cases at the end of your code
     - DO NOT use import statements
     - Only use built-in functions: print, range, len, sum, min, max, abs, round, int, str, list, dict, tuple, set, float, bool, sorted, enumerate, zip
     
     **Please submit your complete code (function + test cases).**
   
   - Wait for the candidate to submit their code.
   
   **PHASE 2: Evaluate Submission**
   - When user submits code, call 'code_evaluator_agent' with the submitted code.
   - The agent will:
     * Execute the code in the sandbox
     * Compare output with stored expected output
     * Return either 'pass' or 'not pass'
   - **Store the assessment result** (pass/not pass) for the scheduling step.

4. STEP 4: Language Assessment (MANDATORY for multilingual candidates ONLY IF code assessment passed)
   - **CRITICAL**: You can ONLY proceed to language assessment if STEP 3 (code assessment) returned 'pass'.
   - **If code assessment returned 'not pass', SKIP language assessment and inform the user they need to pass the code assessment first.**
   - **Language Assessment Trigger (only if code passed):**
      * If CV shows ANY language OTHER THAN English (with proficiency level like B1, B2, C1, C2, Native, Fluent) → Language assessment is REQUIRED
      * Examples that TRIGGER assessment: "Spanish: Fluent", "German: C2", "Portuguese: Native", "French: B1"
      * English-only candidates → Skip language assessment
   - **PROCESS:**
      1. **VERIFY code assessment result is 'pass' before proceeding**
      2. Identify the highest proficiency non-English language from CV
      3. Call 'language_assessment_agent' with: 
         - Candidate CV information (including language section)
         - Selected job details
         - Instruction: "Test proficiency in [language] at [level]"
      4. Display the language test to the user
      5. Wait for candidate's response in the tested language
      6. Call 'language_assessment_agent' again to evaluate the response
      7. Display evaluation result: `proficiency_confirmed` or `proficiency_needs_improvement`
   - **Note**: Language assessment result is informational and does NOT block scheduling (but you must pass code assessment first).

5. STEP 5: Schedule Live Interview
   - **CRITICAL**: Only proceed to scheduling if STEP 3 (code assessment) returned 'pass'.
   - **If code assessment result is 'not pass':**
      * Inform the user: "Your code assessment did not pass. You need to pass the code assessment before scheduling an interview."
      * DO NOT proceed to language assessment
      * DO NOT call scheduler_agent
      * Offer the user options: retry the assessment, try a different job, or ask for feedback
   - **If code assessment result is 'pass' AND language assessment is complete (if applicable):**
      * Call 'scheduler_agent' with the assessment_result
      * The scheduler will:
        - Fetch busy slots using `calendar_get_busy`.
        - Propose free slots to the candidate.
        - Ask the candidate to confirm a preferred time.
        - Book the selected slot using `calendar_book_slot`.
        - Return confirmation with start, end, and event ID.
   - **NEVER skip to scheduling without a code assessment pass result.**
   - **NEVER proceed to language assessment if code assessment failed.**

CRITICAL RULES:
- ALWAYS delegate to sub-agents using their exact names.
- NEVER skip steps.
- **NEVER skip code assessment. ALL jobs require code assessment before scheduling.**
- Extract and pass skills automatically from CV analysis to job listing agent.
- Parse numeric input to select the correct job from the numbered list.
- **ALWAYS display the FULL response from sub-agents to the user. NEVER summarize or paraphrase.**
- When CV_analysis_agent returns analysis, show the ENTIRE analysis with all sections.
- When job_listing_agent returns jobs, format them with clear numbers (1, 2, 3...) and ALL details.
- When presenting a code assessment, show the ENTIRE problem statement to the user.
- **DO NOT SKIP showing information. Users CANNOT see what sub-agents return unless you display it.**
- **WORKFLOW ORDER: CV Analysis → Job Selection → Code Assessment → (if pass) Scheduling**
""",
    tools=[
        AgentTool(CV_analysis_agent),
        AgentTool(job_listing_agent),
        problem_presenter_tool,  # Function tool for presenting problems
        code_execution_tool,  # Function tool for storing expected output
        AgentTool(code_evaluator_agent),
        AgentTool(language_assessment_agent),
        AgentTool(scheduler_agent),
    ],
)




# ‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️
# Make sure to add necessary tools to src/tools/tools.py and update respective __init__.py files.