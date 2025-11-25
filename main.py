"""
PROJECT AGERE (Agentic Recruiter)
Main Streamlit Application

This is the main entry point for the Agentic Recruiter application.
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

# Import your agents and tools
from src.agents import *

# Load environment variables
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

LOG_FILE = Path(__file__).parent / "runner_events.log"

# --- INIZIO MODIFICHE LOGGING ---

def log_agent_event(event):
    """
    Log agent events parsing nested content parts for Tools and Text.
    """
    # 1. Struttura base del log
    log_entry = {
        "timestamp": datetime.now().timestamp(),
        "agent_name": getattr(event, "agent_name", "Orchestrator"),
        "tool_name": None,
        "input_text": None,   # Usato per argomenti tool o input utente
        "output_text": None,  # Usato per risposte text o risultati tool
        "type": "unknown"
    }

    has_content = False

    # 2. Analisi delle parti del contenuto (Content Parts)
    if hasattr(event, "content") and event.content:
        if hasattr(event.content, "parts") and event.content.parts:
            for part in event.content.parts:
                
                # A. L'Agente Parla (Text)
                if hasattr(part, "text") and part.text:
                    log_entry["type"] = "response"
                    # Concatena se ci sono più parti di testo
                    current = log_entry["output_text"] or ""
                    log_entry["output_text"] = current + part.text
                    has_content = True

                # B. L'Agente chiama un Tool (Function Call)
                if hasattr(part, "function_call") and part.function_call:
                    log_entry["type"] = "tool_call"
                    log_entry["tool_name"] = part.function_call.name
                    # Estrae gli argomenti della funzione
                    try:
                        args_dict = dict(part.function_call.args.items())
                        log_entry["input_text"] = json.dumps(args_dict, ensure_ascii=False)
                    except Exception:
                        log_entry["input_text"] = str(part.function_call.args)
                    has_content = True

                # C. Il Tool risponde (Function Response)
                if hasattr(part, "function_response") and part.function_response:
                    log_entry["type"] = "tool_result"
                    log_entry["tool_name"] = part.function_response.name
                    # Estrae il risultato
                    try:
                        resp_dict = dict(part.function_response.response.items())
                        log_entry["output_text"] = json.dumps(resp_dict, ensure_ascii=False)
                    except Exception:
                        log_entry["output_text"] = str(part.function_response.response)
                    has_content = True

    # 3. Analisi Input Utente (se presente nell'evento, meno comune in output stream)
    if not has_content and hasattr(event, "user_content"):
        # Logica di fallback se l'evento porta solo input utente
        log_entry["type"] = "user_input"
        input_text = getattr(event.user_content, "text", None)
        if not input_text and hasattr(event.user_content, "parts"):
             texts = [p.text for p in event.user_content.parts if hasattr(p, "text") and p.text]
             if texts: input_text = " ".join(texts)
        log_entry["input_text"] = input_text
        if input_text: has_content = True

    # 4. Scrittura su file solo se c'è contenuto utile
    if has_content:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

def extract_agent_response(events):
    """Extract text response from agent events"""
    full_text = []
    for event in events:
        log_agent_event(event)  # log every event with new logic
        
        # Estrazione specifica del testo per la UI di Streamlit
        if hasattr(event, 'content') and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    full_text.append(part.text)
    
    return "".join(full_text) if full_text else None

# --- FINE MODIFICHE LOGGING ---

async def run_agent_async(runner, prompt):
    """Run agent and return response"""
    try:
        response = await runner.run_debug(prompt)
        return extract_agent_response(response)
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def run_agent_sync(runner, prompt):
    """Synchronous wrapper for async agent calls"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_agent_async(runner, prompt))
        loop.close()
        return result
    except Exception as e:
        return f"⚠️ Error running agent: {str(e)}"

def analyze_cv_with_runner(runner, filename):
    """Call the orchestrator agent to start the CV analysis workflow"""
    try:
        prompt = f"""I've uploaded my CV file: {filename}
        
Please analyze it and help me find suitable job opportunities."""
        
        with st.spinner("🤖 Orchestrator Agent starting workflow..."):
            response = run_agent_sync(runner, prompt)
        
        if response:
            return response
        else:
            return "⚠️ Analysis completed but no response was generated."
            
    except Exception as e:
        return f"⚠️ Error during analysis: {str(e)}"

