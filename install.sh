#!/bin/bash

# Git Sniff Otter Installation Script

set -e

echo "🔍 Git Sniff Otter Installation Script"
echo "======================================="

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Check if GitInspector is installed
if ! command -v gitinspector &> /dev/null; then
    echo "⚠️  Warning: GitInspector not found in PATH"
    echo "   Please install GitInspector:"
    echo "   - macOS: brew install gitinspector"
    echo "   - Ubuntu/Debian: apt-get install gitinspector"
    echo "   - Or set GITINSPECTOR_PATH in your .env file"
    echo ""
else
    echo "✅ GitInspector found: $(which gitinspector)"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "🎉 Installation completed!"
echo ""
echo "Next steps:"
echo "1. Copy config.env.example to .env:"
echo "   cp config.env.example .env"
echo ""
echo "2. Edit .env with your API keys and configuration"
echo ""
echo "3. Test the installation:"
echo "   python3 main.py --help"
echo ""
echo "4. Validate your repositories:"
echo "   python3 main.py validate-repos /path/to/your/repo"
echo ""
echo "5. Test Slack connection:"
echo "   python3 main.py test-slack"
echo ""
echo "Happy analyzing! 🔍✨"
