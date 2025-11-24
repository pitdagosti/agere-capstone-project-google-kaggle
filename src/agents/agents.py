# AGENTS FILE 🧑‍🏭

# Packages Import
from google.adk.agents import Agent, LlmAgent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search, AgentTool, FunctionTool
from google.genai import types
from google.adk.models.google_llm import Gemini


# Import custom tools
from src.tools import read_cv, list_available_cvs, compare_candidates

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
job_listing_agent = Agent(
    name="job_listing_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    description="Agent Assistant that searches the internet with Google Search tool.",
    instruction="""
    Agent Assistant that searches the internet with Google Search tool.
    Use Google Search to find job listings for the candidate based on the characteristics of his CV.
    Provide a choice of 5 job listings for the candidate to choose from.
    Wait for candidate choice. If the candidate makes a decision, inform the orchestrator agent,
    otherwise, provide other 5 job listings for the candidate to choose from.
    Repeat the process until the candidate makes a decision.
    """,
    tools=[google_search],
)
# TODO: AGENT TO PROVIDE A PROFILE LINK TO LINKEDIN FOR RECRUITER 
# This Agent Features a Human-in-the-Loop (HITL) layer to ensure the candidate is comfortable with the message before sending it.
recruiter_finder_agent = Agent(
    name="recruiter_finder_agent",
    model=Gemini(model="gemini-2.5-flash-lite"),
    description="Candidate's assistant that finds a recruiter from the company the candidate is applying to.",
    instruction="""
    Candidate's assistant that finds a recruiter from the company the candidate is applying to. 
    Use Google Search to find the recruiter's profile on LinkedIn. 
    If the recruiter's profile is not found you must inform the user that the recruiter's profile is not found 
    and you must provide the user with the company's website link.
    """,
    tools=[google_search],
)

print("✅ Root Agent defined.")
# TODO: AGENT TO CREATE AN ASSESSMENT FOR THE CANDIDATE (CODE INTERVIEW)
# This agent shuold create a code interview assessment for the candidate. 
# The assessment should be written in the language mentioned in the uploaded CV.
# The assessment shuould be ran in a sandbox environment. 
# Provide assessment evaluation and feedback to the candidate.

# TODO: AGENT TO CREATE AN ASSESSMENT FOR THE CANDIDATE (LANGUAGE TEST)
# This agent shuold create a language test assessment for the candidate. 
# The assessment should be written in the language mentioned in the uploaded CV.
# The candidate shuold be able to provide a message in the chat window to the agent as response to the assessment.
# Provide assessment evaluation and feedback to the candidate.

# TODO: AGENT TO SCHEDULE THE CANDIDATE FOR THE LIVE INTERVIEW
# If the candidate is a good fit, the agent should schedule a live interview for the candidate.
# PitDagosti's tool leveraging google calendar API should be used to schedule the interview.


# TODO: ORCHESTRATOR AGENT
orchestrator = LlmAgent(
    name="manager",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    # The instruction explains WHO to call and WHY
    instruction="""
    You are a job applicant assistant orchestrator. You coordinate a team of specialized agents to help 
    candidates find their ideal job match. You MUST delegate tasks to your sub-agents.
    
    YOUR TEAM OF AGENTS:
    1. 'CV_analysis_agent': Analyzes CVs and extracts candidate information, skills, experience
    2. 'job_listing_agent': Searches for job listings that match the candidate's profile
    3. 'recruiter_finder_agent': Finds recruiters. 
    
    WORKFLOW - Follow these steps IN ORDER:
    
    STEP 1: CV Analysis
    - When a user uploads a CV or asks to analyze one, DELEGATE to 'CV_analysis_agent'
    - Wait for the CV analysis to complete
    - Once you receive the analysis, SUMMARIZE it for the user
    - Then EXACTLY ask: "Would you like me to find job listings that match your profile?"
    
    STEP 2: Job Listings (only after CV analysis is complete)
    - When user confirms or asks for job listings, you must DELEGATE to 'job_listing_agent'
    - Ask the job_listing_agent to find 5 relevant jobs based on the CV analysis
    - Present the 5 jobs to the user with clear descriptions
    - Ask the user: "Which job interests you most? (Choose 1-5, or ask for more options)"
    - If user wants more options, delegate to job_listing_agent again for 5 more listings
    - If user selects a job, proceed to Step 3
    
    STEP 3: Recruiter Finder (only after user selects a job)
    - DELEGATE to 'recruiter_finder_agent' with the selected company name
    - Wait for recruiter information
    - Present the recruiter's LinkedIn profile 
    - Ask for user approval before proceeding
    
    CRITICAL RULES:
    - ALWAYS delegate to sub-agents using their exact names
    - NEVER skip steps - follow the workflow sequentially
    - ALWAYS wait for user confirmation before moving to the next major step
    - Keep the user informed of progress at each stage
    - If a user asks a question about the CV, delegate back to CV_analysis_agent
    - Be conversational and helpful, but stay focused on the workflow
    - SPECIFY WHICH AGENT YOU CALLED BEFORE PROVIDING THE ANSWER TO THE USER.
    
    DELEGATION SYNTAX:
    To use a sub-agent, clearly state which agent you're calling and what you need from them.
    Example: "Let me ask the CV_analysis_agent to analyze your CV..."
    """,
    # This automatically registers them as available "tools" for the manager
    tools=[
        AgentTool(CV_analysis_agent), 
        AgentTool(recruiter_finder_agent), 
        AgentTool(job_listing_agent)
    ],
)




# ‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️‼️
# Make sure to add necessary tools to src/tools/tools.py and update respective __init__.py files.