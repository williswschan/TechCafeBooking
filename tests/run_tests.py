#!/usr/bin/env python3
"""
TechCafe Booking App - Test Runner
Executes test suites and provides comprehensive reporting
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime

def check_app_running():
    """Check if the app is running on localhost:5000"""
    try:
        import requests
        response = requests.get("http://localhost:5000", timeout=5)
        return response.status_code == 200
    except:
        return False

def change_to_project_root():
    """Change to project root directory"""
    import os
    # Get the directory where this script is located (tests folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to project root
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)

def run_simple_tests():
    """Run simple API tests"""
    print("🧪 Running Simple API Tests...")
    print("-" * 40)
    
    try:
        result = subprocess.run([sys.executable, "tests/test_simple.py"], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Simple tests timed out")
        return False
    except Exception as e:
        print(f"❌ Error running simple tests: {e}")
        return False


def generate_combined_report():
    """Generate combined test report"""
    print("\n📊 Generating Combined Test Report...")
    print("=" * 60)
    
    # Load simple test results
    simple_results = None
    if os.path.exists('simple_test_report.json'):
        with open('simple_test_report.json', 'r') as f:
            simple_results = json.load(f)
    
    
    # Generate combined report
    combined_report = {
        'timestamp': datetime.now().isoformat(),
        'simple_tests': simple_results,
        'summary': {
            'simple_passed': simple_results['summary']['passed_tests'] if simple_results else 0,
            'simple_total': simple_results['summary']['total_tests'] if simple_results else 0,
        }
    }
    
    # Calculate overall success
    total_passed = combined_report['summary']['simple_passed']
    total_tests = combined_report['summary']['simple_total']
    overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    combined_report['summary']['overall_success_rate'] = overall_success_rate
    combined_report['summary']['all_tests_passed'] = total_passed == total_tests
    
    # Save combined report
    with open('combined_test_report.json', 'w') as f:
        json.dump(combined_report, f, indent=2)
    
    # Print summary
    print(f"📈 TEST RESULTS:")
    print(f"   Simple Tests: {combined_report['summary']['simple_passed']}/{combined_report['summary']['simple_total']}")
    print(f"   Success Rate: {overall_success_rate:.1f}%")
    print(f"   All Tests Passed: {'✅ YES' if combined_report['summary']['all_tests_passed'] else '❌ NO'}")
    
    return combined_report['summary']['all_tests_passed']

def main():
    """Main test runner"""
    print("🚀 TechCafe Booking App - Test Suite Runner")
    print("=" * 60)
    
    # Change to project root directory
    change_to_project_root()
    
    # Check if app is running
    if not check_app_running():
        print("❌ App is not running on localhost:5000")
        print("   Please start the app first: python app.py")
        sys.exit(1)
    
    print("✅ App is running, starting tests...")
    
    # Run simple tests
    simple_success = run_simple_tests()
    
    # Generate combined report
    all_passed = generate_combined_report()
    
    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! App is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  SOME TESTS FAILED! Please check the detailed reports.")
        print("   - tests/simple_test_report.json")
        print("   - tests/combined_test_report.json")
        sys.exit(1)

if __name__ == "__main__":
    main()
