import json
import openai
from config import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('NLUProcessor')

# Initialize OpenAI client
client = None
if OPENAI_API_KEY and OPENAI_API_KEY != "[Your OpenAI API Key Here]":
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI client: {e}")
        client = None
else:
    logger.warning("OpenAI client not initialized - API key missing or placeholder")

def parse_instruction_fallback(user_prompt):
    """
    Fallback parser for when OpenAI API is not available
    """
    logger.info("Using fallback parser (OpenAI not available)")
    
    # Simple rule-based parser for common commands
    user_prompt_lower = user_prompt.lower()
    
    if "google" in user_prompt_lower:
        return {
            "test_name": "open_google",
            "objective": "Open google.com homepage",
            "steps": [
                {"action": "navigate", "url": "https://www.google.com"}
            ],
            "timestamp": datetime.now().isoformat()
        }
    elif "wikipedia" in user_prompt_lower:
        return {
            "test_name": "open_wikipedia",
            "objective": "Open wikipedia.org homepage",
            "steps": [
                {"action": "navigate", "url": "https://www.wikipedia.org"}
            ],
            "timestamp": datetime.now().isoformat()
        }
    elif "python.org" in user_prompt_lower or "python" in user_prompt_lower:
        return {
            "test_name": "open_python_org",
            "objective": "Open python.org homepage",
            "steps": [
                {"action": "navigate", "url": "https://www.python.org"}
            ],
            "timestamp": datetime.now().isoformat()
        }
    else:
        # Default fallback - just try to open a website
        return {
            "test_name": "open_website",
            "objective": f"Open website based on instruction: {user_prompt}",
            "steps": [
                {"action": "navigate", "url": "https://www.google.com"}
            ],
            "timestamp": datetime.now().isoformat()
        }

def parse_instruction(user_prompt):
    """
    Parse natural language instruction into structured test steps
    """
    # Try OpenAI first if available
    if client:
        try:
            SYSTEM_PROMPT = """
You are TestSmith AI, an expert QA automation engineer. Your task is to analyze a user's natural language instruction and extract the key elements needed to write a Selenium test case in Python.

Always respond **only** with a valid JSON object with the following exact structure:
{
  "test_name": "A concise, descriptive name for the test based on the instruction.",
  "objective": "A one-sentence description of what the test should verify.",
  "steps": [
    {"action": "navigate", "url": "https://example.com/login"}
  ]
}

If the instruction is ambiguous, make a reasonable assumption. Your goal is to always produce executable code.
"""

            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            parsed_data = json.loads(result)
            parsed_data['timestamp'] = datetime.now().isoformat()
            logger.info(f"Successfully parsed instruction using OpenAI: {user_prompt}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"OpenAI parsing failed: {e}, using fallback")
            return parse_instruction_fallback(user_prompt)
    else:
        # Use fallback parser
        return parse_instruction_fallback(user_prompt)