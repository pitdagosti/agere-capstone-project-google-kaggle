"""
PROJECT AGERE (Agentic Recruiter)
Main Streamlit Application

Main entry point for the Agentic Recruiter application.
Users can upload their CV/resume and interact with the AI-powered recruitment system.
"""

import streamlit as st
import os
import asyncio
import html
from dotenv import load_dotenv
from pathlib import Path
import json
from datetime import datetime
from google.adk.runners import InMemoryRunner

from src.agents import *  # Tutti gli agenti, incluso orchestrator, sono importati qui.
load_dotenv()

# Explicitly set environment variables for ADK (needed for Streamlit)
api_key = os.getenv("GOOGLE_API_KEY")
use_vertexai = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key
if use_vertexai:
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = use_vertexai

# Page configuration
st.set_page_config(
    page_title="AGERE - Agentic Recruiter",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load custom CSS from external file
def load_css():
    """Load custom CSS styling from external file"""
    css_file = Path(__file__).parent / "src" / "styles" / "custom.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state for chat and agent
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'runner' not in st.session_state:
    st.session_state.runner = None
if 'current_cv_file' not in st.session_state:
    st.session_state.current_cv_file = None
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = False
if 'uploaded_file_content' not in st.session_state:
    st.session_state.uploaded_file_content = None

# Logging
LOG_DIR = Path(__file__).parent / "log_files"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "runner_events.log"


def log_agent_event(event):
    """
    Log agent events by parsing nested content parts for Tools and Text.
    Fixed: handles NoneType safely
    """
    log_entry = {
        "timestamp": datetime.now().timestamp(),
        "agent_name": getattr(event, "agent_name", "Orchestrator"),
        "tool_name": None,
        "input_text": None,
        "output_text": None,
        "type": "unknown"
    }

    has_content = False

    # Parse content parts
    if hasattr(event, "content") and event.content:
        parts = getattr(event.content, "parts", [])
        if parts:
            for part in parts:
                # Agent Text
                if hasattr(part, "text") and part.text:
                    log_entry["type"] = "response"
                    current = log_entry["output_text"] or ""
                    log_entry["output_text"] = current + part.text
                    has_content = True

                # Tool Call
                if hasattr(part, "function_call") and getattr(part, "function_call", None):
                    log_entry["type"] = "tool_call"
                    log_entry["tool_name"] = getattr(part.function_call, "name", None)
                    try:
                        args_dict = getattr(part.function_call, "args", {})
                        if args_dict is not None:
                            if hasattr(args_dict, "items"):
                                args_dict = dict(args_dict.items())
                            log_entry["input_text"] = json.dumps(args_dict, ensure_ascii=False)
                        else:
                            log_entry["input_text"] = None
                    except Exception:
                        log_entry["input_text"] = str(getattr(part.function_call, "args", None))
                    has_content = True

                # Tool Response
                if hasattr(part, "function_response") and getattr(part, "function_response", None):
                    log_entry["type"] = "tool_result"
                    log_entry["tool_name"] = getattr(part.function_response, "name", None)
                    try:
                        resp_dict = getattr(part.function_response, "response", {})
                        if resp_dict is not None:
                            if hasattr(resp_dict, "items"):
                                resp_dict = dict(resp_dict.items())
                            log_entry["output_text"] = json.dumps(resp_dict, ensure_ascii=False)
                        else:
                            log_entry["output_text"] = None
                    except Exception:
                        log_entry["output_text"] = str(getattr(part.function_response, "response", None))
                    has_content = True

    # Fallback for user input
    if not has_content and hasattr(event, "user_content"):
        log_entry["type"] = "user_input"
        input_text = getattr(event.user_content, "text", None)
        if not input_text and hasattr(event.user_content, "parts"):
            parts = getattr(event.user_content, "parts", [])
            texts = [p.text for p in parts if hasattr(p, "text") and p.text]
            if texts:
                input_text = " ".join(texts)
        log_entry["input_text"] = input_text
        if input_text:
            has_content = True

    # Write log only if content exists
    if has_content:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def extract_agent_response(events):
    """
    Extract all text from agent events.
    Safely handles NoneType and missing parts.
    """
    if not events:
        return None

    full_text = []

    for event in events:
        log_agent_event(event)  # sempre loggare
        content = getattr(event, 'content', None)
        parts = getattr(content, 'parts', []) if content and getattr(content, 'parts', None) else []

        for part in parts:
            text = getattr(part, 'text', None)
            if text:
                full_text.append(text)
            else:
                # Debug: parti non testuali
                print("DEBUG: non-text part detected", part)

    return "".join(full_text) if full_text else None


async def run_agent_async(runner, prompt):
    """Run agent and return response safely, never None"""
    if runner is None:
        return "⚠️ Error: agent runner is not initialized."
    try:
        response = await runner.run_debug(prompt)
        text = extract_agent_response(response)
        if text is None or text.strip() == "":
            return "⚠️ The agent processed your request but produced no output."
        return text
    except Exception as e:
        return f"⚠️ Error running agent asynchronously: {str(e)}"


def run_agent_sync(runner, prompt):
    """Synchronous wrapper for async agent calls safely"""
    if runner is None:
        return "⚠️ Error: agent runner is not initialized."
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_agent_async(runner, prompt))
        loop.close()
        return result
    except Exception as e:
        return f"⚠️ Error running agent synchronously: {str(e)}"


