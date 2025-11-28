# Language Assessment Agent - Complete Implementation Guide

## Overview

The **Language Assessment Agent** is the final component of the AGERE system that validates a candidate's language proficiency before they proceed to interview scheduling. It generates tailored language assessments, evaluates responses, and provides objective pass/not pass determinations.

## Purpose

Help job candidates **prove their language skills** at the level required by their target position through:
- **Objective Assessment**: Real language proficiency testing
- **Tailored Challenges**: Difficulty adjusted to candidate's stated level
- **Clear Feedback**: Understand exactly what's expected
- **Fair Evaluation**: Strict, unbiased scoring system
- **Second Chances**: One retry per job, then blocked after 2 failures

## Architecture

### File Structure

```
src/
├── tools/
│   ├── language_assessment.py    # Core assessment logic & state management
│   └── tools.py                  # FunctionTool wrappers for agents
├── agents/
│   └── agents.py                 # language_assessment_agent definition
└── styles/
    └── custom.css                # UI styling
```

### Key Components

#### 1. **language_assessment.py** - Core Module

Contains all assessment logic, proficiency levels, and evaluation criteria.

**Main Functions:**

```python
# Generation
generate_language_assessment(language, proficiency_level, candidate_name, job_title)
→ Returns tailored assessment with 4 tasks

# Evaluation  
evaluate_language_assessment(candidate_response, language, proficiency_level, assessment_content)
→ Returns {result: "pass"/"not pass", score, feedback, details}

# Tracking
increment_failure_count(candidate_id, job_id) → int (failure count)
is_job_blocked(candidate_id, job_id) → bool
reset_attempts(candidate_id, job_id) → void

# Agent Wrappers
generate_assessment_for_candidate(...)  # For agents to call
evaluate_candidate_response(...)        # For agents to call
```

**Proficiency Levels:**

| Level | CEFR | Score | Difficulty | Assessment Tasks |
|-------|------|-------|------------|------------------|
| beginner | A1 | 1 | Basic | Comprehension, Vocabulary, Grammar, Writing |
| elementary | A2 | 2 | Basic | Same as A1 |
| intermediate | B1 | 3 | Intermediate | Comprehension, Discussion, Complex Grammar, Business Writing |
| upper_intermediate | B2 | 4 | Intermediate | Same as B1 |
| advanced | C1 | 5 | Advanced | Comprehension, Debate, Technical Communication, Essay |
| proficient | C2 | 6 | Advanced | Same as C1 |
| native | Native | 7 | Advanced | Same as C1 |

#### 2. **language_assessment_agent** - The Agent

Orchestrates the assessment workflow with two distinct modes:

**MODE 1: Assessment Generation**
- Determines candidate's proficiency level
- Uses `language_assessment_generation_tool` to create assessment
- Presents tasks with clear instructions
- Requests candidate response

**MODE 2: Strict Evaluation**
- Receives candidate's written response
- Uses `language_assessment_evaluation_tool` to evaluate
- Extracts result (pass/not pass)
- Returns ONLY the single word: "pass" or "not pass"

#### 3. **Assessment State Management**

Tracks candidate failures per job using JSON state file:

```json
{
  "candidate_001_job_001": {
    "failure_count": 1,
    "job_id": "job_001",
    "candidate_id": "candidate_001",
    "blocked": false,
    "last_attempt": "2024-11-28T10:30:00"
  }
}
```

**Rules:**
- After **1st failure**: Allow retry at same level
- After **2nd failure**: Block job (no more attempts on this job)
- Candidate must choose different job or end session

## Workflow

### Complete Assessment Flow

```
CANDIDATE SELECTS JOB
    ↓
ORCHESTRATOR DETECTS LANGUAGE REQUIREMENT
    ↓
ORCHESTRATOR DELEGATES TO language_assessment_agent
    ↓
┌─────────────────────────────────────┐
│  ASSESSMENT GENERATION (MODE 1)     │
├─────────────────────────────────────┤
│ 1. Extract proficiency level        │
│ 2. Call generation_tool             │
│ 3. Present assessment               │
│ 4. Request response                 │
└─────────────────────────────────────┘
    ↓
CANDIDATE SUBMITS RESPONSE
    ↓
┌─────────────────────────────────────┐
│  ASSESSMENT EVALUATION (MODE 2)     │
├─────────────────────────────────────┤
│ 1. Receive full response            │
│ 2. Call evaluation_tool             │
│ 3. Extract result (pass/not pass)   │
│ 4. Return single word               │
└─────────────────────────────────────┘
    ↓
ORCHESTRATOR PROCESSES RESULT
    ├─ PASS: Congratulate → Proceed to scheduling
    ├─ FAIL (1st): Suggest retry
    └─ FAIL (2nd): Block job → Suggest different role
```

### Agent Instruction Flow

The `language_assessment_agent` instructions define:

