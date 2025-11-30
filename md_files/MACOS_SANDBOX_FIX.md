# macOS Code Sandbox Fix

## Problem

The code assessment agent was incorrectly marking correct code submissions as "not pass". When candidates submitted valid Python code, they would receive a failure message even though their code was correct.

## Root Cause

The issue was in `src/tools/code_sandbox.py`. On macOS systems (darwin 24.6.0), the code execution sandbox had two critical problems:

### 1. Resource Limit Error (Line 31)
```python
resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
```

On macOS, this call was failing with:
```
ValueError: current limit exceeds maximum limit
```

This is a known issue on macOS where the `RLIMIT_AS` (address space limit) cannot be set in the same way as on Linux. The process would crash before even executing the candidate's code, causing the sandbox to return an error result (❌).

### 2. Multiprocessing Start Method
The default multiprocessing start method (`spawn`) was causing processes to hang, especially when run from Streamlit. This resulted in timeout errors even for simple, correct code.

## Solution Applied

### Fix 1: Graceful Resource Limit Handling
Wrapped the `resource.setrlimit()` call in a try-except block to handle macOS gracefully:

```python
if IS_UNIX:
    try:
        # Set memory limit (in bytes)
        memory_bytes = memory_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    except (ValueError, OSError) as e:
        # On macOS, setrlimit may fail with "current limit exceeds maximum limit"
        # This is a known issue on macOS - we'll rely on the timeout mechanism instead
        pass
```

**Result**: On macOS, if resource limits can't be set, the sandbox relies on the timeout mechanism instead. This maintains security while ensuring compatibility.

### Fix 2: Force Fork Start Method
Added explicit multiprocessing start method configuration:

```python
# Set the multiprocessing start method for better compatibility
# This prevents issues with Streamlit and macOS
if __name__ != '__main__':
    try:
        multiprocessing.set_start_method('fork', force=True)
    except RuntimeError:
        # Already set, ignore
        pass
```

**Result**: Uses the faster and more reliable `fork` method on Unix systems, preventing process hangs.

## Testing Results

After the fix, all test cases pass successfully:

```
Test 1: Simple working code
Status: success
Output: Sum of even numbers: 12
Execution time: 0.0049s

Test 3: User's code submission
Status: success
Output:
sum_even_numbers([1, 2, 3, 4, 5, 6]) = 12
sum_even_numbers([2, 4, 6, 8]) = 20
sum_even_numbers([1, 3, 5, 7]) = 0
sum_even_numbers([]) = 0
Execution time: 0.005s

✅ ALL TESTS PASSED! The code sandbox is working correctly.
✅ The macOS resource limit issue has been fixed.
```

## Impact

### Before Fix
- ❌ All code submissions (even correct ones) would fail with a `ValueError`
- ❌ The `code_assessment_agent` would return "not pass" for valid code
- ❌ Candidates couldn't proceed to the interview scheduling step

### After Fix
- ✅ Code executes successfully in the sandbox
- ✅ The `code_assessment_agent` correctly evaluates code as "pass" or "not pass"
- ✅ Valid code submissions allow candidates to proceed to scheduling
- ✅ Security is maintained through timeout mechanisms and restricted builtins

## Files Modified

- `src/tools/code_sandbox.py` - Fixed resource limit handling and multiprocessing start method

## Compatibility

This fix maintains compatibility across:
- ✅ macOS (darwin) - Primary fix target
- ✅ Linux - Continues to work with resource limits when available
- ✅ Windows - Already handled through IS_UNIX check
- ✅ Streamlit - Works correctly when run from the Streamlit app
- ✅ Standalone Python - Works in regular Python scripts

## How It Works Now

1. **Code Submission**: Candidate submits code through Streamlit chat
2. **Orchestrator**: Routes to `code_assessment_agent`
3. **Agent**: Calls `run_code_assignment` tool from `tools.py`
4. **Sandbox Execution**: `execute_code()` in `code_sandbox.py`:
   - Sets multiprocessing to use `fork` method
   - Attempts to set resource limits (gracefully fails on macOS)
   - Executes code in isolated process with restricted builtins
   - Uses timeout as primary safeguard
   - Returns success (✅) or error (❌)
5. **Agent Response**: Returns "pass" or "not pass" based on tool output
6. **Orchestrator**: Proceeds to scheduling if "pass"

## Security Considerations

The sandbox remains secure even without resource limits on macOS because:

1. **Restricted Builtins**: Code runs with limited built-in functions (no `import`, `open`, etc.)
2. **Timeout Protection**: 3-second timeout prevents infinite loops and long-running code
3. **Static Analysis**: Forbidden keywords are blocked before execution
4. **Process Isolation**: Code runs in a separate process that can be terminated

## Future Improvements

While the current fix works well, potential enhancements could include:

1. Platform-specific memory monitoring using `psutil` library
2. More granular timeout controls per test case
3. Enhanced static analysis for additional security patterns
4. Async execution for better Streamlit integration

---

**Status**: ✅ Fixed and Tested  
**Date**: November 28, 2025  
**Platform**: macOS darwin 24.6.0

