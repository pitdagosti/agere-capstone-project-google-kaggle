# Tool Separation: Test vs Production

## Issue Fixed

The agent was mentioning "dummy_files_for_testing" folder in its responses to end users during Streamlit sessions, which was confusing because users upload files dynamically during runtime.

## Solution

### 1. Updated `tools.py` - Production Tools

**Changes:**
- Removed mention of `dummy_files_for_testing` from the tool annotation and docstring
- Tool description now focuses on "CV files that have been uploaded for analysis"
- Error messages don't mention technical folder names
- The tool still checks both folders internally (temp_uploads first, dummy_files_for_testing as silent fallback)

```python
def read_cv(filename: Annotated[str, "Name of the CV file to read and analyze"]) -> str:
    """
    Read a CV file that has been uploaded for analysis.
    """
```

### 2. Updated `agents.py` - Agent Instructions

**Changes:**
- Removed mention of `dummy_files_for_testing` from agent description
- Updated agent instructions to emphasize using the read_cv tool directly
- Agent now explicitly told to "Always use your read_cv tool to access CV files when asked to analyze them"

### 3. Updated `main.py` - Prompts

**Changes:**
- Simplified prompts to directly instruct: "Please use the read_cv tool to analyze the CV file named..."
- Removed confusing references to folders in prompts
- Chat prompts now simply say "Reference the CV file you previously analyzed"

## How It Works

### For End Users (Streamlit):
1. User uploads CV → Saved to `temp_uploads/`
2. Agent reads from `temp_uploads/` (transparently)
3. No mention of folder structure to the user

### For Testing (Notebooks):
1. Test files remain in `dummy_files_for_testing/`
2. Agent can still access them (as fallback)
3. Tests in `test_debug_tools.ipynb` continue to work

## File Structure

```
project/
├── temp_uploads/           # Dynamically uploaded files (Streamlit)
│   └── cv_maria_santos.pdf
├── dummy_files_for_testing/ # Static test files (for notebooks)
│   ├── cv_john_doe.txt
│   └── cv_maria_santos.pdf
└── tools/
    ├── tools.py             # Production tools (used by Streamlit)
    └── test_debug_tools.ipynb # Test tools (for development)
```

## Key Principle

**Separation of Concerns:**
- **Production tools** (`tools.py`) → User-facing, clean abstractions, no technical details
- **Test tools** (notebooks) → Development/debugging, can be more verbose
- **Internal implementation** → Can check multiple locations, but don't expose this to users

## Testing

Run Streamlit and verify the agent no longer mentions folder names:
```bash
streamlit run main.py
```

Expected behavior:
- Upload a CV
- Click "Analyze CV"  
- Agent should directly read and analyze without asking about folders
- No mention of `dummy_files_for_testing` in agent responses

