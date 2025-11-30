# UX Improvement: Explicit Constraint Communication

## The Question

*"Should the agent specify WHAT SHOULD NOT BE IN THE CODE? Like, 'DO NOT WRITE IMPORTS' or something like that to avoid incurring in invalid answers or just ask to rewrite the solution without imports?"*

## Answer: YES - Be Explicit! ✅

### Why Explicit Communication is Better

#### ❌ Bad UX (Implicit Constraints):
```
Assignment:
"Write a function that processes data..."

[User submits code with imports]

Result: "not pass"
```

**Problems:**
- User doesn't know WHY they failed
- Wastes time writing "correct" code that violates hidden rules
- Frustrating experience
- Feels unfair

---

#### ✅ Good UX (Explicit Constraints):
```
Assignment:
"Write a function that processes data..."

**CONSTRAINTS:**
- DO NOT use any import statements (no libraries allowed)
- Only use Python built-in functions: print, range, len, sum, min, max...
- Your code will run in a restricted sandbox environment

[User knows the rules and writes code accordingly]

Result: Fair evaluation
```

**Benefits:**
- Clear expectations upfront
- No wasted attempts on invalid approaches
- Fair and transparent assessment
- Professional experience

---

## Implementation

### Updated code_assessment_agent Instructions

**Added mandatory constraint block:**

```python
- After generating the assignment problem, you MUST include this exact warning at the end:
  
  **CONSTRAINTS:**
  - DO NOT use any import statements (no libraries allowed)
  - Only use Python built-in functions: print, range, len, sum, min, max, 
    abs, round, int, str, list, dict, tuple, set, float, bool, sorted, 
    enumerate, zip
  - Your code will run in a restricted sandbox environment
  
- Then ask the user to submit their code.
```

---

## Example Assignments (Before vs After)

### Before (Implicit Constraints) ❌

```
**Problem:**
Write a function that calculates the dot product of two vectors.

Please submit your code.
```

**User might write:**
```python
import numpy as np

def dot_product(v1, v2):
    return np.dot(v1, v2)
```

**Result:** "not pass" (User confused why!)

---

### After (Explicit Constraints) ✅

```
**Problem:**
Write a function that calculates the dot product of two vectors (represented 
as lists). Return the sum of element-wise products.

Example:
Input: [1, 2, 3], [4, 5, 6]
Output: 32  (1*4 + 2*5 + 3*6)

**CONSTRAINTS:**
- DO NOT use any import statements (no libraries allowed)
- Only use Python built-in functions: print, range, len, sum, min, max, 
  abs, round, int, str, list, dict, tuple, set, float, bool, sorted, 
  enumerate, zip
- Your code will run in a restricted sandbox environment

Please submit your code.
```

**User writes:**
```python
def dot_product(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))

# Test
result = dot_product([1, 2, 3], [4, 5, 6])
print(f"Dot product: {result}")
```

**Result:** "pass" ✅ (User knew the rules!)

---

## UX Principles Applied

### 1. **Transparency**
- Users see all constraints upfront
- No hidden rules or gotchas
- Clear expectations

### 2. **Fairness**
- Everyone gets the same information
- No advantage for those who "figure out" the rules
- Assessment tests coding skills, not mind-reading

### 3. **Error Prevention**
- Prevents wasted time on invalid approaches
- Reduces frustration
- Better candidate experience

### 4. **Professional Standards**
- Mirrors real technical interviews
- Shows respect for candidate's time
- Builds trust in the process

---

## Alternative Approach (Not Recommended)

### ❌ Let them fail first, then ask to rewrite:

```
User: [submits code with imports]
Agent: "Your code uses imports which are not allowed. Please rewrite without imports."
User: [rewrites code]
```

**Why this is worse:**
- Wastes user's time
- Creates negative experience
- Feels like a "gotcha"
- Multiple back-and-forth cycles
- Unprofessional

**When it might be acceptable:**
- If this is explicitly part of the test (testing adaptability)
- If you want to see how candidates handle feedback
- Educational context where learning from mistakes is the goal

**But for job screening:** Always be explicit upfront! ✅

---

## Real-World Comparison

### Technical Interview Best Practices:

**Good Interviewer:**
```
"Write a function to reverse a string. You cannot use built-in 
reverse functions - implement it yourself."
```
✅ Clear constraints upfront

**Bad Interviewer:**
```
"Write a function to reverse a string."
[Candidate uses built-in reverse]
"No, you can't use that."
```
❌ Hidden gotcha

---

## Impact on User Flow

### Complete User Experience:

1. **Upload CV** → See full analysis
2. **Select job** → See all job details
3. **Receive assessment:**
   ```
   Problem: [Clear problem statement]
   
   Example: [Input/output example]
   
   CONSTRAINTS: [Clear list of what's allowed/forbidden]
   
   Submit your code.
   ```
4. **Submit code** → Fair evaluation
5. **Pass** → Schedule interview OR **Not pass** → Clear reason

---

## Summary

### What We Changed:

**Before:**
- Agent knew constraints internally
- Users had to guess or discover through failure

**After:**
- Agent displays constraints in every assignment
- Users know the rules before writing code

### Why It's Better:

✅ **Transparent** - No hidden rules  
✅ **Fair** - Everyone gets same information  
✅ **Efficient** - No wasted attempts  
✅ **Professional** - Mirrors real interview standards  
✅ **Respectful** - Values candidate's time  

### The Key Insight:

**Always optimize for user experience, not agent convenience.**

If there's a constraint that affects whether code passes or fails, **tell the user upfront!**

---

**Status:** ✅ Implemented  
**File Modified:** `src/agents/agents.py`  
**UX Impact:** High - Significantly improves candidate experience

