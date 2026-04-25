#!/bin/bash

# c2llm Installer Script

set -e

echo "🚀 Installing c2llm..."

# 1. Create bin directory if it doesn't exist
INSTALL_DIR="$HOME/bin"
mkdir -p "$INSTALL_DIR"

# 2. Copy files (assuming run from project root)
cp c2llm.py "$INSTALL_DIR/c2llm.py"
cp c2llm-completion.bash "$INSTALL_DIR/c2llm-completion.bash"
cp LICENSE "$INSTALL_DIR/LICENSE"
chmod +x "$INSTALL_DIR/c2llm.py"

# 3. Create symlink
ln -sf "$INSTALL_DIR/c2llm.py" "$INSTALL_DIR/c2llm"

# 4. Check dependencies
echo "🔍 Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it."
fi

# Detect Display Server and suggest clipboard tool
if [[ "$XDG_SESSION_TYPE" == "wayland" ]]; then
    if ! command -v wl-copy &> /dev/null; then
        echo "💡 Suggestion: Install 'wl-clipboard' for Wayland support."
    fi
else
    if ! command -v xclip &> /dev/null; then
        echo "💡 Suggestion: Install 'xclip' for X11 support."
    fi
fi

# 5. Update .bashrc if necessary
BASHRC="$HOME/.bashrc"
if ! grep -q "c2llm-completion.bash" "$BASHRC"; then
    echo "📝 Adding c2llm to .bashrc..."
    echo "" >> "$BASHRC"
    echo "# c2llm (Code to LLM) settings" >> "$BASHRC"
    echo "export PATH=\"\$HOME/bin:\$PATH\"" >> "$BASHRC"
    echo "source \"\$HOME/bin/c2llm-completion.bash\"" >> "$BASHRC"
else
    echo "✅ c2llm already in .bashrc"
fi

echo "✨ Installation complete!"
echo "🔄 Please run 'source ~/.bashrc' or restart your terminal."
echo "👉 Try it out: c2llm --help"
