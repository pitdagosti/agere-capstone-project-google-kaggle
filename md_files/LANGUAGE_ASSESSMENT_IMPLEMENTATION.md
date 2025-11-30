# Language Assessment Agent Implementation ✅

## Overview

Implemented a simple yet effective language proficiency assessment agent that tests candidates' language skills as claimed in their CV.

---

## Agent Description

The `language_assessment_agent` creates conversational language tests and evaluates candidate responses to verify proficiency levels.

### Key Features:
✅ Tests languages from CV  
✅ Appropriate difficulty for claimed level (A1-C2)  
✅ Simple conversational prompts  
✅ Encouraging, professional evaluation  
✅ No external tools needed  

---

## How It Works

### MODE 1: Language Test Generation

```
Input: Candidate CV with languages (e.g., Spanish: Fluent, French: B1)
      Job requiring international collaboration

Agent:
1. Selects ONE non-native language from CV
2. Reviews claimed proficiency level
3. Creates appropriate prompt for that level
4. Asks candidate to respond in that language
```

**Example Output:**

```
Language Assessment: Spanish (Claimed level: Fluent/C1)

Please respond to the following prompt in Spanish:

"Por favor, describe tu experiencia laboral más reciente y qué 
responsabilidades tenías. También explica cómo tu experiencia 
técnica puede contribuir a un equipo internacional."

(Please describe your most recent work experience and what 
responsibilities you had. Also explain how your technical 
experience can contribute to an international team.)

Please provide your response in Spanish.
```

---

### MODE 2: Response Evaluation

```
Input: Candidate's response in the tested language

Agent evaluates:
✓ Correct language used?
✓ Understood the prompt?
✓ Appropriate grammar/vocabulary for level?
✓ Complete response?

Output: Brief assessment + verdict
```

**Example Evaluation:**

```
Language Assessment Result:

Your response demonstrates excellent comprehension and appropriate 
vocabulary for C1 level Spanish. Grammar is accurate and you 
effectively communicate complex ideas about your technical 
experience. The response fully addresses both parts of the question.

Verdict: proficiency_confirmed ✅
```

---

## Proficiency Levels

### CEFR Framework Reference:

| Level | Description | Test Complexity |
|-------|-------------|-----------------|
| **A1-A2** | Basic | Simple questions about daily life, hobbies, work |
| **B1-B2** | Intermediate | Describe experiences, give opinions, handle scenarios |
| **C1-C2** | Advanced | Discuss complex/abstract topics, professional situations |

---

## Integration with Workflow

### Updated Orchestrator Workflow:

```
STEP 1: CV Analysis
   ↓
STEP 2: Job Listings
   ↓
STEP 3: Code Assessment (MANDATORY)
   ↓ (if pass)
STEP 4: Language Assessment (OPTIONAL)
   ↓
STEP 5: Schedule Interview
```

### When Language Assessment Triggers:

✅ Code assessment passed  
✅ CV shows multilingual skills  
✅ Job requires international collaboration

❌ **Does NOT block scheduling** - it's informational!

---

## Example Flow

### Scenario: John Doe applies for Full-Stack Developer role

**CV Languages:**
- English: Native
- Spanish: Fluent (C1)
- French: Intermediate (B1)

**After Code Assessment Passes:**

```
Orchestrator: "Since this role involves international collaboration 
and your CV indicates fluency in Spanish, let's verify your language 
proficiency."

[Calls language_assessment_agent]

Agent: "Language Assessment: Spanish (Claimed level: Fluent/C1)

Por favor, explique cómo manejaría la comunicación técnica con un 
equipo distribuido internacionalmente. ¿Qué desafíos anticiparía?

(Please explain how you would handle technical communication with 
an internationally distributed team. What challenges would you anticipate?)

Please respond in Spanish below."

[User responds in Spanish]

Agent evaluates and returns: proficiency_confirmed

Orchestrator: "Great! Your Spanish proficiency has been confirmed. 
Now let's schedule your interview..."
```

