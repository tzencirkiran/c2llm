#!/usr/bin/env python3
import os
import sys
import subprocess
import pathlib
import difflib
import json
from typing import List, Set

def is_fuzzy_match(term: str, target: str, threshold: float = 0.8) -> bool:
    """Checks if a term is an exact substring or a fuzzy match to a target string."""
    term = term.lower()
    target = target.lower()
    
    if term in target:
        return True
    
    # Split target into words (by common delimiters) to check for fuzzy word matches
    words = target.replace('/', ' ').replace('.', ' ').replace('_', ' ').replace('-', ' ').split()
    for word in words:
        if difflib.SequenceMatcher(None, term, word).ratio() >= threshold:
            return True
    return False

def get_files_for_group(keywords: List[str]) -> Set[pathlib.Path]:
    """Finds files for a single group of keywords (AND logic)."""
    found_files = set()
    cwd = pathlib.Path.cwd()
    
    ext_map = {
        "python": ".py", "py": ".py",
        "javascript": ".js", "js": ".js", "ts": ".ts", "typescript": ".ts",
        "html": ".html", "css": ".css",
        "bash": ".sh", "shell": ".sh",
        "rust": ".rs", "go": ".go",
        "markdown": ".md", "md": ".md",
        "json": ".json", "yaml": ".yaml", "yml": ".yml"
    }

    # Directories to always ignore
    ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}

    target_exts = []
    search_terms = []
    
    for k in keywords:
        matches = difflib.get_close_matches(k.lower(), ext_map.keys(), n=1, cutoff=0.7)
        if matches:
            target_exts.append(ext_map[matches[0]])
        else:
            search_terms.append(k.lower())

    for path in cwd.rglob("*"):
        # Skip directories and ignored paths
        if path.is_dir() or any(part in ignore_dirs for part in path.parts):
            continue
            
        ext_match = not target_exts or path.suffix in target_exts
        path_str = str(path.relative_to(cwd))
        term_match = not search_terms or all(is_fuzzy_match(term, path_str) for term in search_terms)
        
        if ext_match and term_match:
            found_files.add(path)
            
    return found_files

def parse_selection(selection_str: str, max_val: int) -> List[int]:
    """Parses a string like '1, 3, 5-8' into a list of indices."""
    if not selection_str.strip() or selection_str.lower() in ["all", "y", "yes"]:
        return list(range(max_val))
    
    indices = set()
    parts = selection_str.replace(',', ' ').split()
    
    for part in parts:
        try:
            if '-' in part:
                start_str, end_str = part.split('-')
                start, end = int(start_str), int(end_str)
                indices.update(range(start - 1, end))
            else:
                indices.add(int(part) - 1)
        except ValueError:
            continue
            
    return sorted([i for i in indices if 0 <= i < max_val])

def get_config_path():
    """Finds the nearest .c2llm.json file or the repo root."""
    curr = pathlib.Path.cwd()
    for parent in [curr] + list(curr.parents):
        if (parent / ".git").exists() or (parent / ".c2llm.json").exists():
            return parent / ".c2llm.json"
    return curr / ".c2llm.json"

def load_config():
    path = get_config_path()
    config = {"fixed_files": [], "enabled": True, "auto_browser": False, "model": "chatgpt"}
    if path.exists():
        try:
            with open(path, 'r') as f:
                config.update(json.load(f))
        except:
            pass
    return config

def save_config(config):
    path = get_config_path()
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)

def handle_browser_command(args):
    if not args or args[0] != "toggle":
        print("Usage: c2llm browser toggle")
        return
    
    config = load_config()
    config['auto_browser'] = not config.get('auto_browser', False)
    save_config(config)
    print(f"Auto-Browser is now {'ENABLED' if config['auto_browser'] else 'DISABLED'}")

def handle_set_command(args):
    if not args:
        print("Usage: c2llm set [chatgpt | gemini | claude]")
        return
    model = args[0].lower()
    valid_models = ["chatgpt", "gemini", "claude"]
    if model not in valid_models:
        print(f"Invalid model. Choose from: {', '.join(valid_models)}")
        return
    config = load_config()
    config['model'] = model
    save_config(config)
    print(f"Default model set to: {model.upper()}")

def handle_fixed_command(args):
    config = load_config()
    if not args:
        print(f"Fixed files (Enabled: {config['enabled']}):")
        if config['fixed_files']:
            for f in config['fixed_files']:
                print(f"  - {f}")
        else:
            print("  (None)")
        return

    action = args[0]
    if action == "-a" and len(args) > 1:
        filename = args[1]
        if filename not in config['fixed_files']:
            config['fixed_files'].append(filename)
            save_config(config)
            print(f"Added {filename} to fixed files.")
    elif action == "-rm" and len(args) > 1:
        filename = args[1]
        if filename in config['fixed_files']:
            config['fixed_files'].remove(filename)
            save_config(config)
            print(f"Removed {filename} from fixed files.")
    else:
        print("Usage: c2llm fixed [-a filename | -rm filename]")

def handle_persistence_command(args):
    if not args or args[0] != "toggle":
        print("Usage: c2llm persistence toggle")
        return
    
    config = load_config()
    config['enabled'] = not config.get('enabled', True)
    save_config(config)
    print(f"Persistence is now {'ENABLED' if config['enabled'] else 'DISABLED'}")

