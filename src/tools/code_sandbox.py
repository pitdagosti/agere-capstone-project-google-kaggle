import multiprocessing
import sys
import io
import contextlib
import time
import traceback

# --- Configuration ---
TIMEOUT_SECONDS = 3  

def _unsafe_execute(code, return_dict):
    """
    Internal function running inside the separate process.
    Captures stdout and handles execution scope.
    """
    output_capture = io.StringIO()
    
    try:
        # Capture stdout/print statements
        with contextlib.redirect_stdout(output_capture):
            # Execute code with restricted globals (no import os, etc.)
            safe_globals = {"__builtins__": {
                "print": print, 
                "range": range, 
                "len": len, 
                "int": int, 
                "str": str, 
                "list": list,
                "sum": sum,
                "min": min,
                "max": max,
                "abs": abs
                # We can add more safe functions here
            }}
            exec(code, safe_globals)
            
        return_dict["output"] = output_capture.getvalue()
        return_dict["status"] = "success"
        
    except Exception:
        return_dict["output"] = output_capture.getvalue()
        return_dict["status"] = "error"
        return_dict["error_msg"] = traceback.format_exc()

def execute_code(code_string: str) -> dict:
    """
    THE MAIN TOOL: Called by the Agent.
    Manages the Sandbox (Process) and Timeout logic.
    
    Args:
        code_string (str): The Python code to execute.
        
    Returns:
        dict: Contains 'status', 'output', 'error_msg', and 'execution_time'.
    """
    
    # 1. Security Scan (static check for obvious malicious imports)
    forbidden = ["import os", "import sys", "subprocess", "open(", "input("]
    for term in forbidden:
        if term in code_string:
            return {
                "status": "security_violation", 
                "output": f"Forbidden term detected: '{term}'",
                "error_msg": "Security Policy Violation",
                "execution_time": 0.0
            }

    # 2. Prepare the separate Process
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    
    # Create the Process (the "sandbox environment")
    p = multiprocessing.Process(target=_unsafe_execute, args=(code_string, return_dict))
    
    # 3. Execution and Time Monitoring
    start_time = time.time()
    p.start()
    
    # Wait for the Process to finish for X seconds
    p.join(TIMEOUT_SECONDS)
    
    execution_time = round(time.time() - start_time, 4)

    # 4. Check: Did it finish or get stuck?
    if p.is_alive():
        # If it is still alive, it means it's stuck (Infinite Loop). TERMINATE IT.
        p.terminate()
        p.join()
        return {
            "status": "timeout",
            "output": "",
            "error_msg": f"Code execution exceeded {TIMEOUT_SECONDS} seconds limit.",
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
    for _ in range(n):
        a, b = b, a + b
    return a
print(f"Fibonacci(10) is: {fib(10)}")
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
    loop_code = """
total = 0
while True:
    total += 1
"""
    result3 = execute_code(loop_code)
    print(f"Result: {result3}\n")
    
    print("✅ --- Tests Completed ---")