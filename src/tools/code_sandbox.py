import multiprocessing
import sys
import io
import contextlib
import time
import traceback
import re
import platform

# Set the multiprocessing start method for better compatibility
# This prevents issues with Streamlit and macOS/Linux
# Windows only supports 'spawn', Unix systems can use 'fork'
if __name__ != '__main__':
    try:
        if platform.system() in ('Darwin', 'Linux'):
            # macOS and Linux: use 'fork' for better performance and Streamlit compatibility
            multiprocessing.set_start_method('fork', force=True)
        # Windows will use its default 'spawn' method
    except RuntimeError:
        # Already set, ignore
        pass

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
        try:
            # Set memory limit (in bytes)
            memory_bytes = memory_limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        except (ValueError, OSError) as e:
            # On macOS, setrlimit may fail with "current limit exceeds maximum limit"
            # This is a known issue on macOS - we'll rely on the timeout mechanism instead
            pass
        
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
    except Exception as e:
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