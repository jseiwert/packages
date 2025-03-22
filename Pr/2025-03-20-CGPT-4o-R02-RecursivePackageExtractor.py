import os
import re
import json
from pathlib import Path

def extract_packages_and_imports_from_line(line):
    """
    Extracts package names and optional versions from a line of Python code.
    Also captures raw import statements.
    """
    packages = set()
    imports = set()

    # Match import statements
    import_match = re.match(r'^\s*(import|from)\s+([a-zA-Z0-9_\.]+)', line)
    if import_match:
        full_import = import_match.group(0).strip()
        imports.add(full_import)
        pkg = import_match.group(2).split('.')[0]
        packages.add(pkg)

    # Match version hints (e.g., # numpy==1.24.1 or numpy==1.24.1)
    version_match = re.findall(r'([a-zA-Z0-9_\-]+)==([\d\.]+)', line)
    for name, version in version_match:
        packages.add(f"{name}=={version}")

    return packages, imports

def extract_from_py(file_path):
    packages = set()
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                pkgs, imps = extract_packages_and_imports_from_line(line)
                packages.update(pkgs)
                imports.update(imps)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return packages, imports

def extract_from_ipynb(file_path):
    packages = set()
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
            for cell in notebook.get("cells", []):
                if cell.get("cell_type") == "code":
                    for line in cell.get("source", []):
                        pkgs, imps = extract_packages_and_imports_from_line(line)
                        packages.update(pkgs)
                        imports.update(imps)
    except Exception as e:
        print(f"Error reading notebook {file_path}: {e}")
    return packages, imports

def write_package_list(file_path, packages, imports):
    """
    Writes packages and imports to a file named <directory-filename>packages_list.txt
    """
    directory = file_path.parent.name
    stem = file_path.stem
    output_filename = f"{directory}-{stem}_packages_list.txt"
    output_path = file_path.parent / output_filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Extracted from: {file_path}\n\n")

        f.write("=== Packages ===\n")
        for pkg in sorted(packages):
            f.write(pkg + '\n')

        f.write("\n=== Import Statements ===\n")
        for imp in sorted(imports):
            f.write(imp + '\n')

    print(f"[✔] Wrote package and import list to: {output_path}")

def walk_and_extract(root_dir):
    """
    Recursively walk through directories and extract packages and imports
    from .py and .ipynb files
    """
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fname.endswith('.py'):
                packages, imports = extract_from_py(fpath)
            elif fname.endswith('.ipynb'):
                packages, imports = extract_from_ipynb(fpath)
            else:
                continue

            if packages or imports:
                write_package_list(fpath, packages, imports)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Extract installed packages and import statements from Python and Jupyter files.")
    parser.add_argument("root_dir", help="Root directory to scan")
    args = parser.parse_args()

    walk_and_extract(args.root_dir)
