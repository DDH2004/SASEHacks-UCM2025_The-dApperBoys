import subprocess
import os
import time

def start_local_validator():
    """Start a local Solana validator for development"""
    print("Starting local Solana validator...")
    
    # Create directory for validator data if it doesn't exist
    validator_dir = os.path.expanduser("~/solana-local-validator")
    os.makedirs(validator_dir, exist_ok=True)
    
    # Start the validator
    cmd = ["solana-test-validator", "--ledger", validator_dir]
    validator_process = subprocess.Popen(cmd)
    
    # Give it some time to start
    time.sleep(5)
    print("Local Solana validator is running!")
    return validator_process

if __name__ == "__main__":
    validator = start_local_validator()
    try:
        # Keep the script running
        print("Press Ctrl+C to stop the validator")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping validator...")
        validator.terminate()
        print("Validator stopped")