def show_status():
    config = load_config()
    print("\n📊 c2llm Status (Repo-specific)")
    print(f"--------------------------------")
    print(f"Active Model: {config.get('model', 'chatgpt').upper()}")
    print(f"Persistence:  {'✅ ENABLED' if config.get('enabled', True) else '❌ DISABLED'}")
    print(f"Auto-Browser: {'✅ ENABLED' if config.get('auto_browser', False) else '❌ DISABLED'}")
    
    fixed = config.get('fixed_files', [])
    print(f"\nFixed Files ({len(fixed)}):")
    if fixed:
        for f in fixed:
            print(f"  - {f}")
    else:
        print("  (None)")
    print("")

def show_help():
    help_text = """
🚀 c2llm: Code to LLM Clipboard Utility

Usage:
  c2llm [queries]          Search and copy files
  c2llm set [model]          Set active LLM (chatgpt, gemini, claude)
  c2llm fixed              Manage repo-specific fixed files
  c2llm persistence toggle Toggle fixed files inclusion
  c2llm browser toggle     Toggle auto-opening ChatGPT in Firefox
  c2llm status             Show current repo settings
  c2llm --help             Show this help message

Search Queries:
  - Supports fuzzy matching for typos (e.g., 'pyton' -> 'python').
  - Use languages or extensions (e.g., 'python', 'js', 'bash').
  - Use 'and', '+', or ',' to search for multiple groups (OR logic).
  - Keywords within a group use AND logic.

Examples:
  c2llm python auth                     # Python files with 'auth' in path
  c2llm main.py, utils.py               # Both specific files
  c2llm js ui + python logic            # JS UI files AND Python logic files

Interactive Selection:
  - After searching, you'll see a numbered list.
  - Press [Enter] to copy ALL found files.
  - Type numbers (1, 3) or ranges (1-4) to pick specific files.
  - Type 'n' to cancel.

Persistence & Browser (Repo-specific):
  c2llm fixed -a <file>     # Add a file to be included in every search
  c2llm fixed -rm <file>    # Remove a file from fixed list
  c2llm fixed               # List current fixed files
  c2llm persistence toggle  # Enable/Disable auto-inclusion of fixed files
  c2llm browser toggle      # Auto-open ChatGPT in Firefox after copying

Output:
  Files are formatted with '--- FILE: filename ---' headers,
  optimized for pasting into ChatGPT/LLM prompts.
"""
    print(help_text)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ["--help", "-h"]:
        show_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "status":
        show_status()
        sys.exit(0)
    elif cmd == "fixed":
        handle_fixed_command(sys.argv[2:])
        sys.exit(0)
    elif cmd == "persistence":
        handle_persistence_command(sys.argv[2:])
        sys.exit(0)
    elif cmd == "set":
        handle_set_command(sys.argv[2:])
        sys.exit(0)
    elif cmd == "browser":
        handle_browser_command(sys.argv[2:])
        sys.exit(0)

    # Normal search logic
    config = load_config()
    raw_args = sys.argv[1:]
    groups = []
    current_group = []
    
    separators = {"and", "+", ","}
    
    for arg in raw_args:
        clean_arg = arg.strip().lower()
        if clean_arg in separators:
            if current_group:
                groups.append(current_group)
                current_group = []
        elif clean_arg.endswith(','):
            current_group.append(clean_arg[:-1])
            groups.append(current_group)
            current_group = []
        else:
            current_group.append(arg)
            
    if current_group:
        groups.append(current_group)

    all_found_files = set()
    for group in groups:
        all_found_files.update(get_files_for_group(group))

    # Add fixed files if enabled
    if config.get('enabled', True):
        cwd = pathlib.Path.cwd()
        for f_name in config.get('fixed_files', []):
            f_path = cwd / f_name
            if f_path.exists() and f_path.is_file():
                all_found_files.add(f_path)

    files = sorted(list(all_found_files))

    if not files:
        print(f"No files found matching your query.")
        sys.exit(0)

    print(f"\nFound {len(files)} files:")
    for i, f in enumerate(files, 1):
        print(f"  {i}. {f.relative_to(pathlib.Path.cwd())}")

    print("\nSelection options:")
    print(" - Press Enter (or type 'all') to copy all")
    print(" - Type numbers (e.g., '1, 3, 5') or ranges (e.g., '1-4')")
    print(" - Type 'n' to cancel")
    
    selection_input = input("\nSelection: ").strip().lower()
    
    if selection_input == 'n':
        print("Cancelled.")
        sys.exit(0)

    selected_indices = parse_selection(selection_input, len(files))
    selected_files = [files[i] for i in selected_indices]

    if not selected_files:
        print("No files selected. Cancelled.")
        sys.exit(0)

    print(f"\nCopying {len(selected_files)} files to clipboard...")
    
    output = []
    for f in selected_files:
        try:
            content = f.read_text(encoding='utf-8')
            output.append(f"--- FILE: {f.relative_to(pathlib.Path.cwd())} ---\n")
            output.append(content)
            output.append("\n\n")
        except Exception as e:
            print(f"Error reading {f}: {e}")

    final_text = "".join(output)
    
    try:
        process = subprocess.Popen(['wl-copy'], stdin=subprocess.PIPE)
        process.communicate(input=final_text.encode('utf-8'))
        print("\n✅ Successfully copied to clipboard!")

        # Auto-browser logic
        if config.get('auto_browser', False):
            model = config.get('model', 'chatgpt')
            urls = {
                "chatgpt": "https://chatgpt.com/?temporary-chat=true",
                "gemini": "https://gemini.google.com/app",
                "claude": "https://claude.ai/new?incognito"
            }
            url = urls.get(model, urls["chatgpt"])
            print(f"🌐 Opening {model.upper()} in Firefox...")
            subprocess.Popen(['firefox', '--new-tab', url],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
    except FileNotFoundError:
        print("\n❌ Error: 'wl-copy' not found. Please install 'wl-clipboard'.")

if __name__ == "__main__":
    main()
