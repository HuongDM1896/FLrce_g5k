import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser(description="Run a benchmark experiment")
    parser.add_argument("-r", "--repeat", type=int, required=True, help="Number of repetitions")
    parser.add_argument("-e", "--exp", type=str, required=True, help="Experiment name")
    args = parser.parse_args()
    
    fls = ["flrce", "fedcom", "fedprox"]

    # Iterate over each fl and run measure.py
    for fl in fls:
        print(f"Running flower with {fl}")
        try:
            # Convert all arguments to strings explicitly
            cmd = [
                "python3", 
                "measure.py", 
                "-e", str(args.exp), 
                "-r", str(args.repeat), 
                "-m", str(fl)
            ]
            print(f"Command: {' '.join(cmd)}")  # Debug: print the command
            
            subprocess.run(cmd, check=True)
            print(f"Successfully completed experiment with {fl}\n")
        except subprocess.CalledProcessError as e:
            print(f"Error when trying to run flower with {fl}")
            print(f"Return code: {e.returncode}")
            print(f"Details: {e}\n")
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            print(f"Error type: {type(e).__name__}\n")

if __name__ == "__main__":
    main()