@st.dialog("📊 CV Analysis & Chat", width="large")
def show_analysis_dialog(uploaded_file):
    """Display CV analysis and chat in a modal dialog"""
    
    if st.session_state.runner is None:
        st.session_state.runner = InMemoryRunner(agent=orchestrator)
    
    temp_uploads_dir = Path(__file__).parent / "temp_uploads"
    temp_uploads_dir.mkdir(exist_ok=True)
    
    temp_file_path = temp_uploads_dir / uploaded_file.name
    
    if st.session_state.current_cv_file != uploaded_file.name:
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    if st.session_state.current_cv_file != uploaded_file.name:
        st.session_state.current_cv_file = uploaded_file.name
        st.session_state.messages = []
        
        st.subheader("🔍 Initial CV Analysis")
        st.caption(f"Analyzing: **{uploaded_file.name}** ({uploaded_file.type})")
        
        analysis_result = analyze_cv_with_runner(st.session_state.runner, uploaded_file.name)
        
        if analysis_result:
            st.session_state.messages.append({
                "role": "assistant",
                "content": analysis_result
            })
        else:
            st.warning("Analysis completed but no response generated.")
    
    st.markdown("---")
    st.subheader("💬 Chat with AI Recruiter")
    st.caption(f"Currently analyzing: **{uploaded_file.name}**")
    
    chat_container = st.container()
    input_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(
                    f"""<div class="user-message-container">
<div class="user-message-bubble">{html.escape(message["content"])}</div>
</div>""",
                    unsafe_allow_html=True
                )
            else:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    with input_container:
        prompt = st.chat_input("Ask questions about this CV or request additional analysis...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            st.markdown(
                f"""<div class="user-message-container">
<div class="user-message-bubble">{html.escape(prompt)}</div>
</div>""",
                unsafe_allow_html=True
            )
        
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🤖 AI Agent thinking..."):
                    response = run_agent_sync(st.session_state.runner, prompt)
                    
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        fallback_msg = "I processed your request but couldn't generate a response. Please try rephrasing."
                        st.warning(fallback_msg)
                        st.session_state.messages.append({"role": "assistant", "content": fallback_msg})

def main():
    """Main application function"""
    
    st.markdown("""
        <div class="main-header">
            <h1>PROJECT AGERE</h1>
            <h3>Agentic Recruiter - AI-Powered CV Analysis</h3>
        </div>
    """, unsafe_allow_html=True)
    
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
    
    st.header("📄 Upload Resume/CV")
    
    uploaded_file = st.file_uploader(
        "Drop your file here or click to upload",
        type=["pdf", "txt"],
        help="Supported formats: PDF, TXT. Maximum file size: 200MB",
        key="cv_uploader"
    )
    
    if uploaded_file is not None:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        file_details = {
            "Filename": uploaded_file.name,
            "File Type": uploaded_file.type,
            "File Size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        
        with st.expander("📋 File Details", expanded=False):
            for key, value in file_details.items():
                st.write(f"**{key}:** {value}")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔍 Analyze CV", type="primary", use_container_width=True):
                show_analysis_dialog(uploaded_file)
                
        with col_btn2:
            if st.button("🗑️ Clear & Reset", use_container_width=True):
                temp_uploads_dir = Path(__file__).parent / "temp_uploads"
                if temp_uploads_dir.exists():
                    try:
                        deleted_count = 0
                        for file in temp_uploads_dir.iterdir():
                            if file.is_file():
                                file.unlink()
                                deleted_count += 1
                        if deleted_count > 0:
                            st.success(f"🗑️ Deleted {deleted_count} file(s) from temp_uploads")
                    except Exception as e:
                        st.error(f"Could not delete files: {e}")
                
                st.session_state.messages = []
                st.session_state.current_cv_file = None
                st.session_state.show_analysis = False
                st.session_state.uploaded_file_content = None
                if 'cv_uploader' in st.session_state:
                    del st.session_state['cv_uploader']
                st.rerun()
    
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

    st.markdown("""
        <div class="footer">
            <p>🤖 PROJECT AGERE - Agentic Recruiter | Powered by Google Vertex AI</p>
            <p>v1.0.0 | Built with Streamlit</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
