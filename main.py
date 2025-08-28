import argparse
import json
import os
import sys
from nlu_processor import parse_instruction
from test_generator import generate_test_code
from test_executor import execute_test
from report_generator import add_to_report, generate_excel_report
from config import TEST_CASES_DIR, REPORTS_DIR, SCREENSHOTS_DIR, LOGS_DIR

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(TEST_CASES_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

def main():
    ensure_directories()
    
    parser = argparse.ArgumentParser(description='TestSmith AI - Autonomous Selenium Test Engineer')
    parser.add_argument('instruction', nargs='?', help='Natural language test instruction')
    parser.add_argument('--file', '-f', help='File containing multiple test instructions (one per line)')
    parser.add_argument('--eval', '-e', action='store_true', help='Run evaluation on the test dataset')
    
    args = parser.parse_args()
    
    if args.eval:
        from evaluation_runner import run_evaluation
        run_evaluation()
        return
    
    if args.file:
        with open(args.file, 'r') as f:
            instructions = [line.strip() for line in f.readlines() if line.strip()]
        
        results = []
        for instruction in instructions:
            print(f"\nProcessing: {instruction}")
            result = process_instruction(instruction)
            results.append(result)
        
        # Generate comprehensive report
        generate_excel_report(results)
        print(f"\nBatch processing complete. Results saved to {REPORTS_DIR}")
        return
    
    if not args.instruction:
        print("Please provide a test instruction or use --file for batch processing")
        parser.print_help()
        return
    
    process_instruction(args.instruction)

def process_instruction(instruction):
    """Process a single instruction through the full pipeline"""
    print(f"[1/4] Parsing instruction: {instruction}")
    parsed_data = parse_instruction(instruction)

    print("[2/4] Generating test code...")
    test_code, code_path = generate_test_code(parsed_data)

    print("[3/4] Executing test...")
    status, output, code_path, screenshot_path = execute_test(test_code, parsed_data['test_name'])

    print("[4/4] Generating report...")
    report_entry = {
        "test_name": parsed_data['test_name'],
        "description": parsed_data['objective'],
        "status": status,
        "error": output if status == "FAIL" else "",
        "screenshot_link": screenshot_path,
        "generated_code_link": code_path,
        "timestamp": parsed_data.get('timestamp', '')
    }
    
    add_to_report(report_entry)
    print(f"Test '{parsed_data['test_name']}' completed with status: {status}")
    
    if status == "FAIL":
        print(f"Error: {output}")
    
    return report_entry

if __name__ == "__main__":
    main()