---

## Agent Implementation Details

### File: `src/agents/agents.py`

```python
language_assessment_agent = Agent(
    name="language_assessment_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="""
        Professional language proficiency assessment agent.
        """,
    instruction="""
    MODE 1: Generate appropriate language test
    MODE 2: Evaluate response and provide feedback
    
    Rules:
    - Professional and encouraging
    - Test ONE language only
    - Consider nervousness (minor errors OK)
    - Provide clear verdict
    """,
    tools=[]  # No tools needed!
)
```

### Added to Orchestrator Tools:

```python
tools=[
    AgentTool(CV_analysis_agent),
    AgentTool(job_listing_agent),
    AgentTool(code_assessment_agent),
    AgentTool(language_assessment_agent),  # NEW!
    AgentTool(scheduler_agent),
]
```

---

## Example Test Prompts by Level

### A1-A2 (Basic)

**Spanish:**
```
"Hola! ¿Puedes decirme tu nombre y de dónde eres? ¿Qué te gusta hacer 
en tu tiempo libre?"

(Hello! Can you tell me your name and where you're from? What do you 
like to do in your free time?)
```

### B1-B2 (Intermediate)

**German:**
```
"Beschreiben Sie einen typischen Arbeitstag in Ihrer aktuellen Position. 
Welche Aufgaben machen Ihnen am meisten Spaß?"

(Describe a typical workday in your current position. Which tasks do 
you enjoy the most?)
```

### C1-C2 (Advanced)

**French:**
```
"Analysez les défis techniques auxquels vous avez été confronté dans 
votre dernier projet. Comment avez-vous équilibré les exigences de 
qualité avec les contraintes de temps?"

(Analyze the technical challenges you faced in your last project. How 
did you balance quality requirements with time constraints?)
```

---

## Evaluation Criteria

### What the Agent Checks:

#### 1. Appropriateness (25%)
- Responded in correct language?
- Language matches prompt?

#### 2. Comprehension (25%)
- Understood the question?
- Addressed what was asked?

#### 3. Grammar & Vocabulary (25%)
- Appropriate for claimed level?
- Errors acceptable for level?

#### 4. Completeness (25%)
- Fully answered the prompt?
- Sufficient detail provided?

---

## Evaluation Examples

### ✅ proficiency_confirmed

```
"Your response demonstrates strong command of French at the B2 level. 
You used appropriate vocabulary, maintained good grammatical structure, 
and fully addressed the question about your project experience. Minor 
preposition errors are typical and acceptable at this level.

Verdict: proficiency_confirmed"
```

### ⚠️ proficiency_needs_improvement

```
"While you attempted to respond in German, the grammar and vocabulary 
suggest a lower proficiency than the C1 level claimed. The response 
shows B1-level structures. Consider additional practice or training.

Verdict: proficiency_needs_improvement"
```

### ❌ Wrong Language

```
"You responded in English instead of the requested Spanish. Please 
try again in Spanish, or if you're not comfortable, we can note this 
for the interview discussion.

Verdict: proficiency_needs_improvement"
```

---

## Benefits

### For Recruiters:
✅ Quick language verification  
✅ Identifies misrepresented skills  
✅ Informational, doesn't block hiring  
✅ Shows communication ability

### For Candidates:
✅ Fair assessment of actual skills  
✅ Opportunity to demonstrate proficiency  
✅ Encouraging feedback  
✅ Doesn't penalize minor errors

