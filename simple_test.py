# simple_test.py - Test basic functionality
from nlu_processor import parse_instruction_fallback

# Test the fallback parser
result = parse_instruction_fallback("Open google.com")
print("Fallback parser result:", result)

# Test if we can generate code
from test_generator import generate_test_code
test_code, filepath = generate_test_code(result)
print("Generated test file:", filepath)
print("Test code generated successfully!")