import multiprocessing
import sys
import io
import contextlib
import time
import traceback
import re

# --- Resource limiting (Unix-based systems only) ---
try:
    import resource
    IS_UNIX = True
except ImportError:
    IS_UNIX = False
    print("Warning: 'resource' module not found. Memory and CPU time limits are not available on this OS (e.g., Windows).")

# --- Configuration ---
DEFAULT_TIMEOUT_SECONDS = 3  
DEFAULT_MEMORY_LIMIT_MB = 128 # Default memory limit in Megabytes

def _unsafe_execute(code, return_dict, memory_limit_mb):
    """
    Internal function running inside the separate process.
    Captures stdout, handles execution scope, and sets resource limits.
    """
    
    # --- Set Resource Limits (if on Unix) ---
    if IS_UNIX:
        # Set memory limit (in bytes)
        memory_bytes = memory_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        
        # CPU time limit is an additional safeguard against complex computations
        # that aren't simple infinite loops. The p.join() timeout is still the primary guard.
        # resource.setrlimit(resource.RLIMIT_CPU, (TIMEOUT_SECONDS, TIMEOUT_SECONDS))

    output_capture = io.StringIO()
    
    try:
        # Capture stdout/print statements
        with contextlib.redirect_stdout(output_capture):
            # Execute code with a richer but still safe set of globals
            # IMPLEMENTATION of the comment "# We can add more safe functions here"
            safe_builtins = {
                "print": print, "range": range, "len": len, "sum": sum,
                "min": min, "max": max, "abs": abs, "round": round,
                "int": int, "str": str, "list": list, "dict": dict, 
                "tuple": tuple, "set": set, "float": float, "bool": bool,
                "sorted": sorted, "enumerate": enumerate, "zip": zip
            }
            safe_globals = {"__builtins__": safe_builtins}
            exec(code, safe_globals)
            
        return_dict["output"] = output_capture.getvalue()
        return_dict["status"] = "success"
        
    except MemoryError:
        return_dict["output"] = output_capture.getvalue()
        return_dict["status"] = "memory_error"
        return_dict["error_msg"] = f"Memory usage exceeded the limit of {memory_limit_mb}MB."
    except Exception:
        return_dict["output"] = output_capture.getvalue()
        return_dict["status"] = "error"
        return_dict["error_msg"] = traceback.format_exc()

def execute_code(code_string: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    """
    THE MAIN TOOL: Called by the Agent.
    Manages the Sandbox (Process), Timeout logic, and Resource Limits.
    
    Args:
        code_string (str): The Python code to execute.
        timeout (int): The maximum execution time in seconds.
        
    Returns:
        dict: Contains 'status', 'output', 'error_msg', and 'execution_time'.
    """
    
    # 1. Improved Security Scan (static check for obvious malicious keywords)
    # This is a fast-path rejection. The primary security comes from the restricted __builtins__.
    forbidden_keywords = ["import", "os", "sys", "subprocess", "open", "input", "eval", "exec"]
    # Use regex to find whole words to avoid false positives on variable names
    for keyword in forbidden_keywords:
        if re.search(r'\b' + keyword + r'\b', code_string):
            return {
                "status": "security_violation", 
                "output": f"Forbidden keyword detected: '{keyword}'",
                "error_msg": "Security Policy Violation: Use of potentially unsafe keywords is not allowed.",
                "execution_time": 0.0
            }

    # 2. Prepare the separate Process
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    
    # Create the Process (the "sandbox environment")
    p = multiprocessing.Process(target=_unsafe_execute, args=(code_string, return_dict, DEFAULT_MEMORY_LIMIT_MB))
    
    # 3. Execution and Time Monitoring
    start_time = time.time()
    p.start()
    
    # Wait for the Process to finish for X seconds
    p.join(timeout)
    
    execution_time = round(time.time() - start_time, 4)

    # 4. Check: Did it finish or get stuck?
    if p.is_alive():
        p.terminate()
        p.join()
        return {
            "status": "timeout",
            "output": "",
            "error_msg": f"Code execution exceeded the {timeout} seconds time limit.",
            "execution_time": execution_time
        }

    # 5. Return Results
    result = {
        "status": return_dict.get("status", "unknown_error"),
        "output": return_dict.get("output", "").strip(),
        "error_msg": return_dict.get("error_msg", None),
        "execution_time": execution_time
    }
    
    return result

# ==========================================
# TESTING SECTION (Local Verification)
# ==========================================
if __name__ == "__main__":
    print("🧪 --- Starting Sandbox Tests --- \n")

    # TEST CASE 1: Success (Valid Logic)
    print("🔹 Test 1: Valid Python Code (Fibonacci)")
    valid_code = """
def fib(n):
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result
print(f"Fibonacci sequence (10): {fib(10)}")
"""
    result1 = execute_code(valid_code)
    print(f"Result: {result1}\n")

    # TEST CASE 2: Security Violation (Malicious Import)
    print("🔹 Test 2: Security Check (Import OS)")
    malicious_code = "import os\nprint(os.listdir())"
    result2 = execute_code(malicious_code)
    print(f"Result: {result2}\n")

    # TEST CASE 3: Resilience (Infinite Loop / Timeout)
    print("🔹 Test 3: Timeout Check (Infinite Loop)")
    loop_code = "while True: pass"
    result3 = execute_code(loop_code, timeout=2) # Test with custom timeout
    print(f"Result: {result3}\n")

    # TEST CASE 4: NEW - Memory Bomb
    if IS_UNIX:
        print("🔹 Test 4: Memory Limit Check (Memory Bomb)")
        memory_bomb_code = "huge_list = [0] * (200 * 1024 * 1024) # Try to allocate 200MB"
        result4 = execute_code(memory_bomb_code)
        print(f"Result: {result4}\n")
    else:
        print("🔹 Test 4: Memory Limit Check - SKIPPED (not on a Unix-like system)\n")
        
    # TEST CASE 5: NEW - Allowed Built-ins
    print("🔹 Test 5: Check allowed built-ins (float, sorted)")
    allowed_code = "print(sorted([3.14, 1.0, 2.5]))"
    result5 = execute_code(allowed_code)
    print(f"Result: {result5}\n")
    
    print("✅ --- Tests Completed ---")
