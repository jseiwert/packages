import os
import shutil
import subprocess
import platform
import sys

# Check if Graphviz is installed and in PATH
def check_dot_in_path():
    dot_path = shutil.which("dot")
    if dot_path:
        print(f"[✔] Found 'dot' executable at: {dot_path}")
        try:
            version = subprocess.check_output(["dot", "-V"], stderr=subprocess.STDOUT).decode()
            print(f"[✔] Graphviz version: {version.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"[!] 'dot' found but failed to execute: {e.output.decode().strip()}")
            return False
        return True
    else:
        print("[✘] 'dot' not found in PATH.")
        return False

def suggest_fix():
    system = platform.system()
    print("\n--- Suggestions ---")
    if system == "Windows":
        print("1. Download Graphviz installer from https://graphviz.org/download/")
        print("2. During setup, ensure you CHECK the box to 'Add Graphviz to system PATH'")
        print("3. After install, restart your terminal and run 'dot -V' to verify.")
        print("4. If already installed, add its 'bin' folder to your PATH manually:")
        print("   Example: C:\\Program Files\\Graphviz\\bin")
    elif system == "Darwin":
        print("Install using Homebrew: brew install graphviz")
    elif system == "Linux":
        print("Install using: sudo apt install graphviz")
    else:
        print(f"[!] Unsupported platform: {system}")

def main():
    print("[INFO] Checking Graphviz system installation...\n")
    if not check_dot_in_path():
        suggest_fix()

if __name__ == "__main__":
    main()
