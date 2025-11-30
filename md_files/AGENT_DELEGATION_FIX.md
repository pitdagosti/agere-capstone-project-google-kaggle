# Agent Delegation Fix - Force Orchestrator to Use code_evaluator_agent

## Problem Identified

Despite the orchestrator having instructions that say "[MANDATORY] call 'code_evaluator_agent'", the LLM was still calling `run_code_assignment` directly.

### Root Cause

The orchestrator has access to BOTH:
1. `code_execution_tool` (direct function tool)
2. `code_evaluator_agent` (agent wrapper)

When LLMs have direct access to a tool, they prefer it over delegating to an agent - it's a "shortcut" behavior even when instructions say not to.

---

## Solution Applied

### Enhanced Instructions with Explicit FORBID

**PHASE 1 - Step 2** (lines 431-439):
```
**Step 2**: IMMEDIATELY call `run_code_assignment` to store the expected output (SETUP ONLY)
- **CRITICAL**: This is the ONLY time you use `run_code_assignment` directly. 
  You will NEVER call it again in this workflow.
- [mappings...]
- After this, you are DONE with `run_code_assignment`. Do NOT call it again.
```

**PHASE 2** (lines 444-457):
```
**PHASE 2: Evaluate Submission**
- When user submits code, YOU MUST ONLY call 'code_evaluator_agent' 
  (NOT run_code_assignment directly).
- **CRITICAL RULE**: You are FORBIDDEN from calling 'run_code_assignment' 
  with user code. Only 'code_evaluator_agent' can evaluate user code.
- Pass the user's complete code to the agent: 
  `code_evaluator_agent(request="<user's complete code>")`
```

---

## Why This Approach

1. **Clear Boundaries**: Explicitly states when to use direct tool (setup only)
2. **Forbidden Language**: Uses "FORBIDDEN" not just "mandatory" 
3. **Positive Guidance**: Shows exact syntax for correct agent call
4. **Consequences Stated**: "You will NEVER call it again"

---

## Expected Behavior Now

### Old Flow (Bypassing Agent)
```
1. User submits code
2. Orchestrator calls run_code_assignment(code=user_code) ❌
3. Tool returns "✅ Code executed successfully!"
4. Orchestrator says "passed"
```

### New Flow (Using Agent)
```
1. User submits code
2. Orchestrator calls code_evaluator_agent(request=user_code) ✅
3. Agent calls run_code_assignment(code=user_code) internally
4. Agent analyzes tool response
5. Agent returns "pass" or "not pass"
6. Orchestrator displays clear result
```

---

## Benefits

1. **Consistent Pass/Fail Logic**: Agent handles all evaluation
2. **Better Error Handling**: Agent can provide detailed feedback
3. **Cleaner Separation**: Orchestrator coordinates, agent evaluates
4. **Easier Maintenance**: Change evaluation logic in one place

---

## Alternative Solution (If This Doesn't Work)

If the LLM still ignores the instructions, remove `code_execution_tool` from orchestrator's tool list and create a separate wrapper for setup:

```python
# New wrapper tool
def setup_code_assessment(job_category: str, context: Any = None):
    expected_outputs = {
        "backend": "600\n3600\n0\n0\n1000",
        "data": "{'sum': 15...}",
        # etc
    }
    return run_code_assignment(code="# Setup", 
                               expected_output=expected_outputs.get(job_category))

# Orchestrator tools (line 505-513)
tools=[
    AgentTool(CV_analysis_agent),
    AgentTool(job_listing_agent),
    problem_presenter_tool,
    setup_assessment_tool,  # New wrapper instead of code_execution_tool
    AgentTool(code_evaluator_agent),
    AgentTool(language_assessment_agent),
    AgentTool(scheduler_agent),
]
```

This makes it **impossible** for orchestrator to call `run_code_assignment` directly since it won't have access to it.

---

## Test Again

Run another test and check `runner_events.log`:

**Look for**:
```json
{"agent_name": "Orchestrator", "tool_name": "code_evaluator_agent", ...}
```

**NOT**:
```json
{"agent_name": "Orchestrator", "tool_name": "run_code_assignment", ...}
```

---

**Status**: Instructions strengthened with FORBIDDEN language ✅

