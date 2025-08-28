import subprocess
import os
import sys
from config import TEST_CASES_DIR, LOGS_DIR
from datetime import datetime
import logging
import re  # Add this import

logger = logging.getLogger('TestExecutor')

def execute_test(test_code, test_name):
    """
    Execute the generated test code and return results
    """
    # The test code is already saved by test_generator.py
    # Find the latest test file for this test name
    test_files = [f for f in os.listdir(TEST_CASES_DIR) 
                 if f.startswith(f"test_{test_name.lower().replace(' ', '_')}")]
    
    if not test_files:
        logger.error(f"No test file found for {test_name}")
        return "ERROR", "Test file not found", "", ""
    
    # Get the most recent file
    test_files.sort(reverse=True)
    test_file = os.path.join(TEST_CASES_DIR, test_files[0])
    
    # Set up log file - FIXED: Add proper timestamp variable
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(LOGS_DIR, f"test_{test_name}_{timestamp}.log")
    
    try:
        # Run the test using subprocess
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            timeout=300  # 5 minute timeout
        )
        
        # Save log output
        with open(log_file, 'w') as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\nSTDERR:\n")
            f.write(result.stderr)
        
        # Determine status
        status = "PASS" if result.returncode == 0 else "FAIL"
        output = result.stderr if result.stderr else result.stdout
        
        # Find screenshot path from output using regex for better reliability
        screenshot_path = ""
        screenshot_match = re.search(r"Screenshot saved to:\s*(.+)", output)
        if screenshot_match:
            screenshot_path = screenshot_match.group(1).strip()
        
        logger.info(f"Test execution completed with status: {status}")
        return status, output, test_file, screenshot_path
        
    except subprocess.TimeoutExpired:
        error_msg = "Test execution timed out after 5 minutes"
        logger.error(error_msg)
        return "TIMEOUT", error_msg, test_file, ""
    except Exception as e:
        error_msg = f"Error executing test: {str(e)}"
        logger.error(error_msg)
        return "ERROR", error_msg, test_file, ""