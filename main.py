"""
PROJECT AGERE (Agentic Recruiter)
Main Streamlit Application

This is the main entry point for the Agentic Recruiter application.
Users can upload their CV/resume and interact with the AI-powered recruitment system.
"""

import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path

# Import your agents and tools
from agents import root_agent, InMemoryRunner
import tools

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AGERE - Agentic Recruiter",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .upload-section {
        padding: 2rem;
        border: 2px dashed #667eea;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-left: 4px solid #667eea;
        background-color: #f0f2f6;
        border-radius: 5px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🤖 PROJECT AGERE</h1>
            <h3>Agentic Recruiter - AI-Powered CV Analysis</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 About")
        st.info("""
        **AGERE** is an intelligent recruitment assistant that analyzes 
        CVs/resumes using advanced AI agents to provide insights and recommendations.
        """)
        
        st.header("⚙️ Settings")
        # Placeholder for future settings
        analysis_depth = st.selectbox(
            "Analysis Depth",
            ["Quick Scan", "Standard Analysis", "Deep Dive"],
            index=1
        )
        
        st.header("📊 Status")
        st.success("System Ready")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Upload Resume/CV")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Upload your CV (PDF or TXT format)",
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
            
            with st.expander("📋 File Details", expanded=True):
                for key, value in file_details.items():
                    st.write(f"**{key}:** {value}")
            
            # Action buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                if st.button("🔍 Analyze CV", type="primary", use_container_width=True):
                    st.session_state.analyze_clicked = True
                    
            with col_btn2:
                if st.button("👁️ Preview", use_container_width=True):
                    st.session_state.preview_clicked = True
                    
            with col_btn3:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.session_state.clear_clicked = True
                    st.rerun()
        
        else:
            st.markdown("""
                <div class="upload-section">
                    <p style="text-align: center; color: #667eea; font-size: 1.2rem;">
                        👆 Click above to upload a resume/CV
                    </p>
                    <p style="text-align: center; color: #666;">
                        Drag and drop is also supported
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.header("📊 Analysis Results")
        
        if uploaded_file is not None and st.session_state.get('analyze_clicked', False):
            # Placeholder for analysis results
            with st.spinner("🤖 AI Agents analyzing CV..."):
                # This is where the actual analysis will happen
                st.info("⚠️ Analysis functionality coming soon!")
                
                # Placeholder sections
                with st.expander("📌 Key Information", expanded=True):
                    st.markdown("""
                    - **Name:** [To be extracted]
                    - **Email:** [To be extracted]
                    - **Phone:** [To be extracted]
                    - **Location:** [To be extracted]
                    """)
                
                with st.expander("💼 Work Experience"):
                    st.write("Work experience analysis will appear here...")
                
                with st.expander("🎓 Education"):
                    st.write("Education details will appear here...")
                
                with st.expander("🛠️ Skills"):
                    st.write("Skills extraction will appear here...")
                
                with st.expander("🎯 Recommendations"):
                    st.write("AI-generated recommendations will appear here...")
        
        elif uploaded_file is not None and st.session_state.get('preview_clicked', False):
            # Preview section
            st.subheader("📄 Document Preview")
            
            if uploaded_file.type == "text/plain":
                # Display text file content
                text_content = uploaded_file.read().decode("utf-8")
                st.text_area("Content", text_content, height=400)
            elif uploaded_file.type == "application/pdf":
                st.info("📑 PDF preview - Full PDF parsing coming soon!")
                st.write("PDF files will be parsed and displayed here.")
            
        else:
            st.markdown("""
                <div class="info-box">
                    <h4>🤖 How it works:</h4>
                    <ol>
                        <li>Upload your CV in PDF or TXT format</li>
                        <li>Click 'Analyze CV' to start the AI analysis</li>
                        <li>Review the extracted information and insights</li>
                        <li>Get AI-powered recommendations</li>
                    </ol>
                </div>
            """, unsafe_allow_html=True)
            
            # Feature highlights
            st.subheader("✨ Features")
            
            feature_col1, feature_col2 = st.columns(2)
            
            with feature_col1:
                st.markdown("""
                - 🔍 **Smart Extraction**
                - 💡 **AI Insights**
                - 📈 **Skill Analysis**
                """)
            
            with feature_col2:
                st.markdown("""
                - 🎯 **Job Matching**
                - 📊 **Experience Mapping**
                - ✅ **Quality Scoring**
                """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; padding: 1rem;">
            <p>🤖 PROJECT AGERE - Agentic Recruiter | Powered by AI</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

