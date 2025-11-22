# PROJECT AGERE (Agentic Recruiter) 🤖

AI-Powered CV Analysis and Recruitment System

## 📁 Project Structure

```
capstone-project-google-kaggle/
├── __init__.py              # Root package initialization
├── main.py                  # Streamlit web application
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
│
├── agents/                 # 🧑‍🏭 Agent definitions
│   ├── __init__.py        # Agents package
│   └── agents.py          # Agent implementations
│
├── tools/                  # 🔧 Custom tools
│   ├── __init__.py        # Tools package
│   └── tools.py           # Tool implementations
│
├── notebooks/             # 📓 Development notebooks
│   └── main.ipynb
│
└── test_debug_notebooks/  # 🧪 Testing notebooks
    └── main.ipynb
```

## 🚀 Getting Started

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd capstone-project-google-kaggle
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your API keys
```

### Running the Application

**Streamlit Web App:**
```bash
streamlit run main.py
```

**Jupyter Notebooks:**
```bash
jupyter notebook
```

## 📦 Package Structure

The project uses Python's package system with `__init__.py` files for clean imports.

### Importing Agents

```python
# Import specific components
from agents import root_agent, Agent, InMemoryRunner

# Use the agent
runner = InMemoryRunner()
response = runner.run(root_agent, "Analyze this CV...")
```

### Importing Tools

```python
# Import the tools package
import tools

# Or import specific tools (when you create them)
from tools import custom_tool
```

### In Notebooks

For notebooks in subfolders, add this at the top:

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path().absolute().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now import normally
from agents import root_agent
import tools
```

## 🧑‍🏭 Agents

Current agents defined in `agents/agents.py`:

- **`root_agent`** - CV reading and job description matching assistant

### Adding New Agents

1. Define your agent in `agents/agents.py`
2. Export it in `agents/__init__.py`
3. Import where needed: `from agents import your_agent`

## 🔧 Tools

Custom tools can be added in `tools/tools.py`.

### Creating Custom Tools

```python
# In tools/tools.py
def custom_cv_parser(cv_text: str) -> dict:
    """Parse CV and extract key information."""
    # Your implementation
    return parsed_data
```

Then export in `tools/__init__.py`:
```python
from .tools import custom_cv_parser

__all__ = ['custom_cv_parser']
```

## 📝 TODO

- [ ] Agent to match candidate to job description
- [ ] Agent to create code interview assessment
- [ ] Agent to create language test
- [ ] Agent to schedule live interview
- [ ] Custom CV parsing tool
- [ ] Custom tool for personalized functions

## 🤝 Contributing

Feel free to add ideas and improvements to the agents and tools!

## 📄 License

See LICENSE file for details.