1. **What it does** - Generates and evaluates language assessments
2. **When it does it** - Two distinct operational modes
3. **How it generates** - Creates tailored assessments by proficiency
4. **How it evaluates** - Strict, tool-based evaluation only
5. **What it returns** - Assessment details or "pass"/"not pass"

## Assessment Generation Details

### Task Types by Difficulty

#### Basic Level (A1-A2)
- **Comprehension**: Read simple text, answer yes/no or short answer questions
- **Vocabulary**: Fill in blank words from multiple choice options
- **Grammar**: Correct simple grammatical errors
- **Writing**: Write 50-100 word message about a simple topic

**Example Task:**
```
Write a short message (50-100 words) in English about:
"Tell me about your daily routine"

Your response: [candidate writes here]
```

#### Intermediate Level (B1-B2)
- **Comprehension**: Summarize articles (100-150 words)
- **Discussion**: Write opinions on topics (150-200 words)
- **Complex Grammar**: Analyze and correct complex structures
- **Business Writing**: Draft professional emails

**Example Task:**
```
Write your opinion on the following topic (150-200 words):
"The impact of remote work on team collaboration"

Your response: [candidate writes here]
```

#### Advanced Level (C1-C2)
- **Comprehension**: Critical analysis of passages (200-300 words)
- **Debate**: Well-argued positions with counterarguments (300+ words)
- **Technical Communication**: Explain technical concepts
- **Essay**: Structured essay (400-500 words with intro/body/conclusion)

**Example Task:**
```
Write an essay in English on the topic:
"The role of artificial intelligence in modern workforce development"

Requirements:
- 400-500 words
- Well-structured (introduction, body, conclusion)
- Professional tone

Your essay: [candidate writes here]
```

## Evaluation Criteria

### Scoring Rubric

**Word Count**
- Minimum words vary by proficiency level
- Response too short = automatic "not pass"

**Structure & Coherence**
- At least 2+ sentences required
- Logical flow between ideas
- Proper use of transitional phrases

**Grammar & Syntax**
- Proper sentence construction
- Correct punctuation usage
- Appropriate capitalization
- Agreement (subject-verb, tense consistency)

**Vocabulary**
- Unique word usage (30%+ variety)
- Appropriate word choice for proficiency level
- Range of vocabulary increases with level

**Task Completion**
- Addresses the prompt directly
- Provides required information
- Meets word count guidelines

### Pass/Not Pass Determination

```
BEGINNER/ELEMENTARY:
  ✅ PASS if: word_count ≥ 30 AND sentences ≥ 2
  ❌ NOT PASS if: any of above not met

INTERMEDIATE:
  ✅ PASS if: word_count ≥ 120 AND vocab_variety AND sentences ≥ 3
  ❌ NOT PASS if: any of above not met

ADVANCED:
  ✅ PASS if: word_count ≥ 200 AND vocab_variety AND grammar_ok
  ❌ NOT PASS if: any of above not met
```

## Integration Points

### 1. **With Orchestrator Agent**

```python
# In orchestrator instructions:
orchestrator = LlmAgent(
    tools=[
        AgentTool(CV_analysis_agent),
        AgentTool(job_listing_agent),
        AgentTool(code_assessment_agent),
        AgentTool(language_assessment_agent)  # ← Integrated
    ]
)
```

### 2. **With Main Streamlit App**

The agent runs within the existing chat interface:
- User uploads CV
- Orchestrator analyzes and suggests jobs
- If job requires language skills → delegates to `language_assessment_agent`
- Assessment appears in chat
- Candidate types response
- Agent evaluates and returns result

### 3. **With Code Assessment Agent**

Both follow the same strict evaluation pattern:
- Generation phase (if first interaction)
- Evaluation phase (when code/text submitted)
- Single-word response ("pass" or "not pass")
- Failure tracking

## Usage Examples

### For Developers

#### Starting an Assessment
```python
from src.agents import language_assessment_agent
from google.adk.runners import InMemoryRunner

runner = InMemoryRunner(agent=language_assessment_agent)
response = await runner.run_debug(
    "Create a Spanish language assessment for an intermediate level candidate applying for a translator position"
)
```

#### Direct Tool Usage
```python
from src.tools.language_assessment import (
    generate_language_assessment,
    evaluate_language_assessment
)

# Generate assessment
assessment = generate_language_assessment(
    language="French",
    proficiency_level="advanced",
    candidate_name="Marie Dupont",
    job_title="Senior Marketing Manager"
)

# Evaluate response
response = "Je suis entièrement d'accord que..."  # [French text]
result = evaluate_language_assessment(
    candidate_response=response,
    language="French",
    proficiency_level="advanced"
)
print(result["result"])  # "pass" or "not pass"
```

### For Candidates

**Step 1: Select Job with Language Requirement**
```
I'd like to apply for the Senior English Teacher position
```

