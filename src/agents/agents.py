# AGENTS FILE 🧑‍🏭

from dotenv import load_dotenv
load_dotenv()
# Packages Import
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import google_search, AgentTool, FunctionTool
from google.genai import types
from google.adk.models.google_llm import Gemini
from src.tools.code_sandbox import execute_code
from google.adk.runners import InMemoryRunner
from pathlib import Path



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



# ============================================================================
# Pre-programmed Coding Problems
# ============================================================================

def get_coding_problem(job_title: str = "default") -> dict:
    """
    Returns a pre-programmed coding problem based on the job category.
    These are simple, well-tested problems suitable for the sandbox environment.
    
    Args:
        job_title: The job title to determine which problem to use.
        
    Returns:
        A dictionary with 'title', 'description', 'test_code', 'expected_output'.
    """
    
    # Handle None, empty, or non-string job_title.
    if not job_title or not isinstance(job_title, str):
        job_title = "default"
    
    # Normalize job title for matching
    job_lower = job_title.lower()
    
    # Computer Vision / Image Processing Problems (check FIRST - most specific)
    if any(word in job_lower for word in ['vision', 'computer vision', 'image', 'cv']):
        return {
            'title': 'Image Feature Extractor',
            'description': '''Write a function `extract_features(image_data)` that processes 2D image data.
image_data is a list of lists of pixel intensity values (0-255).
Return the top 3 most frequent pixel values in descending order of frequency.
If fewer than 3 unique values, return all of them.
If empty, return empty list.''',
            'test_code': '''# Test Case 1
image1 = [[10, 20, 10], [30, 10, 20]]
print(extract_features(image1))

# Test Case 2
image2 = [[5, 5, 5], [5, 10, 15]]
print(extract_features(image2))

# Test Case 3
image3 = []
print(extract_features(image3))

# Test Case 4
image4 = [[7]]
print(extract_features(image4))''',
            'expected_output': '[10, 20, 30]\n[5, 10, 15]\n[]\n[7]'
        }
    
    # Backend / API / Microservices Problems
    elif any(word in job_lower for word in ['backend', 'api', 'microservice']):
        return {
            'title': 'User Data Aggregation',
            'description': '''Write a function `sum_even_user_values(users)` that takes a list of dictionaries. 
Each dictionary has 'id' and 'value' keys. Sum the 'value' for users with even 'id'. 
If the sum exceeds 1000, return double the sum. Otherwise, return the sum as is.''',
            'test_code': '''# Test Case 1: Basic test
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
print(sum_even_user_values(users5))''',
            'expected_output': '600\n3600\n0\n0\n1000'
        }
    
    # Data Science / NLP / ML Problems
    elif any(word in job_lower for word in ['data', 'scientist', 'nlp', 'machine learning', 'ml ']):
        return {
            'title': 'Text Sentiment Analyzer',
            'description': '''Write a function `analyze_sentiment(text_list)` that takes a list of strings.
For each text, determine sentiment: 'positive', 'negative', or 'neutral'.
- Contains 'good', 'great', 'excellent', 'love' → 'positive'
- Contains 'bad', 'terrible', 'awful', 'hate' → 'negative'
- Negative keywords take precedence if both present
- Otherwise → 'neutral'
Return a list of sentiment labels.''',
            'test_code': '''# Test Case 1
print(analyze_sentiment(["This is good", "I hate this", "It was excellent", "The weather"]))

# Test Case 2
print(analyze_sentiment([]))

# Test Case 3
print(analyze_sentiment(["This is not good, but it's bad"]))

# Test Case 4
print(analyze_sentiment(["Love the product!", "Terrible service"]))''',
            'expected_output': "['positive', 'negative', 'positive', 'neutral']\n[]\n['negative']\n['positive', 'negative']"
        }
    
    # Full-Stack / Frontend / General Developer Problems
    elif any(word in job_lower for word in ['full', 'stack', 'frontend', 'developer', 'software', 'engineer']):
        return {
            'title': 'Transaction Balance Calculator',
            'description': '''Write a function `calculate_balance(transactions)` that takes a list of transaction dictionaries.
Each has 'type' ('deposit' or 'withdrawal') and 'amount' keys.
Return the final balance: add deposits, subtract withdrawals.
Start from balance 0.''',
            'test_code': '''# Test Case 1
trans1 = [{'type': 'deposit', 'amount': 100}, {'type': 'withdrawal', 'amount': 30}]
print(calculate_balance(trans1))

# Test Case 2
trans2 = []
print(calculate_balance(trans2))

# Test Case 3
trans3 = [{'type': 'withdrawal', 'amount': 50}]
print(calculate_balance(trans3))

# Test Case 4
trans4 = [{'type': 'deposit', 'amount': 200}, {'type': 'deposit', 'amount': 150}, {'type': 'withdrawal', 'amount': 100}]
print(calculate_balance(trans4))''',
            'expected_output': '70\n0\n-50\n250'
        }
    
    # Default problem for any other job
    else:
        return {
            'title': 'List Statistics Calculator',
            'description': '''Write a function `calculate_stats(numbers)` that takes a list of numbers.
Return a dictionary with: 'sum', 'average', 'min', 'max'.
If list is empty, return all values as 0.
Round average to 2 decimal places.''',
            'test_code': '''# Test Case 1
print(calculate_stats([10, 20, 30, 40]))

# Test Case 2
print(calculate_stats([]))

# Test Case 3
print(calculate_stats([5]))

# Test Case 4
print(calculate_stats([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))''',
            'expected_output': "{'sum': 100, 'average': 25.0, 'min': 10, 'max': 40}\n{'sum': 0, 'average': 0, 'min': 0, 'max': 0}\n{'sum': 5, 'average': 5.0, 'min': 5, 'max': 5}\n{'sum': 55, 'average': 5.5, 'min': 1, 'max': 10}"
        }

