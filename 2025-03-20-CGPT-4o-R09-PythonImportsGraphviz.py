import subprocess
import sys
import shutil
import platform
import ctypes
import os

def is_running_as_admin():
    """Return True if the script is running with administrative privileges."""
    if platform.system() != "Windows":
        return True  # Assume admin check only matters on Windows
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def prompt_user(message):
    try:
        response = input(f"{message} [y/N]: ").strip().lower()
        return response == "y"
    except EOFError:
        return False

def install_chocolatey():
    print("[INFO] Attempting to install Chocolatey...")
    try:
        subprocess.check_call([
            "powershell.exe",
            "-NoProfile",
            "-InputFormat", "None",
            "-ExecutionPolicy", "Bypass",
            "-Command",
            "Set-ExecutionPolicy Bypass -Scope Process -Force;"
            "[System.Net.ServicePointManager]::SecurityProtocol = "
            "[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
            "iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
        ])
        return shutil.which("choco") is not None
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install Chocolatey.")
        return False

def install_graphviz_windows():
    if shutil.which("choco") is None:
        print("[WARNING] Chocolatey (a package manager for Windows) is not installed.")
        print("It allows this script to automatically install tools like Graphviz.")
        if prompt_user("Would you like to install Chocolatey now (recommended)?"):
            if not install_chocolatey():
                return False
        else:
            print("[WARNING] Skipping Chocolatey install. Script may not work.")
            return False

    if prompt_user("Install Graphviz using Chocolatey?"):
        try:
            subprocess.check_call(["choco", "install", "graphviz", "-y"])
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install Graphviz via Chocolatey.")
            return False
    else:
        print("[WARNING] Skipping Graphviz install. Script may not work.")
        return False

def install_graphviz_by_platform():
    system = platform.system()
    if system == "Windows":
        return install_graphviz_windows()
    elif system == "Darwin":
        print("[INFO] Homebrew install support omitted for brevity.")
        return False
    elif system == "Linux":
        print("[INFO] apt/yum install support omitted for brevity.")
        return False
    else:
        print(f"[ERROR] Unsupported platform: {system}")
        return False

# Ensure 'graphviz' Python package is installed
try:
    import graphviz
except ImportError:
    print("[INFO] Installing missing Python package 'graphviz'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "graphviz"])
    import graphviz

from graphviz import Digraph

def check_graphviz_executable():
    if shutil.which("dot") is None:
        print("[WARNING] Graphviz executable 'dot' not found.")
        if install_graphviz_by_platform():
            print("[INFO] Graphviz installation attempted. Please restart terminal if needed.")
        else:
            print("[ERROR] Graphviz install skipped or failed. Exiting.")
            sys.exit(1)

        if shutil.which("dot") is None:
            print("[ERROR] 'dot' still not found after attempted install. Exiting.")
            sys.exit(1)

def create_import_diagram():
    dot = Digraph(comment='Python Imports and Packages', format='png')
    dot.attr(rankdir='LR', fontsize='12', fontname='Helvetica')

    dot.node('proj', 'my_project/', shape='folder')
    dot.node('main', 'main.py', shape='note')
    dot.node('utils', 'utils/', shape='folder')
    dot.node('init', '__init__.py', shape='note')
    dot.node('helper', 'helper.py', shape='note')

    dot.edge('proj', 'main')
    dot.edge('proj', 'utils')
    dot.edge('utils', 'init')
    dot.edge('utils', 'helper')
    dot.edge('main', 'helper', label='from utils.helper import greet', style='dashed')

    dot.node('stdlib', 'Standard Library', shape='box')
    dot.node('thirdparty', 'Third-Party Packages', shape='box')
    dot.node('localmod', 'Local Modules', shape='box')

    dot.edge('stdlib', 'main', label='import os')
    dot.edge('thirdparty', 'main', label='import numpy as np')
    dot.edge('localmod', 'main', label='from utils.helper import greet')

    return dot

if __name__ == '__main__':
    if not is_running_as_admin():
        print("\n[❗] This script must be run as Administrator to install system components.")
        print("To do this:")
        print("1. Close this window.")
        print("2. Press the Windows key, type 'Terminal' or 'PowerShell'")
        print("3. Right-click → 'Run as administrator'")
        print("4. Then re-run this script from that elevated terminal.\n")
        sys.exit(1)

    check_graphviz_executable()
    diagram = create_import_diagram()
    diagram.render('python_imports_diagram', cleanup=True)
    print("[✔] Diagram successfully rendered: python_imports_diagram.png")
