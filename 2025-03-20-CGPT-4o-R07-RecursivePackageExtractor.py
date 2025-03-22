import os
import re
import json
import csv
import sys
import subprocess
from pathlib import Path

# Ensure required package is installed
try:
    from stdlib_list import stdlib_list
except ImportError:
    print("[INFO] 'stdlib_list' not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "stdlib_list"])
    from stdlib_list import stdlib_list  # Import after installation

# Determine current Python major.minor version for standard lib detection
PY_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
STD_LIBS = set(stdlib_list(PY_VERSION))

def classify_module(name):
    if name in STD_LIBS:
        return "standard"
    return "custom"

def extract_packages_and_imports_from_line(line):
    packages = set()
    imports = set()

    import_from_match = re.match(r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+([a-zA-Z0-9_\*,\s]+)', line)
    import_plain_match = re.match(r'^\s*import\s+([a-zA-Z0-9_\.]+)(\s+as\s+([a-zA-Z0-9_]+))?', line)

    if import_from_match:
        module = import_from_match.group(1).split('.')[0]
        imports.add(line.strip())
        packages.add(module)
    elif import_plain_match:
        module = import_plain_match.group(1).split('.')[0]
        alias = import_plain_match.group(3)
        imports.add(line.strip())
        packages.add(module)

    version_match = re.findall(r'([a-zA-Z0-9_\-]+)==([\d\.]+)', line)
    for name, version in version_match:
        packages.add(f"{name}=={version}")

    return packages, imports

def extract_from_file(file_path, filetype='py'):
    packages, imports = set(), set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f if filetype == 'py' else json.load(f).get("cells", [])
            for line in lines:
                if filetype == 'ipynb':
                    if isinstance(line, dict) and line.get("cell_type") == "code":
                        source_lines = line.get("source", [])
                        for subline in source_lines:
                            pkgs, imps = extract_packages_and_imports_from_line(subline)
                            packages.update(pkgs)
                            imports.update(imps)
                else:
                    pkgs, imps = extract_packages_and_imports_from_line(line)
                    packages.update(pkgs)
                    imports.update(imps)
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")

    return packages, imports

def write_summary_files(summary_data, root_dir):
    summary_txt = Path(root_dir) / "summary_all_packages.txt"
    summary_csv = Path(root_dir) / "summary_all_packages.csv"
    summary_md = Path(root_dir) / "summary_all_packages.md"

    # Write TXT Summary
    with open(summary_txt, 'w', encoding='utf-8') as f:
        for entry in summary_data:
            f.write(f"# {entry['file_path']}\n")
            f.write("## Packages and Imports\n")
            for pkg, imp in entry['package_imports']:
                f.write(f"- `{pkg}` | `{imp}`\n")
            f.write("\n" + "="*40 + "\n\n")

    # Write CSV Summary
    with open(summary_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["File Path", "File Name", "Package", "Import"])
        for entry in summary_data:
            for pkg, imp in entry["package_imports"]:
                writer.writerow([entry["file_path"], entry["file_name"], pkg, imp])

    # Write Markdown Summary as a Table
    with open(summary_md, 'w', encoding='utf-8') as f:
        f.write("# Summary of Extracted Packages and Imports\n\n")
        f.write("| File Path | File Name | Package | Import |\n")
        f.write("|-----------|-----------|---------|--------|\n")
        for entry in summary_data:
            for pkg, imp in entry["package_imports"]:
                f.write(f"| `{entry['file_path']}` | `{entry['file_name']}` | `{pkg}` | `{imp}` |\n")

    print(f"[✔] Wrote summary files: TXT, CSV, and MD")

def write_individual_file(file_path, packages, imports):
    """
    Writes individual package and import lists for each file in CSV and MD formats.
    """
    directory = file_path.parent.name
    stem = file_path.stem
    base_output_name = f"{directory}-{stem}"
    out_dir = file_path.parent

    md_path = out_dir / f"{base_output_name}_imports.md"
    csv_path = out_dir / f"{base_output_name}_imports.csv"

    package_imports = list(zip(sorted(packages), sorted(imports)))

    # Write Markdown
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Imports from `{file_path}`\n\n")
        f.write("| Package | Import |\n")
        f.write("|---------|--------|\n")
        for pkg, imp in package_imports:
            f.write(f"| `{pkg}` | `{imp}` |\n")

    # Write CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Package", "Import"])
        for pkg, imp in package_imports:
            writer.writerow([pkg, imp])

    print(f"[✔] Wrote individual CSV and MD outputs for: {file_path}")

def walk_and_extract(root_dir):
    summary_data = []

    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fname.endswith('.py'):
                packages, imports = extract_from_file(fpath, 'py')
            elif fname.endswith('.ipynb'):
                packages, imports = extract_from_file(fpath, 'ipynb')
            else:
                continue

            if packages or imports:
                package_imports = list(zip(sorted(packages), sorted(imports)))
                summary_data.append({
                    "file_path": str(fpath.parent),
                    "file_name": fpath.name,
                    "package_imports": package_imports
                })
                write_individual_file(fpath, packages, imports)

    write_summary_files(summary_data, root_dir)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Extract packages, import statements, and imported names from Python and Jupyter files.")
    parser.add_argument("root_dir", help="Root directory to scan")
    args = parser.parse_args()

    walk_and_extract(args.root_dir)
