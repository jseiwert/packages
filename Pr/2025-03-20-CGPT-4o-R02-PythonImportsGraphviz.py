import subprocess
import sys

# Ensure 'graphviz' is installed
try:
    import graphviz
except ImportError:
    print("[INFO] 'graphviz' not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "graphviz"])
    import graphviz

from graphviz import Digraph

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
    diagram = create_import_diagram()
    diagram.render('python_imports_diagram', cleanup=True)
