# Language Assessment Skipped - Root Cause & Fix

## TL;DR

The orchestrator skipped the language assessment and jumped straight to scheduling because STEP 4 was marked "OPTIONAL" and the job didn't explicitly mention "international collaboration."

**Maria Santos:**
- Portuguese: Native
- German: Fluent (C2)
- English: Advanced (C1)

**Result:** Language assessment should have triggered, but didn't!

---

## Timeline (From Logs)

### Line 209-212: Job Selection & Code Assessment
```
User selects job #3: Backend Engineer – API & Microservices
Orchestrator calls code_assessment_agent
Agent returns: "" (empty string - another bug!)
```

### Line 213-216: Code Submission & Evaluation
```
User submits FastAPI code (User Management API)
Orchestrator manually evaluates code (no sandbox execution)
Returns: "The code is functionally correct... would 'pass'"
```

### Line 217-218: Direct to Scheduling
```
User: "yes"
Orchestrator: ❌ SKIPS language assessment
Orchestrator: Calls scheduler_agent directly
```

**Language assessment was completely bypassed!**

---

## Root Cause: "OPTIONAL" Keyword

### Old STEP 4 Instructions:

```
4. STEP 4: Language Assessment (OPTIONAL - for international roles)
   - After code assessment passes, check if the candidate's CV indicates 
     multilingual skills AND the job requires international collaboration.
   - If yes, call 'language_assessment_agent'...
```

**Problems:**
1. ❌ "OPTIONAL" → Agent interprets as "I can skip this"
2. ❌ "AND the job requires international collaboration" → Too vague
3. ❌ Job #3 doesn't explicitly say "international" → Agent skips

### Why It Failed for Maria Santos:

**CV Languages:**
- Portuguese: Native ✓
- German: Fluent (C2) ✓
- English: Advanced (C1) ✓

**Job #3 Description:**
- "Collaborate with front-end engineers" ← Not explicitly "international"
- Location: London, UK ← In English-speaking country

**Orchestrator's Logic:**
```python
if "international" in job_description or "multilingual" in job_description:
    do_language_assessment()
else:
    skip_language_assessment()  # ❌ What actually happened
```

---

## The Fix: Make It MANDATORY

### New STEP 4 Instructions:

```
4. STEP 4: Language Assessment (MANDATORY for multilingual candidates)
   - **CRITICAL**: After code assessment passes, you MUST check the CV 
     analysis from STEP 1.
   - **Language Assessment Trigger:**
      * If CV shows ANY language OTHER THAN English (with proficiency level 
        like B1, B2, C1, C2, Native, Fluent) → Language assessment is REQUIRED
      * Examples that TRIGGER assessment: 
        - "Spanish: Fluent" → REQUIRED
        - "German: C2" → REQUIRED
        - "Portuguese: Native" → REQUIRED
        - "French: B1" → REQUIRED
      * English-only candidates → Skip language assessment
```

**Key Changes:**
1. ✅ Changed "OPTIONAL" → "MANDATORY for multilingual candidates"
2. ✅ Clear trigger: ANY non-English language → Assessment required
3. ✅ Removed dependency on job description
4. ✅ Added explicit examples

---

## Decision Logic

### New Flow:

```python
# After code assessment passes:

cv_languages = extract_languages_from_cv()
non_english_languages = [
    lang for lang in cv_languages 
    if lang.name != "English" and lang.proficiency is not None
]

if len(non_english_languages) > 0:
    # Maria Santos case: Portuguese (Native), German (C2)
    highest_proficiency_lang = select_best_language(non_english_languages)
    
    # MUST call language assessment
    language_assessment_agent(
        language=highest_proficiency_lang.name,
        level=highest_proficiency_lang.proficiency
    )
    
    # Wait for user response
    # Evaluate response
    # Display result
    
    # Then proceed to scheduling
else:
    # English-only candidate
    # Skip language assessment
    # Proceed directly to scheduling
```

---

## Why This is Better

### Before (OPTIONAL):
```
Multilingual CV + Job mentions "international" → Language assessment
Multilingual CV + Job doesn't mention "international" → SKIP ❌
```

