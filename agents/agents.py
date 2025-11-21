# AGENTS FILE 🧑‍🏭

# Packages Import
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# Import custom tools
from tools import read_cv, list_available_cvs, compare_candidates

# Load environment variables
from dotenv import load_dotenv
import os

load_dotenv()

print("✅ ADK components imported successfully.")
print("✅ ADK will auto-initialize client from environment variables")

# Agents Definition
# ADK will automatically read GOOGLE_API_KEY and GOOGLE_GENAI_USE_VERTEXAI
# from environment variables - no need to create Client explicitly!

# TODO: AGENT TO SCREEN THE RESUME AND CHECK IF IT MATCHES THE JOB DESCRIPTION
root_agent = Agent(
    name="read_CV_assistant",
    model="gemini-2.0-flash-exp",
    description="Agent to read and analyze CVs from the dummy_files_for_testing folder.",
    instruction="""
    You are a helpful assistant to the human resources department.
    
    Your capabilities:
    - Read CV files using the read_cv tool
    - List available CVs using the list_available_cvs tool
    - Compare candidates using the compare_candidates tool
    
    When analyzing CVs, provide:
    1. Key technical skills and experience level
    2. Languages spoken and proficiency
    3. Work experience summary
    4. Educational background
    5. Overall assessment and recommendations
    
    Be thorough, professional, and objective in your analysis.""",
    tools=[read_cv, list_available_cvs, compare_candidates],
    # No api_client parameter - ADK auto-initializes from environment!
)

print("✅ Root Agent defined with custom CV tools.")

# TODO: AGENT TO MATCH THE CANDIDATE TO THE JOB DESCRIPTION
# TODO: AGENT TO CREATE AN ASSESSMENT FOR THE CANDIDATE (CODE INTERVIEW)
# TODO: AGENT TO CREATE AN ASSESSMENT FOR THE CANDIDATE (LANGUAGE TEST)
# TODO: AGENT TO SCHEDULE THE CANDIDATE FOR THE LIVE INTERVIEW