def analyze_cv_with_runner(runner, filename):
    """Call orchestrator agent to analyze CV safely, never returns None"""
    if runner is None:
        return "⚠️ Error: agent runner is not initialized."
    
    prompt = f"""I've uploaded my CV file: {filename}

Please analyze it and help me find suitable job opportunities."""
    
    try:
        with st.spinner("🤖 Orchestrator Agent starting workflow..."):
            response = run_agent_sync(runner, prompt)
        
        if response is None or response.strip() == "":
            return "⚠️ Analysis completed but the agent did not generate a response."
        return response
    
    except Exception as e:
        return f"⚠️ Error during CV analysis: {str(e)}"


@st.dialog("📊 CV Analysis & Chat", width="large")
def show_analysis_dialog(uploaded_file):
    """Display CV analysis and chat in a modal dialog safely"""

    if st.session_state.runner is None:
        st.session_state.runner = InMemoryRunner(
            agent=orchestrator,
            app_name="agents"
        )

    temp_uploads_dir = Path(__file__).parent / "temp_uploads"
    temp_uploads_dir.mkdir(exist_ok=True)
    
    temp_file_path = temp_uploads_dir / uploaded_file.name

    # Salva file solo se è nuovo
    if st.session_state.current_cv_file != uploaded_file.name:
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # Aggiorna stato sessione solo se file nuovo
    if st.session_state.current_cv_file != uploaded_file.name:
        st.session_state.current_cv_file = uploaded_file.name
        st.session_state.messages = []

        st.subheader("🔍 Initial CV Analysis")
        st.caption(f"Analyzing: **{uploaded_file.name}** ({uploaded_file.type})")

        # Chiamata agente
        analysis_result = analyze_cv_with_runner(st.session_state.runner, uploaded_file.name)

        if analysis_result is not None:
            st.session_state.messages.append({
                "role": "assistant",
                "content": analysis_result
            })
        else:
            st.warning("Analysis completed but no response was generated.")

    # Mostra chat
    st.markdown("---")
    st.subheader("💬 Chat with AI Recruiter")
    st.caption(f"Currently analyzing: **{uploaded_file.name}**")

    chat_container = st.container()
    input_container = st.container()

    # Mostra messaggi esistenti
    with chat_container:
        for message in st.session_state.messages or []:  # sicuro anche se None
            if not message or "role" not in message or "content" not in message:
                continue
            if message["role"] == "user":
                # Check if message contains code (multiline or starts with def/import)
                content = message["content"]
                if "\n" in content or content.strip().startswith(("def ", "import ", "from ", "class ")):
                    # Render as markdown code block for proper formatting
                    with st.chat_message("user"):
                        st.code(content, language="python")
                else:
                    # Regular text message with HTML escape
                    st.markdown(
                        f"""<div class="user-message-container">
<div class="user-message-bubble">{html.escape(content)}</div>
</div>""",
                        unsafe_allow_html=True
                    )
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # Input utente
    with input_container:
        prompt = st.chat_input("Ask questions about this CV or request additional analysis...")

    if prompt:
        # Log user input
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().timestamp(),
                "agent_name": "User",
                "tool_name": None,
                "input_text": prompt,
                "output_text": None,
                "type": "user_input"
            }, ensure_ascii=False) + "\n")
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            # Check if message contains code (multiline or starts with def/import)
            if "\n" in prompt or prompt.strip().startswith(("def ", "import ", "from ", "class ")):
                # Render as markdown code block for proper formatting
                with st.chat_message("user"):
                    st.code(prompt, language="python")
            else:
                # Regular text message with HTML escape
                st.markdown(
                    f"""<div class="user-message-container">
<div class="user-message-bubble">{html.escape(prompt)}</div>
</div>""",
                    unsafe_allow_html=True
                )

        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🤖 AI Agent thinking..."):
                    try:
                        if "```" in prompt or prompt.strip().startswith("import") or "def " in prompt:
                            feedback = run_agent_sync(
                                st.session_state.runner,
                                f"Please execute this Python code safely in sandbox:\n{prompt}"
                            )
                            st.markdown(feedback)
                            st.session_state.messages.append({"role": "assistant", "content": feedback})
                        else:
                            response = run_agent_sync(st.session_state.runner, prompt)
                            if response is not None:
                                st.markdown(response)
                                st.session_state.messages.append({"role": "assistant", "content": response})
                            else:
                                fallback_msg = "I processed your request but couldn't generate a response. Please try rephrasing."
                                st.warning(fallback_msg)
                                st.session_state.messages.append({"role": "assistant", "content": fallback_msg})
                    except Exception as e:
                        st.error(f"⚠️ Agent failed: {e}")
                        st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Agent failed: {e}"})