print("✅ ADK components imported successfully.")
print("✅ ADK will auto-initialize client from environment variables")

# Retry options for API calls.
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

# Agent Definitions
# ADK will automatically read GOOGLE_API_KEY and GOOGLE_GENAI_USE_VERTEXAI
# from environment variables.

# Agent for CV analysis and insights.
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

# Agent to match candidates to job descriptions.
job_listing_agent = Agent(
    name="job_listing_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Agent Assistant that lists job opportunities from the SQLite database and matches candidate skills.",
    instruction="""
    Agent Assistant that MUST PROVIDE job listings to candidates.
    Use the 'job_listing_tool' to fetch jobs from the local SQLite database.
    Always expect to receive a string of skills in 'cv_summary' input to match jobs.
    If cv_summary is empty, fetch jobs without filtering.
    """,
    tools=[job_listing_tool],
)

print("✅ job_listing_agent defined.")

# Agent for creating and evaluating code interview assessments.
code_assessment_agent = Agent(
    name="code_assessment_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Executes candidate code and returns pass/not pass",
    instruction="""You have ONE job: execute code using code_execution_tool.

**MANDATORY PROCESS:**
1. User gives you code
2. You MUST call: code_execution_tool(code="<exact code string>")
3. Read tool response
4. If contains "✅ PASS" → respond ONLY: `pass`
5. If contains "❌" → respond ONLY: `not pass`

**FORBIDDEN:**
- DO NOT analyze code manually
- DO NOT respond without calling tool
- DO NOT skip execution

**Example:**
User: "def add(a,b): return a+b\nprint(add(1,2))"
You: code_execution_tool(code="def add(a,b): return a+b\nprint(add(1,2))")
Tool: "✅ PASS: Output matches!"
You: pass""",
    tools=[code_execution_tool]
)

