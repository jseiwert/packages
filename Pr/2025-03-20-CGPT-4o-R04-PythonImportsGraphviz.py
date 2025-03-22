import subprocess
import sys
import shutil
import os
import platform

def install_system_graphviz():
    """Attempt to install Graphviz on Windows using Chocolatey or provide fallback instructions."""
    if platform.system() != "Windows":
        print("[ERROR] Auto-install is only supported on Windows. Please install manually from https://graphviz.org/download/")
        sys.exit(1)

    print("[INFO] Attempting to install Graphviz system package...")

    # Check if Chocolatey is available
    if shutil.which("choco") is None:
        print(
            "\n[ERROR] Chocolatey is not installed.\n"
            "Please install Graphviz manually from: https://graphviz.org/download/\n"
            "OR install Chocolatey from: https://chocolatey.org/install\n"
        )
        sys.exit(1)

    try:
        subprocess.check_call(["choco", "install", "graphviz", "-y"])
        print("[INFO] Graphviz installed. Restart your terminal if needed.")
    except subprocess.CalledProcessError:
        print("\n[ERROR] Failed to install Graphviz via Chocolatey.")
        sys.exit(1)

# Ensure 'graphviz' package is installed
try:
    import graphviz
except ImportError:
    print("[INFO] 'graphviz' package not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "graphviz"])
    import graphviz

from graphviz import Digraph

def check_graphviz_executable():
    """Ensure the 'dot' executable from Graphviz is available, or try to install it."""
    if shutil.which("dot") is None:
        print("[WARNING] Graphviz executable 'dot' not found.")
        install_system_graphviz()
        if shutil.which("dot") is None:
            print("\n[ERROR] 'dot' still not found after attempted install. Please install Graphviz and restart.")
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