def main():
    """Main application function"""
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>PROJECT AGERE</h1>
            <h3>Agentic Recruiter - AI-Powered CV Analysis</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # How it works section
    st.markdown("### 🚀 How it works")
    steps_col1, steps_col2, steps_col3, steps_col4 = st.columns(4)
    
    with steps_col1:
        st.markdown("""
            <div class="step-item">
                <div class="step-number">1</div>
                <p><strong>Upload CV</strong><br>PDF or TXT format</p>
            </div>
        """, unsafe_allow_html=True)
        
    with steps_col2:
        st.markdown("""
            <div class="step-item">
                <div class="step-number">2</div>
                <p><strong>AI Analysis</strong><br>Deep extraction</p>
            </div>
        """, unsafe_allow_html=True)
        
    with steps_col3:
        st.markdown("""
            <div class="step-item">
                <div class="step-number">3</div>
                <p><strong>Chat & Ask</strong><br>Interactive QA</p>
            </div>
        """, unsafe_allow_html=True)
        
    with steps_col4:
        st.markdown("""
            <div class="step-item">
                <div class="step-number">4</div>
                <p><strong>Insights</strong><br>Get recommendations</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main content area
    st.header("📄 Upload Resume/CV")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Drop your file here or click to upload",
        type=["pdf", "txt"],
        help="Supported formats: PDF, TXT. Maximum file size: 200MB",
        key="cv_uploader"
    )
    
    if uploaded_file is not None:
        # Display file details
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        file_details = {
            "Filename": uploaded_file.name,
            "File Type": uploaded_file.type,
            "File Size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        
        with st.expander("📋 File Details", expanded=False):
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
        
        # Action buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔍 Analyze CV", type="primary", use_container_width=True):
                show_analysis_dialog(uploaded_file)
                
        with col_btn2:
            if st.button("🗑️ Clear & Reset", use_container_width=True):
                # Delete ALL files from temp_uploads folder
                temp_uploads_dir = Path(__file__).parent / "temp_uploads"
                if temp_uploads_dir.exists():
                    try:
                        # Delete all files in the temp_uploads directory
                        deleted_count = 0
                        for file in temp_uploads_dir.iterdir():
                            if file.is_file():  # Only delete files, not directories
                                file.unlink()
                                deleted_count += 1
                        if deleted_count > 0:
                            st.success(f"🗑️ Deleted {deleted_count} file(s) from temp_uploads")
                    except Exception as e:
                        st.error(f"Could not delete files: {e}")
                
                # Clear session state completely
                st.session_state.messages = []
                st.session_state.current_cv_file = None
                st.session_state.show_analysis = False
                st.session_state.uploaded_file_content = None
                # Clear the file uploader by resetting its key
                if 'cv_uploader' in st.session_state:
                    del st.session_state['cv_uploader']
                st.rerun()
    
    # Features Section
    st.markdown("---")
    st.subheader("✨ Features")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">Smart Analysis</div>
                <div class="feature-desc">Advanced AI agents extract skills, experience, and qualifications instantly.</div>
            </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-title">Interactive Chat</div>
                <div class="feature-desc">Ask specific questions about candidates and get evidence-based answers.</div>
            </div>
        """, unsafe_allow_html=True)
        
    with feat_col3:
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Match Scoring</div>
                <div class="feature-desc">Get objective suitability scores for specific job roles and requirements.</div>
            </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div class="footer">
            <p>🤖 PROJECT AGERE - Agentic Recruiter | Powered by Google Vertex AI</p>
            <p>v1.0.0 | Built with Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()