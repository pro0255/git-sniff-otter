# Git Sniff Otter Makefile
# Streamlined development workflow

.PHONY: help venv install install-dev clean test lint format run demo check setup

# Default target
help:
	@echo "🔍 Git Sniff Otter - Development Commands"
	@echo "========================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup      - Complete setup (venv + install + config)"
	@echo "  make venv       - Create virtual environment"
	@echo "  make install    - Install dependencies"
	@echo "  make install-dev- Install with development dependencies"
	@echo ""
	@echo "Development Commands:"
	@echo "  make lint       - Run linting (black, flake8, mypy)"
	@echo "  make format     - Format code with black"
	@echo "  make test       - Run tests"
	@echo "  make check      - Run all checks (lint + test)"
	@echo ""
	@echo "Usage Commands:"
	@echo "  make demo       - Run the demo script"
	@echo "  make run ARGS=  - Run git-sniff-otter with arguments"
	@echo "  make validate REPOS= - Validate repository paths"
	@echo "  make test-slack - Test Slack connection"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean      - Clean up build artifacts and cache"
	@echo "  make config     - Create .env from example"
	@echo "  make requirements - Update requirements.txt"
	@echo ""
	@echo "Examples:"
	@echo "  make run ARGS=\"analyze --repos /path/to/repo --days 7\""
	@echo "  make validate REPOS=\"/path/to/repo1 /path/to/repo2\""

# Python and virtual environment settings
PYTHON = python3
VENV_DIR = venv
VENV_ACTIVATE = $(VENV_DIR)/bin/activate
PIP = $(VENV_DIR)/bin/pip
PYTHON_VENV = $(VENV_DIR)/bin/python

# Check if virtual environment exists
VENV_EXISTS = $(shell test -d $(VENV_DIR) && echo 1 || echo 0)

# Complete setup - one command to get everything ready
setup: venv install config
	@echo "🎉 Setup complete! Next steps:"
	@echo "1. Edit .env with your API keys"
	@echo "2. Run: make demo"
	@echo "3. Run: make test-slack"

# Create virtual environment
venv:
	@if [ $(VENV_EXISTS) -eq 0 ]; then \
		echo "📦 Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "✅ Virtual environment created in $(VENV_DIR)"; \
	else \
		echo "✅ Virtual environment already exists"; \
	fi

# Install production dependencies
install: venv
	@echo "📥 Installing dependencies..."
	@. $(VENV_ACTIVATE) && $(PIP) install --upgrade pip
	@. $(VENV_ACTIVATE) && $(PIP) install -r requirements.txt
	@echo "✅ Dependencies installed"

# Install development dependencies
install-dev: venv
	@echo "📥 Installing development dependencies..."
	@. $(VENV_ACTIVATE) && $(PIP) install --upgrade pip
	@. $(VENV_ACTIVATE) && $(PIP) install -r requirements-dev.txt
	@echo "✅ Development dependencies installed"

# Create .env file from example
config:
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env from example..."; \
		cp config.env.example .env; \
		echo "✅ .env file created. Please edit it with your API keys."; \
	else \
		echo "✅ .env file already exists"; \
	fi

# Code formatting
format: venv
	@echo "🎨 Formatting code..."
	@. $(VENV_ACTIVATE) && black .
	@. $(VENV_ACTIVATE) && isort .
	@echo "✅ Code formatted"

# Linting
lint: venv
	@echo "🔍 Running linters..."
	@. $(VENV_ACTIVATE) && black --check .
	@. $(VENV_ACTIVATE) && flake8 . --max-line-length=88 --extend-ignore=E203,W503
	@. $(VENV_ACTIVATE) && mypy git_sniff_otter --ignore-missing-imports
	@echo "✅ Linting passed"

# Run tests
test: venv
	@echo "🧪 Running tests..."
	@. $(VENV_ACTIVATE) && $(PYTHON_VENV) -m pytest tests/ -v --cov=git_sniff_otter
	@echo "✅ Tests completed"

# Run all checks
check: lint test
	@echo "✅ All checks passed"

# Run the demo
demo: venv
	@echo "🎬 Running demo..."
	@. $(VENV_ACTIVATE) && $(PYTHON_VENV) demo.py

# Run git-sniff-otter with arguments
run: venv
	@if [ -z "$(ARGS)" ]; then \
		echo "❌ Please provide ARGS. Example: make run ARGS=\"--help\""; \
		exit 1; \
	fi
	@echo "🚀 Running git-sniff-otter $(ARGS)"
	@. $(VENV_ACTIVATE) && $(PYTHON_VENV) main.py $(ARGS)

# Validate repositories
validate: venv
	@if [ -z "$(REPOS)" ]; then \
		echo "❌ Please provide REPOS. Example: make validate REPOS=\"/path/to/repo\""; \
		exit 1; \
	fi
	@echo "🔍 Validating repositories: $(REPOS)"
	@. $(VENV_ACTIVATE) && $(PYTHON_VENV) main.py validate-repos $(REPOS)

# Test Slack connection
test-slack: venv
	@echo "🧪 Testing Slack connection..."
	@. $(VENV_ACTIVATE) && $(PYTHON_VENV) main.py test-slack

# Clean up build artifacts and cache
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@echo "✅ Cleanup complete"

# Clean everything including virtual environment
clean-all: clean
	@echo "🧹 Removing virtual environment..."
	@rm -rf $(VENV_DIR)
	@echo "✅ Complete cleanup finished"

# Update requirements.txt (for development)
requirements: venv
	@echo "📝 Updating requirements.txt..."
	@. $(VENV_ACTIVATE) && $(PIP) freeze | grep -v "pkg-resources" > requirements.txt
	@echo "✅ requirements.txt updated"

# Install the package in development mode
install-editable: venv
	@echo "📦 Installing package in editable mode..."
	@. $(VENV_ACTIVATE) && $(PIP) install -e .
	@echo "✅ Package installed in editable mode"

# Quick development setup
dev-setup: venv install-dev config install-editable
	@echo "🎉 Development setup complete!"
	@echo "Virtual environment: $(VENV_DIR)"
	@echo "Activate with: source $(VENV_ACTIVATE)"

# Check if required tools are installed
check-tools:
	@echo "🔧 Checking required tools..."
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed."; exit 1; }
	@command -v git >/dev/null 2>&1 || { echo "❌ Git is required but not installed."; exit 1; }
	@command -v gitinspector >/dev/null 2>&1 || echo "⚠️  GitInspector not found. Install it or set GITINSPECTOR_PATH in .env"
	@echo "✅ Tool check complete"

# Show current environment info
info:
	@echo "🔍 Git Sniff Otter Environment Info"
	@echo "===================================="
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "Virtual Environment: $(VENV_DIR) (exists: $(VENV_EXISTS))"
	@echo "Working Directory: $(shell pwd)"
	@echo "Git: $(shell git --version)"
	@echo "GitInspector: $(shell command -v gitinspector >/dev/null 2>&1 && echo "Found" || echo "Not found")"
	@if [ -f .env ]; then echo "Config: .env exists"; else echo "Config: .env missing"; fi
