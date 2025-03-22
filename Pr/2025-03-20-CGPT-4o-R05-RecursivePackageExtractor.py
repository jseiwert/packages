import os
import re
import json
import csv
import sys
import subprocess
from pathlib import Path

# Ensure 'stdlib_list' is installed
try:
    from stdlib_list import stdlib_list
except ImportError:
    print("[!] 'stdlib_list' not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "stdlib_list"])
    from stdlib_list import stdlib_list

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
    imported_names = set()

    import_from_match = re.match(r'^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+([a-zA-Z0-9_\*,\s]+)', line)
    import_plain_match = re.match(r'^\s*import\s+([a-zA-Z0-9_\.]+)(\s+as\s+([a-zA-Z0-9_]+))?', line)

    if import_from_match:
        module = import_from_match.group(1).split('.')[0]
        names = import_from_match.group(2).replace(' ', '').split(',')
        packages.add(module)
        imports.add(line.strip())
        for name in names:
            imported_names.add(f"{module}.{name}")
    elif import_plain_match:
        module = import_plain_match.group(1).split('.')[0]
        alias = import_plain_match.group(3)
        packages.add(module)
        imports.add(line.strip())
        imported_names.add(f"{module} as {alias}" if alias else module)

    version_match = re.findall(r'([a-zA-Z0-9_\-]+)==([\d\.]+)', line)
    for name, version in version_match:
        packages.add(f"{name}=={version}")

    return packages, imports, imported_names

def extract_from_file(file_path, filetype='py'):
    packages, imports, imported_names = set(), set(), set()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f if filetype == 'py' else json.load(f).get("cells", [])
            for line in lines:
                if filetype == 'ipynb':
                    if isinstance(line, dict) and line.get("cell_type") == "code":
                        source_lines = line.get("source", [])
                        for subline in source_lines:
                            pkgs, imps, names = extract_packages_and_imports_from_line(subline)
                            packages.update(pkgs)
                            imports.update(imps)
                            imported_names.update(names)
                else:
                    pkgs, imps, names = extract_packages_and_imports_from_line(line)
                    packages.update(pkgs)
                    imports.update(imps)
                    imported_names.update(names)
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")

    return packages, imports, imported_names

def write_outputs(file_path, packages, imports, imported_names, summary_data):
    directory = file_path.parent.name
    stem = file_path.stem
    base_output_name = f"{directory}-{stem}"
    out_dir = file_path.parent

    txt_path = out_dir / f"{base_output_name}_packages_list.txt"
    md_path = out_dir / f"{base_output_name}_imports.md"
    csv_path = out_dir / f"{base_output_name}_imports.csv"

    # Write TXT
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Extracted from: {file_path}\n\n")
        f.write("=== Packages ===\n")
        for pkg in sorted(packages):
            f.write(pkg + '\n')
        f.write("\n=== Import Statements ===\n")
        for imp in sorted(imports):
            f.write(imp + '\n')
        f.write("\n=== Imported Names ===\n")
        for name in sorted(imported_names):
            f.write(name + '\n')

    # Write Markdown
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Imports from `{file_path}`\n\n")
        f.write("## Packages\n")
        for pkg in sorted(packages):
            label = classify_module(pkg.split("==")[0] if "==" in pkg else pkg)
            f.write(f"- `{pkg}` ({label})\n")

        f.write("\n## Import Statements\n")
        for imp in sorted(imports):
            f.write(f"- `{imp}`\n")

        f.write("\n## Imported Names\n")
        for name in sorted(imported_names):
            label = classify_module(name.split('.')[0])
            f.write(f"- `{name}` ({label})\n")

    # Write CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Type"])
        for pkg in sorted(packages):
            label = classify_module(pkg.split("==")[0] if "==" in pkg else pkg)
            writer.writerow([pkg, label])
        for name in sorted(imported_names):
            label = classify_module(name.split('.')[0])
            writer.writerow([name, label])

    print(f"[✔] Wrote TXT, MD, and CSV outputs for: {file_path}")

    # Add to summary
    summary_data.append({
        "file": str(file_path),
        "packages": sorted(packages),
        "imports": sorted(imports),
        "names": sorted(imported_names)
    })

def write_summary_file(summary_data, root_dir):
    summary_txt = Path(root_dir) / "summary_all_packages.txt"
    with open(summary_txt, 'w', encoding='utf-8') as f:
        for entry in summary_data:
            f.write(f"# {entry['file']}\n")
            f.write("## Packages\n")
            for pkg in entry['packages']:
                f.write(f"- {pkg}\n")
            f.write("\n## Import Statements\n")
            for imp in entry['imports']:
                f.write(f"- {imp}\n")
            f.write("\n## Imported Names\n")
            for name in entry['names']:
                f.write(f"- {name}\n")
            f.write("\n" + "="*40 + "\n\n")
    print(f"[✔] Wrote summary file: {summary_txt}")

def walk_and_extract(root_dir):
    summary_data = []

    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            fpath = Path(dirpath) / fname
            if fname.endswith('.py'):
                packages, imports, imported_names = extract_from_file(fpath, 'py')
            elif fname.endswith('.ipynb'):
                packages, imports, imported_names = extract_from_file(fpath, 'ipynb')
            else:
                continue

            if packages or imports or imported_names:
                write_outputs(fpath, packages, imports, imported_names, summary_data)

    write_summary_file(summary_data, root_dir)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Extract packages, import statements, and imported names from Python and Jupyter files.")
    parser.add_argument("root_dir", help="Root directory to scan")
    args = parser.parse_args()

    walk_and_extract(args.root_dir)
