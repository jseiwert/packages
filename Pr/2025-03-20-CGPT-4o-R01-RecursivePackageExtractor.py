import os
import re
import json
from pathlib import Path

def extract_packages_from_line(line):
    """
    Extracts package names and optional versions from a line of Python code.
    """
    packages = set()

    # Match import statements
    import_match = re.match(r'^\s*(import|from)\s+([a-zA-Z0-9_\.]+)', line)
    if import_match:
        pkg = import_match.group(2).split('.')[0]
        packages.add(pkg)

    # Match version hints (e.g., # numpy==1.24.1 or numpy==1.24.1)
    version_match = re.findall(r'([a-zA-Z0-9_\-]+)==([\d\.]+)', line)
    for name, version in version_match:
        packages.add(f"{name}=={version}")

    return packages

def extract_packages_from_py(file_path):
    packages = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                packages.update(extract_packages_from_line(line))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return packages

def extract_packages_from_ipynb(file_path):
    packages = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
            for cell in notebook.get("cells", []):
                if cell.get("cell_type") == "code":
                    for line in cell.get("source", []):
                        packages.update(extract_packages_from_line(line))
    except Exception as e:
        print(f"Error reading notebook {file_path}: {e}")
    return packages

def write_package_list(file_path, packages):
    """
    Writes packages to a file named <directory-filename>packages_list.txt
    """
    directory = file_path.parent.name
    stem = file_path.stem
    output_filename = f"{directory}-{stem}_packages_list.txt"
    output_path = file_path.parent / output_filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Extracted packages from: {file_path}\n\n")
        for pkg in sorted(packages):
            f.write(pkg + '\n')
    print(f"[✔] Wrote package list to: {output_path}")

def walk_and_extract(root_dir):
    """
    Recursively walk through directories and extract packages from .py and .ipynb files
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fname.endswith('.py'):
                packages = extract_packages_from_py(fpath)
            elif fname.endswith('.ipynb'):
                packages = extract_packages_from_ipynb(fpath)
            else:
                continue

            if packages:
                write_package_list(fpath, packages)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Extract installed packages from Python and Jupyter files.")
    parser.add_argument("root_dir", help="Root directory to scan")
    args = parser.parse_args()

    walk_and_extract(args.root_dir)