# Problem Presenter Agent (Shows pre-programmed problems).
problem_presenter_agent = Agent(
    name="problem_presenter_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Presents coding problems using the problem_presenter_tool",
    instruction="""Call problem_presenter_tool(job_title="<job title>") and return its complete output.

DO NOT add commentary. Just call the tool and show its output.""",
    tools=[problem_presenter_tool]
)

# Language Assessment Agent.
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
      
      * French (B2): "Pouvez-vous décrire un proyecto reciente sur lequel vous avez travaillé et quel était votre rôle?"
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

# Agent for scheduling live interviews.
scheduler_agent = Agent(
    name="scheduler_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="Agent that schedules interviews using Google Calendar, with robust token handling.",
    instruction="""
    You schedule interviews only AFTER receiving 'assignment_result: pass'.

    INTELLIGENT WORKFLOW:

    1. Verify assignment_result = 'pass'. If not, stop.
    2. Verify Google Calendar credentials (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN).
       - If missing, respond: "Google Calendar credentials are missing. Please configure them in environment variables."
    3. Refresh access token using refresh token. Stop with clear error if refresh fails.
    4. Fetch busy slots using `calendar_get_busy` for the next 5 business days.
       - Only consider **future slots**, after the current datetime.
       - If fetching fails, log the error but continue with booking if token is valid.
    5. Identify 3-5 free time slots that do not conflict with busy slots.
       - Present these options **to the candidate**.
       - If the candidate email is missing, **ask for it explicitly** before booking.
    6. Once the candidate selects a slot:
       - Book the event using `calendar_book_slot`, passing the candidate email.
       - Confirm the booking with event ID, start, end, and event link.
    7. Log everything:
       - Access token used
       - API responses
       - Any errors or warnings

    ERROR HANDLING:
    - Invalid access token → attempt refresh automatically.
    - API errors (401, 403, 404) → only actionable messages: "Failed to create event: check your Google Calendar account or token."
    - Do not reveal "integration not configured" if credentials exist.
    """,
    tools=[calendar_get_busy, calendar_book_slot]
)


