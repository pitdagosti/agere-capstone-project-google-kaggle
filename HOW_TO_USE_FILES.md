# 📄 How to Include Files in Agent Prompts

## Quick Reference Guide for CV Analysis

### Method 1: Direct File Reading (Simplest) ✅

```python
from pathlib import Path

# Read the CV file
cv_file_path = Path("../dummy_files_for_testing/cv_john_doe.txt")
cv_content = cv_file_path.read_text()

# Include in prompt
prompt = f"""
Please analyze the following CV:

{cv_content}

Questions:
1. What are the candidate's main technical skills?
2. What languages does the candidate speak?
"""

response = await runner.run_debug(prompt)
```

### Method 2: Using Custom Tools (RECOMMENDED) ⭐

```python
from tools import read_cv_file, create_cv_analysis_prompt

# Read CV
cv_content = read_cv_file("../dummy_files_for_testing/cv_john_doe.txt")

# Create structured prompt
job_description = "Senior Python Developer with microservices experience"
prompt = create_cv_analysis_prompt(cv_content, job_description)

# Run agent
response = await runner.run_debug(prompt)
```

### Method 3: Compare Multiple CVs 

```python
from tools import load_all_cvs

# Load all CVs from folder
all_cvs = load_all_cvs("../dummy_files_for_testing")

# Create comparison prompt
prompt = f"Compare these {len(all_cvs)} candidates for a Python role:\n\n"
for name, content in all_cvs.items():
    prompt += f"--- {name} ---\n{content}\n\n"

response = await runner.run_debug(prompt)
```

### Method 4: PDF Support

```python
from tools import read_cv_file

# Works with both .txt and .pdf files
cv_content = read_cv_file("../dummy_files_for_testing/cv_john_doe.pdf")

# Note: Requires pdfplumber - install with:
# pip install pdfplumber
```

## 📁 Available Test Files

In `dummy_files_for_testing/`:
- `cv_john_doe.txt` - Software Developer
- `cv_john_doe.pdf` - Software Developer (PDF version)
- `cv_maria_santos.txt` - Another candidate
- `cv_maria_santos.pdf` - Another candidate (PDF version)

## 🔧 Custom Tools Available

Located in `tools/tools.py`:

1. **`read_cv_file(file_path)`** - Read any CV file (txt/pdf)
2. **`load_all_cvs(folder_path)`** - Load all CVs from a folder
3. **`create_cv_analysis_prompt(cv_content, job_description)`** - Create structured prompts

## 💡 Pro Tips

1. **Use relative paths** from your notebook location:
   ```python
   "../dummy_files_for_testing/cv_john_doe.txt"
   ```

2. **Always handle encoding** for text files:
   ```python
   cv_content = file_path.read_text(encoding='utf-8')
   ```

3. **Structure your prompts** for better AI responses:
   ```python
   prompt = f"""
   CV Content:
   {cv_content}
   
   Job Requirements:
   {job_requirements}
   
   Please analyze and provide:
   1. Match score (1-10)
   2. Key strengths
   3. Concerns
   4. Recommendation
   """
   ```

4. **Test with small files first** before processing large batches

## 🚀 Next Steps

1. Run Cell 4 in `test_debug_agents.ipynb` to see basic file reading
2. Run Cell 8 to see the custom tools in action
3. Uncomment `response = await runner.run_debug(prompt)` to get actual AI analysis
4. Modify prompts to ask specific questions about candidates

## 📦 Dependencies

For PDF support, add to `requirements.txt`:
```
pdfplumber>=0.10.0
```

Then install:
```bash
pip install pdfplumber
```