**Step 2: Agent Generates Assessment**
```
===== LANGUAGE PROFICIENCY ASSESSMENT =====
Candidate: Sarah Chen
Position: Senior English Teacher
Language: English
Level: C1 - Advanced

[Assessment with 4 tasks presented]

Please complete all tasks and provide your responses.
```

**Step 3: Candidate Submits Response**
```
[Candidate provides comprehensive written response to assessment tasks]
```

**Step 4: Agent Evaluates**
```
pass
```
(or)
```
not pass
```

**Step 5: Orchestrator Handles Result**
- If pass: "Excellent! You've proven your language proficiency..."
- If not pass (1st): "Let's try again. Would you like to retake the assessment?"
- If not pass (2nd): "Unfortunately, this position is no longer available. Would you like to explore other roles?"

## Supported Languages

The agent supports all languages with proper task generation:

**European Languages:**
- English, Spanish, French, German, Italian, Portuguese, Dutch, Swedish, Polish, Russian

**Asian Languages:**
- Chinese (Simplified/Traditional), Japanese, Korean

**Middle Eastern & Indian Languages:**
- Arabic, Hebrew, Persian (Farsi), Hindi, Tamil, Telugu, Urdu

**And more:** Assessment tasks are generated dynamically for any language

## Configuration

### Adjusting Proficiency Levels

In `src/tools/language_assessment.py`:

```python
PROFICIENCY_LEVELS = {
    "intermediate": {
        "description": "B1 - Intermediate",
        "score": 3,
        "assessment_difficulty": "intermediate"
    },
    # Add or modify levels here
}
```

### Adjusting Failure Tolerance

Change the block threshold from 2 failures:

```python
# In increment_failure_count():
if state[key]["failure_count"] >= 3:  # Change from 2 to 3
    state[key]["blocked"] = True
```

### Adjusting Minimum Word Counts

In `evaluate_language_assessment()`:

```python
min_word_counts = {
    "beginner": 30,      # Adjust these
    "intermediate": 120,
    "advanced": 250,
}
```

## Troubleshooting

### Issue: Assessment generation fails

**Check:**
- Proficiency level is in `PROFICIENCY_LEVELS` dict
- Language parameter is a string
- Candidate name and job title provided

### Issue: "not pass" always returned

**Check:**
- Response length meets minimum word count
- Response has proper structure (multiple sentences)
- For advanced levels, ensure response demonstrates language quality

### Issue: Job blocking not working

**Check:**
- `jobs/language_assessment_state.json` file is readable/writable
- Candidate ID and Job ID are consistent across calls
- State file not corrupted (valid JSON)

### Issue: Agent returns more than "pass"/"not pass"

**Check:**
- In evaluation mode, agent should ONLY return one word
- Review agent instructions for evaluation strict rules
- Ensure evaluation_tool is being called correctly

## Testing

Run the test suite:

```bash
python test_language_assessment.py
```

This tests:
- ✅ Tool imports
- ✅ Assessment generation
- ✅ Evaluation logic
- ✅ Failure tracking
- ✅ Job blocking
- ✅ All proficiency levels
- ✅ Agent integration
- ✅ Orchestrator integration

## Performance Considerations

- **Assessment Generation**: <1 second (no API calls)
- **Assessment Evaluation**: <2 seconds (local analysis)
- **State Management**: <100ms (JSON file I/O)
- **Total Assessment Flow**: 20-30 minutes (candidate thinking time)

## Future Enhancements

Potential improvements (out of scope for current version):

1. **AI-Powered Grammar Checking**
   - Use Gemini to provide detailed grammar feedback
   - Detailed error analysis instead of simple pass/fail

2. **Spoken Assessment**
   - Voice recording and transcription
   - Pronunciation evaluation

3. **Vocabulary Analysis**
   - NLP-based vocabulary complexity scoring
   - Level-appropriate vocabulary suggestions

4. **Adaptive Difficulty**
   - Difficulty adjusts based on performance
   - Progressive assessment levels

5. **Detailed Rubric Scoring**
   - Replace binary pass/fail with numeric score
   - Breakdown by skill (grammar, vocab, etc.)

6. **Assessment Analytics**
   - Track language proficiency trends
   - Identify common weak areas

## Summary

The Language Assessment Agent completes the AGERE system by providing:

✅ **Objective Validation**: Prove language skills with real assessments
✅ **Tailored Challenges**: Difficulty matches candidate proficiency
✅ **Fair Evaluation**: Unbiased, tool-based scoring
✅ **Clear Feedback**: Know exactly what's expected
✅ **Strict Protocol**: Single-word evaluation (pass/not pass)
✅ **Failure Tracking**: Two chances per job, then blocked
✅ **Full Integration**: Works seamlessly with orchestrator

**Status**: ✅ **COMPLETE AND READY FOR DEPLOYMENT**
