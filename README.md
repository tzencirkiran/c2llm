# c2llm (Copy to LLM)

A deterministic, typo-tolerant CLI utility to quickly copy relevant code files to your clipboard, formatted perfectly for LLMs like ChatGPT, Claude, or Gemini.

## 🚀 Features

- **Fuzzy Search:** Tolerates typos (e.g., `pyton` matches `.py` files).
- **Multi-Group Queries:** Combine searches with `and`, `+`, or `,`.
- **Repo-Specific Persistence:** "Fix" certain files (like `AGENT.md` or `README.md`) to always be included in copies for a specific project.
- **Interactive Selection:** Preview and pick exactly which files to copy using numbers or ranges.
- **Model Selection:** Switch between ChatGPT, Gemini, and Claude as your destination.
- **Auto-Browser:** Automatically opens your selected LLM in a new Firefox tab after copying.
- **Wayland & X11 Support:** Works out of the box on modern Linux systems.
- **Tab Completion:** Full bash completion for commands and files.

## 📦 Installation

Run the following command in your terminal to install `c2llm`:

```bash
curl -sSL https://github.com/tzencirkiran/c2llm/main/install.sh | bash
```

*(Or manual installation)*:
1. Clone this repo.
2. Run `./install.sh`.

## 🛠 Usage

### Basic Search
```bash
c2llm python auth                     # Find Python files with 'auth' in path
c2llm main.py, utils.py               # Copy two specific files
c2llm js ui + python logic            # Combine JS UI and Python logic
```

### Model Selection
```bash
c2llm set gemini             # Switch to Gemini (default is chatgpt)
c2llm set claude             # Switch to Claude
```

### Persistence (Repo-specific)
```bash
c2llm fixed -a AGENT.md      # Always include AGENT.md in this repo
c2llm persistence toggle     # Turn off auto-inclusion temporarily
c2llm status                 # See current repo settings
```

### Browser Automation
```bash
c2llm browser toggle         # Automatically open LLM's web app after copying
```

## ⌨️ Selection Options
After running a search, you will see a numbered list:
- **Press Enter**: Copy all found files.
- **1, 3, 5**: Copy specific files.
- **1-4**: Copy a range of files.
- **n**: Cancel.

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## 📄 License
[MIT](https://choosealicense.com/licenses/mit/)