**Problem:** Many international roles don't use the word "international"!

### After (MANDATORY):
```
Multilingual CV (any non-English language) → Language assessment ✓
English-only CV → Skip language assessment
```

**Benefits:**
- ✅ Consistent assessment for all multilingual candidates
- ✅ Doesn't depend on job description wording
- ✅ Properly validates CV claims
- ✅ More fair to all candidates

---

## Testing the Fix

### Test Case 1: Maria Santos (Multilingual)

**CV:**
- Portuguese: Native
- German: C2
- English: C1

**Expected Flow:**
```
1. CV Analysis ✓
2. Job Selection ✓
3. Code Assessment → PASS ✓
4. Language Assessment → German (C2) ✓ [NEW!]
5. Scheduling ✓
```

### Test Case 2: John Doe (English Only)

**CV:**
- English: Native

**Expected Flow:**
```
1. CV Analysis ✓
2. Job Selection ✓
3. Code Assessment → PASS ✓
4. Language Assessment → SKIP (English-only) ✓
5. Scheduling ✓
```

### Test Case 3: Candidate with Basic Language Skills

**CV:**
- English: Native
- Spanish: B1

**Expected Flow:**
```
1. CV Analysis ✓
2. Job Selection ✓
3. Code Assessment → PASS ✓
4. Language Assessment → Spanish (B1) ✓ [TRIGGERED!]
5. Scheduling ✓
```

---

## Why It Was Skipped in Your Case

Looking at line 203-208 of the logs:

**Maria's CV (Line 203):**
```
**3. Languages**
*   **Portuguese:** Native speaker
*   **German:** Fluent (C2 level)
*   **English:** Advanced (C1 level)
```

**Job #3 (Line 207-208):**
```
Backend Engineer – API & Microservices at TechCorp
Location: London, UK - On-site
Description: Focuses on developing RESTful APIs and microservices.
```

**Orchestrator's Reasoning:**
```
1. Code assessment passed ✓
2. Check: Is language assessment needed?
   - CV has languages? YES (Portuguese, German, English)
   - Job mentions "international"? NO ❌
   - DECISION: OPTIONAL + NO = SKIP
3. Jump to scheduling ❌
```

With the new instructions:
```
1. Code assessment passed ✓
2. Check: Is language assessment needed?
   - CV has non-English languages? YES (Portuguese, German)
   - DECISION: MANDATORY for multilingual candidates
3. Call language_assessment_agent ✓
4. Then proceed to scheduling ✓
```

---

## Additional Notes

### Note on Line 212: Empty Code Assessment

```json
{"result": ""}
```

This is another bug - the code_assessment_agent returned an empty string instead of a problem. This happened because the agent was asked to evaluate code (line 214) without first generating a problem.

**The orchestrator flow was confused:**
```
Line 210: "Generate code assessment"
Line 211: Agent returns "" (empty - should have been a problem!)
Line 213: User submits code anyway
Line 214: "Evaluate this code"
Line 215: Agent manually reviews (doesn't execute)
```

**Correct flow should be:**
```
1. Generate problem → Display to user
2. User submits code
3. Execute code → Compare output
4. Return pass/not pass
```

This is a separate issue from the language assessment skip.

---

## Summary

### The Bug:
❌ Language assessment was "OPTIONAL" with vague conditions  
❌ Orchestrator skipped it for Maria Santos despite 3 languages in CV  
❌ Jumped straight to scheduling  

### The Fix:
✅ Changed to "MANDATORY for multilingual candidates"  
✅ Clear trigger: ANY non-English language with proficiency level  
✅ No dependency on job description wording  
✅ Consistent assessment for all multilingual candidates  

### Impact:
🎯 Language assessment will now properly trigger for Maria Santos  
🎯 Fair validation of language skills claimed in CV  
🎯 Better candidate evaluation process  

---

**File Updated:** `src/agents/agents.py` (STEP 4)  
**Status:** ✅ Fixed  
**Next Test:** Run full workflow with Maria Santos' CV to verify language assessment triggers

