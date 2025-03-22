import subprocess
import sys
import shutil
import platform
import graphviz
from graphviz import Digraph

def print_graphviz_install_instructions():
    system = platform.system()
    print("\n[!] Graphviz executable 'dot' is not available. You must install Graphviz manually:")
    if system == "Windows":
        print("1. Download Graphviz from: https://graphviz.org/download/")
        print("2. During installation, check the box: 'Add Graphviz to system PATH'")
        print("3. After installation, restart your terminal.")
        print("4. Confirm installation by running: dot -V")
    elif system == "Darwin":
        print("Run: brew install graphviz")
    elif system == "Linux":
        print("Run: sudo apt install graphviz")
    else:
        print("Unsupported platform. Please install Graphviz manually from: https://graphviz.org/download/")

def check_graphviz_executable():
    if shutil.which("dot") is None:
        print_graphviz_install_instructions()
        sys.exit(1)

def create_import_diagram(output_format, filename):
    dot = Digraph(comment='Python Imports and Packages', format=output_format)
    dot.attr(rankdir='LR', fontsize='16', fontname='Times-Roman')
    dot.attr(size='10,7')

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

    try:
        dot.render(filename, cleanup=True)
        print(f"[✔] Diagram successfully rendered: {filename}.{output_format}")
    except Exception as e:
        print(f"[✘] Failed to render diagram to {output_format}: {e}")

if __name__ == '__main__':
    check_graphviz_executable()
    create_import_diagram('png', '2025-03-21-CGPT-4o-R16-PythonImportsGraphviz_TimesRoman')
    create_import_diagram('pdf', '2025-03-21-CGPT-4o-R16-PythonImportsGraphviz_TimesRoman')
