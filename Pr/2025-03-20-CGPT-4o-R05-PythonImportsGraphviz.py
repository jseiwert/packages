import subprocess
import sys
import shutil
import platform
import os

def install_graphviz_windows():
    """Attempt to install Graphviz on Windows using Chocolatey."""
    if shutil.which("choco") is None:
        print(
            "\n[ERROR] Chocolatey is not installed.\n"
            "Please install Graphviz manually from: https://graphviz.org/download/\n"
            "Or install Chocolatey from: https://chocolatey.org/install\n"
        )
        return False
    try:
        subprocess.check_call(["choco", "install", "graphviz", "-y"])
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install Graphviz via Chocolatey.")
        return False

def install_graphviz_mac():
    """Attempt to install Graphviz on macOS using Homebrew."""
    if shutil.which("brew") is None:
        print(
            "\n[ERROR] Homebrew is not installed.\n"
            "Install it from https://brew.sh and try again,\n"
            "or install Graphviz manually from https://graphviz.org/download/\n"
        )
        return False
    try:
        subprocess.check_call(["brew", "install", "graphviz"])
        return True
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install Graphviz via Homebrew.")
        return False

def install_graphviz_linux():
    """Attempt to install Graphviz on Linux using apt or yum."""
    apt = shutil.which("apt")
    yum = shutil.which("yum")

    if apt:
        try:
            subprocess.check_call(["sudo", "apt", "update"])
            subprocess.check_call(["sudo", "apt", "install", "-y", "graphviz"])
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install Graphviz using apt.")
    elif yum:
        try:
            subprocess.check_call(["sudo", "yum", "install", "-y", "graphviz"])
            return True
        except subprocess.CalledProcessError:
            print("[ERROR] Failed to install Graphviz using yum.")
    else:
        print("[ERROR] No supported package manager found (apt or yum).")
    return False

def install_graphviz_by_platform():
    """Dispatch platform-specific Graphviz installation."""
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
    """Ensure the 'dot' executable from Graphviz is available."""
    if shutil.which("dot") is None:
        print("[WARNING] Graphviz executable 'dot' not found.")
        if install_graphviz_by_platform():
            print("[INFO] Installation attempted. Please restart your terminal if needed.")
        else:
            print("[ERROR] Graphviz installation failed or not supported. Exiting.")
            sys.exit(1)

        # Recheck after attempted install
        if shutil.which("dot") is None:
            print("[ERROR] 'dot' still not found after attempted install. Exiting.")
            sys.exit(1)

def create_import_diagram():
    dot = Digraph(comment='Python Imports and Packages', format='png')
    dot.attr(rankdir='LR', fontsize='12', fontname='Helvetica')

    # File structure
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

    # External sources
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
