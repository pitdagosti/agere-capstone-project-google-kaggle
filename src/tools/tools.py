# CUSTOM TOOLS FOR AGENTS 🔧

from pathlib import Path
from typing import Dict, Union, Annotated
from google.genai import types

# =============================================================================
# CUSTOM ADK TOOLS - These can be used in Agent tools=[] parameter
# =============================================================================

def read_cv(filename: Annotated[str, "Name of the CV file to read and analyze"]) -> str:
    """
    Read a CV file that has been uploaded for analysis.
    This tool allows the agent to read candidate CVs.
    
    Args:
        filename: Name of the CV file (e.g., 'cv_john_doe.txt' or 'candidate_resume.pdf')
        
    Returns:
        str: Content of the CV file
    """
    # Check both temp_uploads (for Streamlit uploads) and dummy_files_for_testing (for testing)
    # Base path should be the project root (two levels up from src/tools/tools.py)
    base_path = Path(__file__).parent.parent.parent
    temp_uploads_path = base_path / "temp_uploads" / filename
    dummy_files_path = base_path / "dummy_files_for_testing" / filename
    
    # Try temp_uploads first (for uploaded files), then dummy_files_for_testing (silently as fallback)
    if temp_uploads_path.exists():
        file_path = temp_uploads_path
    elif dummy_files_path.exists():
        file_path = dummy_files_path
    else:
        return f"❌ Error: Could not find the CV file '{filename}'. Please ensure the file was uploaded successfully."
    
    try:
        if file_path.suffix == '.txt':
            content = file_path.read_text(encoding='utf-8')
            return f"✅ Successfully read {filename}:\n\n{content}"
        
        elif file_path.suffix == '.pdf':
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                    return f"✅ Successfully read {filename}:\n\n{text}"
            except ImportError:
                return "⚠️ PDF reading requires pdfplumber. Install with: pip install pdfplumber"
        else:
            return f"❌ Unsupported file type: {file_path.suffix}. Supported types: .txt, .pdf"
            
    except Exception as e:
        return f"❌ Error reading file: {str(e)}"


def list_available_cvs() -> str:
    """
    List all available CV files in the dummy_files_for_testing folder.
    Use this tool to see what CVs are available to analyze.
    
    Returns:
        str: List of available CV files
    """
    # Base path should be the project root (three levels up from src/tools/tools.py)
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


def compare_candidates(
    filename1: Annotated[str, "First CV filename"],
    filename2: Annotated[str, "Second CV filename"],
    criteria: Annotated[str, "Comparison criteria (e.g., 'Python experience')"]
) -> str:
    """
    Compare two candidate CVs based on specific criteria.
    
    Args:
        filename1: First CV filename
        filename2: Second CV filename  
        criteria: What to compare (e.g., 'Python experience', 'language skills')
        
    Returns:
        str: Both CVs with comparison context
    """
    cv1 = read_cv(filename1)
    cv2 = read_cv(filename2)
    
    return f"""
Comparing two candidates on: {criteria}

=== CANDIDATE 1: {filename1} ===
{cv1}

=== CANDIDATE 2: {filename2} ===
{cv2}

Please compare these candidates specifically on: {criteria}
"""


# =============================================================================
# HELPER FUNCTIONS - Not ADK tools, just utility functions
# =============================================================================

def read_cv_file(file_path: Union[str, Path]) -> str:
    """
    Helper function to read CV file (not an ADK tool, just a utility)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if file_path.suffix == '.txt':
        return file_path.read_text(encoding='utf-8')
    
    elif file_path.suffix == '.pdf':
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
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

