import subprocess
import sys
import shutil
import platform

def prompt_user(message):
    """Prompt user for yes/no and return True if yes."""
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

def install_homebrew():
    print("[INFO] Attempting to install Homebrew...")
    try:
        subprocess.check_call([
            '/bin/bash', '-c',
            "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ])
        return shutil.which("brew") is not None
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install Homebrew.")
        return False

def install_graphviz_windows():
    if shutil.which("choco") is None:
        print("[WARNING] Chocolatey is not installed.")
        if prompt_user("Would you like to install Chocolatey?"):
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

def install_graphviz_mac():
    if shutil.which("brew") is None:
        print("[WARNING] Homebrew is not installed.")
        if prompt_user("Would you like to install Homebrew?"):
            if not install_homebrew():
                return False
        else:
            print("[WARNING] Skipping Homebrew install. Script may not work.")
            return False

    if prompt_user("Install Graphviz using Homebrew?"):
        try:
            subprocess.check_call(["brew", "install", "graphviz"])
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install Graphviz via Homebrew.")
            return False
    else:
        print("[WARNING] Skipping Graphviz install. Script may not work.")
        return False

def install_graphviz_linux():
    apt = shutil.which("apt")
    if not apt:
        print("[ERROR] No supported package manager found. Please install Graphviz manually.")
        return False

    if prompt_user("Install Graphviz using apt?"):
        try:
            subprocess.check_call(["sudo", "apt", "update"])
            subprocess.check_call(["sudo", "apt", "install", "-y", "graphviz"])
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install Graphviz via apt.")
            return False
    else:
        print("[WARNING] Skipping Graphviz install. Script may not work.")
        return False

def install_graphviz_by_platform():
    system = platform.system()
    if system == "Windows":
        return install_graphviz_windows()
    elif system == "Darwin":
        return install_graphviz_mac()
    elif system == "Linux":
        return install_graphviz_linux()
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
    check_graphviz_executable()
    diagram = create_import_diagram()
    diagram.render('python_imports_diagram', cleanup=True)
    print("[✔] Diagram successfully rendered: python_imports_diagram.png")
