import os
from config import TEST_CASES_DIR
from datetime import datetime
import logging

logger = logging.getLogger('TestGenerator')

def generate_test_code(parsed_instruction):
    """
    Generate executable Python test code from parsed instruction
    """
    test_name = parsed_instruction['test_name'].lower().replace(' ', '_')
    steps_code = generate_steps_code(parsed_instruction['steps'])
    
    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    test_code = f"""
import os
import sys
from datetime import datetime
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import HEADLESS, BROWSER, IMPLICIT_WAIT

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_{test_name}():
    # Setup browser options
    if BROWSER.lower() == "chrome":
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = Options()
        if HEADLESS:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Auto-handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    elif BROWSER.lower() == "firefox":
        from selenium.webdriver.firefox.options import Options
        from selenium.webdriver.firefox.service import Service
        from webdriver_manager.firefox import GeckoDriverManager

        options = Options()
        if HEADLESS:
            options.add_argument("--headless")
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

    else:
        raise ValueError(f"Unsupported browser: {{BROWSER}}")

    driver.implicitly_wait(IMPLICIT_WAIT)
    test_status, error_message, screenshot_path = "PASS", "", ""

    try:
        # Test steps
        {steps_code}

        print("Test passed successfully.")

    except Exception as e:
        test_status = "FAIL"
        error_message = str(e)
        print(f"Test failed with error: {{error_message}}")

        # Take screenshot on failure
        screenshot_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshots_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        screenshot_path = os.path.join(screenshots_dir, f"{test_name}_{{screenshot_timestamp}}.png")
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved to: {{screenshot_path}}")

        raise

    finally:
        driver.quit()
        return test_status, error_message, screenshot_path

if __name__ == "__main__":
    status, error, screenshot = test_{test_name}()
    print(f"Test Status: {{status}}")
    if error:
        print(f"Error: {{error}}")
"""
    
    # Save the generated code to a file
    filename = f"test_{test_name}_{timestamp}.py"
    filepath = os.path.join(TEST_CASES_DIR, filename)

    with open(filepath, 'w', encoding="utf-8") as f:
        f.write(test_code)

    logger.info(f"Generated test code saved to: {filepath}")
    return test_code, filepath


def generate_steps_code(steps):
    """Generate Python code for each test step"""
    steps_code = []
    for i, step in enumerate(steps):
        action = step.get('action', '')

        if action == 'navigate':
            url = step.get('url', '')
            step_code = f"driver.get('{url}')"

        elif action == 'click':
            by = step.get('by', 'id').upper()
            locator = step.get('locator', '')
            step_code = f"driver.find_element(By.{by}, '{locator}').click()"

        elif action == 'input':
            by = step.get('by', 'id').upper()
            locator = step.get('locator', '')
            text = step.get('text', '')
            step_code = f"driver.find_element(By.{by}, '{locator}').send_keys('{text}')"

        elif action == 'verify':
            by = step.get('by', 'id').upper()
            locator = step.get('locator', '')
            expected = step.get('expected', '')
            step_code = f"""
element = driver.find_element(By.{by}, '{locator}')
assert '{expected}' in element.text, f"Verification failed. Expected: {expected}, Got: {{element.text}}"
            """.strip()

        elif action == 'wait':
            by = step.get('by', 'id').upper()
            locator = step.get('locator', '')
            timeout = step.get('timeout', 10)
            step_code = f"""
try:
    element = WebDriverWait(driver, {timeout}).until(
        EC.presence_of_element_located((By.{by}, '{locator}'))
    )
    print("Element found: {locator}")
except TimeoutException:
    raise TimeoutException(f"Element not found within {timeout} seconds: {locator}")
            """.strip()
        else:
            step_code = f'print("Unknown action: {action}")'

        # Append step
        steps_code.append(f"# Step {i+1}: {action}")
        steps_code.append(step_code)

    return "\n        ".join(steps_code)
