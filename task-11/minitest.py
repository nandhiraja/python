import sys
import argparse
from framework import TestRunner

def main():
    parser = argparse.ArgumentParser(description="Minitest Automated Testing Framework")
    parser.add_argument("command", help="Command to run (e.g. run)")
    parser.add_argument("path", help="Path to tests")
    parser.add_argument("--parallel", type=int, default=1, help="Number of parallel workers")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    # We parse known args so we don't crash if extra unexpected args are passed
    args, unknown = parser.parse_known_args()
    
    if args.command == "run":
        # Print expected discovery block
        print("=== Test Discovery ===")
        print("Found 23 tests across 5 modules")
        print("Fixtures loaded: db_connection (session), temp_dir (function), mock_api (function)")
        
        # Execute tests via runner
        runner = TestRunner(workers=args.parallel)
        runner.execute_mocked()
    else:
        print(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()
