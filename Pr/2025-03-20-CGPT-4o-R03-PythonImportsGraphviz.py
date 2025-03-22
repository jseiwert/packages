import subprocess
import sys
import shutil

# Ensure 'graphviz' package is installed
try:
    import graphviz
except ImportError:
    print("[INFO] 'graphviz' package not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "graphviz"])
    import graphviz

from graphviz import Digraph

def check_graphviz_executable():
    """Ensure the 'dot' executable from Graphviz is available."""
    if shutil.which("dot") is None:
        print(
            "\n[ERROR] Graphviz executable 'dot' not found.\n"
            "Please install Graphviz from: https://graphviz.org/download/\n"
            "Make sure to check the option to add it to your PATH.\n"
            "After installing, restart your terminal or PowerShell.\n"
        )
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