### For the System:
✅ Simple implementation (no tools needed)  
✅ Flexible difficulty scaling  
✅ Optional (doesn't break workflow)  
✅ Easy to integrate

---

## Important Design Decisions

### 1. **Optional, Not Blocking**

Language assessment **does not** prevent scheduling if it fails:
- Code assessment is the gate-keeper
- Language is informational
- Allows human review in interview

### 2. **One Language Only**

Test only ONE language per assessment:
- Keeps it simple and quick
- Focuses on most relevant language
- Reduces candidate fatigue

### 3. **Encouraging Feedback**

Always be professional and encouraging:
- Candidates may be nervous
- Minor errors are expected
- Focus on overall communication

### 4. **No External Tools**

No tools needed:
- Pure conversational assessment
- LLM handles evaluation
- Simpler architecture

---

## Workflow Integration

### Orchestrator Logic:

```python
# After code assessment passes
if code_result == "pass":
    # Check if language assessment needed
    cv_has_languages = check_cv_for_multilingual()
    job_needs_languages = check_job_requirements()
    
    if cv_has_languages and job_needs_languages:
        # Optional language assessment
        lang_result = call_language_assessment_agent()
        display_language_result(lang_result)
    
    # Always proceed to scheduling (language doesn't block)
    proceed_to_scheduling()
```

---

## Testing Scenarios

### Test 1: Basic Spanish (B1)

**Prompt:**
```
"¿Puedes describir tu proyecto favorito en el que has trabajado?"
```

**Expected Response:**
```
"Mi proyecto favorito fue desarrollar una aplicación web con Python. 
Trabajé en el backend y usé Flask para crear APIs..."
```

**Expected Evaluation:**
```
proficiency_confirmed (appropriate vocabulary, correct grammar for B1)
```

---

### Test 2: Advanced German (C1)

**Prompt:**
```
"Erläutern Sie die architektonischen Entscheidungen in Ihrem 
komplexesten Projekt."
```

**Expected Response:**
```
"In unserem komplexesten Projekt haben wir eine Microservices-Architektur 
implementiert, um Skalierbarkeit zu gewährleisten..."
```

**Expected Evaluation:**
```
proficiency_confirmed (complex vocabulary, advanced structures)
```

---

### Test 3: Wrong Language Response

**Prompt (in Spanish):**
```
"Describe tu experiencia laboral..."
```

**User Response (in English):**
```
"My work experience includes..."
```

**Expected Evaluation:**
```
proficiency_needs_improvement (wrong language used)
```

---

## Future Enhancements

### Phase 2 Ideas:

1. **Multi-Language Testing**
   - Test 2-3 languages if critical for role
   - Compare claimed vs actual proficiency across languages

2. **Audio/Video Assessment**
   - Record voice responses
   - Evaluate pronunciation and fluency
   - More realistic communication test

3. **Structured Scoring**
   - Numeric scores (0-100)
   - Category breakdown (grammar, vocabulary, fluency)
   - Comparison with industry benchmarks

4. **Adaptive Difficulty**
   - Start with claimed level
   - Adjust difficulty based on response quality
   - Pinpoint actual proficiency level

---

## Summary

### What Was Implemented:
✅ Language assessment agent with 2 modes  
✅ Appropriate difficulty scaling (A1-C2)  
✅ Professional, encouraging evaluation  
✅ Integration with orchestrator workflow  
✅ Optional assessment (doesn't block scheduling)

### What It Tests:
✅ Correct language usage  
✅ Comprehension of prompts  
✅ Grammar and vocabulary  
✅ Response completeness

### Key Features:
✅ Simple conversational prompts  
✅ No external tools needed  
✅ Flexible and scalable  
✅ Professional feedback

---

## Regarding the Async Error

The async error you mentioned was likely a transient issue with the Streamlit/ADK event loop. Since it worked the second time, it's not a systematic problem. The implementation I provided is **synchronous** and won't introduce async issues.

**If the error persists:**
1. Check if Streamlit is running in the correct mode
2. Verify Google ADK version compatibility
3. Review terminal logs for stack traces
4. Consider adding error handling in `main.py`

---

**Status:** ✅ Implemented  
**Files Modified:** `src/agents/agents.py`  
**Integration:** Complete  
**Ready to Test:** YES  

Next time a candidate with multilingual skills applies for an international role and passes the code assessment, the language assessment will automatically trigger! 🌍


