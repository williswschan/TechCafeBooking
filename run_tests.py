#!/usr/bin/env python3
"""
TechCafe Booking App - Test Runner (Project Root)
Simple wrapper to run API tests from the tests folder
"""

import sys
import os
import subprocess

def main():
    """Run API tests from the tests folder"""
    # Get the directory where this script is located (project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(script_dir, 'tests')
    
    # Change to tests directory and run the main test runner
    os.chdir(tests_dir)
    
    try:
        result = subprocess.run([sys.executable, "run_tests.py"], 
                              capture_output=False, text=True)
        sys.exit(result.returncode)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()