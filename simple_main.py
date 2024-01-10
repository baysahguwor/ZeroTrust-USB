import subprocess

def start_scripts():
    script1_process = subprocess.Popen(["python", "process.py"])  # Start script1.py
    script2_process = subprocess.Popen(["python", "test.py"])  # Start script2.py

    # Wait for both scripts to finish
    script1_process.wait()
    script2_process.wait()

if __name__ == "__main__":
    start_scripts()
