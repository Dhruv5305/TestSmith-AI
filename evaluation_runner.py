import time
from main import process_instruction
from config import EVALUATION_DATASET
import logging

logger = logging.getLogger('EvaluationRunner')

def run_evaluation():
    """
    Run evaluation on the test dataset and calculate metrics
    """
    print("Running evaluation on test dataset...")
    
    results = {
        "easy": {"total": 0, "passed": 0, "failed": 0, "timeouts": 0, "errors": 0, "latencies": []},
        "medium": {"total": 0, "passed": 0, "failed": 0, "timeouts": 0, "errors": 0, "latencies": []},
        "hard": {"total": 0, "passed": 0, "failed": 0, "timeouts": 0, "errors": 0, "latencies": []},
        "overall": {"total": 0, "passed": 0, "failed": 0, "timeouts": 0, "errors": 0, "latencies": []}
    }
    
    # Run tests for each difficulty level
    for difficulty, instructions in EVALUATION_DATASET.items():
        print(f"\n=== Evaluating {difficulty.upper()} tests ===")
        
        for instruction in instructions:
            print(f"\nRunning: {instruction}")
            start_time = time.time()
            
            try:
                result = process_instruction(instruction)
                end_time = time.time()
                latency = end_time - start_time
                
                results[difficulty]["latencies"].append(latency)
                results["overall"]["latencies"].append(latency)
                
                results[difficulty]["total"] += 1
                results["overall"]["total"] += 1
                
                if result["status"] == "PASS":
                    results[difficulty]["passed"] += 1
                    results["overall"]["passed"] += 1
                    print(f"✓ PASSED (in {latency:.2f}s)")
                else:
                    results[difficulty]["failed"] += 1
                    results["overall"]["failed"] += 1
                    print(f"✗ FAILED (in {latency:.2f}s)")
                    
            except Exception as e:
                end_time = time.time()
                latency = end_time - start_time
                
                results[difficulty]["latencies"].append(latency)
                results["overall"]["latencies"].append(latency)
                
                results[difficulty]["total"] += 1
                results[difficulty]["errors"] += 1
                results["overall"]["total"] += 1
                results["overall"]["errors"] += 1
                
                print(f"✗ ERROR: {str(e)} (in {latency:.2f}s)")
    
    # Calculate metrics
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    
    for difficulty in ["easy", "medium", "hard", "overall"]:
        data = results[difficulty]
        if data["total"] > 0:
            accuracy = (data["passed"] / data["total"]) * 100
            avg_latency = sum(data["latencies"]) / len(data["latencies"]) if data["latencies"] else 0
            p80_latency = sorted(data["latencies"])[int(len(data["latencies"]) * 0.8)] if data["latencies"] else 0
            
            print(f"\n{difficulty.upper()} LEVEL:")
            print(f"  Accuracy: {accuracy:.2f}% ({data['passed']}/{data['total']})")
            print(f"  Average Latency: {avg_latency:.2f}s")
            print(f"  80th Percentile Latency: {p80_latency:.2f}s")
            print(f"  Failures: {data['failed']}, Errors: {data['errors']}")
    
    # Check success criteria
    overall = results["overall"]
    overall_accuracy = (overall["passed"] / overall["total"]) * 100 if overall["total"] > 0 else 0
    latencies = overall["latencies"]
    p80_latency = sorted(latencies)[int(len(latencies) * 0.8)] if latencies else 0
    
    print("\n" + "="*50)
    print("SUCCESS CRITERIA CHECK")
    print("="*50)
    
    accuracy_met = overall_accuracy >= 90
    latency_met = p80_latency <= 3 if latencies else False
    
    print(f"Accuracy >90%: {overall_accuracy:.2f}% - {'✓ MET' if accuracy_met else '✗ NOT MET'}")
    print(f"80% of tasks <3s: {p80_latency:.2f}s - {'✓ MET' if latency_met else '✗ NOT MET'}")
    
    if accuracy_met and latency_met:
        print("\n🎉 ALL SUCCESS CRITERIA MET! 🎉")
    else:
        print("\n❌ Some success criteria were not met.")
    
    return results