# Orchestrator Agent.
orchestrator = LlmAgent(
    name="manager",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""
You are a job applicant assistant orchestrator. Coordinate a team of specialized agents to help 
candidates find their ideal job match. You MUST delegate tasks to your sub-agents.

WORKFLOW, MANDATORY TO FOLLOW STRICTLY:

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
   - **CRITICAL**: YOU MUST Display jobs in this EXACT format:
   
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

3. STEP 3: Code Assessment (TWO-PHASE PROCESS)
   - **MANDATORY**: ALL software/engineering jobs require a code assessment. Do NOT skip this step.
   
   **PHASE 1: Present Pre-Programmed Problem**
   - After user selects a job number, call 'problem_presenter_tool' DIRECTLY with the job title string.
   - Example: problem_presenter_tool(job_title="Machine Learning Engineer – Computer Vision Focus")
   - The tool will return the complete problem with test cases and constraints.
   - **CRITICAL**: Display the FULL problem to the user exactly as the tool returns it.
   - Wait for the candidate to provide their solution in the chat window.
   
   **PHASE 2: Evaluate Submission**  
   - When user submits code, IMMEDIATELY call code_assessment_agent.
   - Pass the code EXACTLY as submitted, with NO other text.
   - DO NOT say "I'll evaluate this" or "Please execute" - JUST CALL THE AGENT.
   - Wait for agent response: 'pass' or 'not pass'.
   - Store result for scheduling.
   
   **Example flow:**
   User: [submits code]
   You: code_assessment_agent(code="[exact code user submitted]")
   Agent: "pass"
   You: "Great! Your code passed the assessment." 
   THEN MOVE TO STEP 4: LANGUAGE ASSESSMENT, YOU MUST DO THAT AFTER THE CODE ASSESSMENT PASSED.

4. STEP 4: Language Assessment (MANDATORY for multilingual candidates)
   - **CRITICAL**: After code assessment passes, you MUST check the CV analysis from STEP 1.
   - **Language Assessment Trigger:**
      * If CV shows ANY language OTHER THAN English (with proficiency level like B1, B2, C1, C2, Native, Fluent) → Language assessment is REQUIRED
      * Examples that TRIGGER assessment: "Spanish: Fluent", "German: C2", "Portuguese: Native", "French: B1"
      * English-only candidates → Skip language assessment
      * Specify that if user retrieves "Async Error" He should provide the answer again.
   
   - **TWO-PHASE PROCESS (both phases mandatory):**
   
   **PHASE 1: Generate Language Test**
   1. Identify the highest proficiency non-English language from CV
   2. IMMEDIATELY call 'language_assessment_agent' with:
      "Generate a language test for candidate [Name]. CV Languages: [full language list]. Selected job: [Job Title]. Test [Language] at [Level] level."
   3. Display the FULL language test to the user
   4. Wait for candidate's response in the tested language
   
   **PHASE 2: Evaluate Response (DO NOT SKIP THIS!)**
   5. When user submits language response, you MUST call language_assessment_agent IMMEDIATELY.
   6. Format: "Evaluate this [Language] response at [Level] level: [user's text]"
   7. DO NOT paraphrase or summarize the user's response - pass it EXACTLY as written.
   8. Display the agent's evaluation result to the user.
   9. Then proceed to STEP 5 (scheduling) regardless of language result.
   
   **EXAMPLE OF PHASE 2:**
   User submits: "Hola, trabajé en..."
   You MUST call: language_assessment_agent("Evaluate this Spanish response at C1 level: Hola, trabajé en...")
   Agent returns: "Your Spanish demonstrates C1 proficiency. proficiency_confirmed"
   You display: [agent's evaluation]
   Then: Proceed to STEP 5
   
   **CRITICAL**: Do NOT skip calling the agent for evaluation! Do NOT just say "proficiency confirmed" without calling the agent!

5. STEP 5: Schedule Live Interview
   - **CRITICAL**: Only proceed to scheduling if STEP 3 (code assessment) AND 4 (language assessment) returned 'pass'.
   - If code assessment result is 'not pass', inform the user and DO NOT call scheduler_agent.
   - If code assessment result is 'pass' AND language assessment is complete (if applicable), call 'scheduler_agent' with the assessment_result.
   - The scheduler will:
       - Fetch busy slots using `calendar_get_busy`.
       - IT MUST PROPOSE FREE SLOTS TO THE CANDIDATE.
       - Ask the candidate to confirm a preferred time.
       - Book the selected slot using `calendar_book_slot`.
       - Return confirmation with start, end, and event ID.
   - **NEVER skip to scheduling without a code assessment pass result.**

CRITICAL RULES:
- ALWAYS delegate to sub-agents using their exact names.
- NEVER skip steps.
- **NEVER skip code assessment. ALL jobs require code assessment before scheduling.**
- Extract and pass skills automatically from CV analysis to job listing agent.
- Parse numeric input to select the correct job from the numbered list.
- **ALWAYS display the FULL response from sub-agents to the user. NEVER summarize or paraphrase.**
- When CV_analysis_agent returns analysis, show the ENTIRE analysis with all sections.
- When job_listing_agent returns jobs, format them with clear numbers (1, 2, 3...) and ALL details.
- When code_assessment_agent returns an assignment, show the ENTIRE problem statement to the user.
- **DO NOT SKIP showing information. Users CANNOT see what sub-agents return unless you display it.**
- **WORKFLOW ORDER: CV Analysis → Job Selection → Code Assessment → (if pass) Scheduling**
""",
    tools=[
        AgentTool(CV_analysis_agent),
        AgentTool(job_listing_agent),
        problem_presenter_tool,  # Direct tool call instead of agent
        AgentTool(code_assessment_agent),
        AgentTool(language_assessment_agent),
        AgentTool(scheduler_agent),
    ],
)