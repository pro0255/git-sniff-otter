# 🔍 Git Sniff Otter

An automated Git repository analysis and reporting tool that uses LLM-powered insights to generate comprehensive reports and delivers them to Slack.

## 📋 Features

- **Multi-Repository Analysis**: Analyze multiple Git repositories simultaneously
- **Flexible Time Windows**: Analyze activity for specific date ranges or relative periods (last week, month, etc.)
- **Comprehensive Statistics**: Combines GitInspector data with detailed commit analysis
- **LLM-Powered Reports**: Uses OpenAI GPT models to generate human-readable, insightful reports
- **Slack Integration**: Automatically delivers reports to Slack channels via webhook or bot token
- **Rich CLI Interface**: Beautiful command-line interface with progress indicators and validation

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **GitInspector** tool installed and available in your PATH
   ```bash
   # Install GitInspector (example for macOS with Homebrew)
   brew install gitinspector
   ```
3. **OpenAI API Key** for LLM report generation
4. **Slack Integration** (webhook URL or bot token)

### Installation

#### Quick Setup (Recommended)

```bash
git clone <repository-url>
cd git-sniff-otter
make setup
```

This will:
- Create a virtual environment
- Install all dependencies
- Create a `.env` configuration file from the example

#### Manual Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd git-sniff-otter
   ```

2. Create virtual environment and install dependencies:
   ```bash
   make venv
   make install
   ```

3. Set up configuration:
   ```bash
   make config
   # Edit .env with your API keys and configuration
   ```

#### Development Setup

For development with additional tools (linting, testing, pre-commit hooks):

```bash
make dev-setup
```

### Configuration

Create a `.env` file with your configuration:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4

# Slack Configuration (choose one method)
SLACK_TOKEN=your_slack_bot_token_here
# OR
SLACK_WEBHOOK_URL=your_slack_webhook_url_here

SLACK_CHANNEL=#your-channel-name

# Optional: GitInspector path if not in system PATH
GITINSPECTOR_PATH=gitinspector
```

## 📖 Usage

### Make Commands (Recommended)

The Makefile provides convenient commands for common tasks:

```bash
# Get help with all available commands
make help

# Run a quick demo
make demo

# Analyze repositories (using virtual environment automatically)
make run ARGS="analyze --repos /path/to/repo1 --repos /path/to/repo2"

# Validate repository paths
make validate REPOS="/path/to/repo1 /path/to/repo2"

# Test Slack connection
make test-slack
```

### Direct Python Usage

If you prefer to run Python directly (remember to activate the virtual environment first):

```bash
# Activate virtual environment
source venv/bin/activate

# Basic analysis for the last 7 days
python main.py analyze --repos /path/to/repo1 --repos /path/to/repo2

# Custom time range (last 30 days)
python main.py analyze --repos /path/to/repo1 --days 30

# Specific date range
python main.py analyze --repos /path/to/repo1 --start-date 2024-01-01 --end-date 2024-01-31

# Advanced options
python main.py analyze \
  --repos /path/to/repo1 \
  --repos /path/to/repo2 \
  --days 14 \
  --channel "#engineering-reports" \
  --save-report report.md \
  --config custom-config.env

# Dry run (generate report without sending)
python main.py analyze --repos /path/to/repo1 --dry-run

# Validate repositories
python main.py validate-repos /path/to/repo1 /path/to/repo2

# Test Slack connection
python main.py test-slack
```

## 🔧 Command Reference

### `analyze` Command

Main command for analyzing repositories and generating reports.

**Options:**
- `--repos, -r`: Git repository paths (can be specified multiple times) **[Required]**
- `--days, -d`: Number of days to analyze (default: 7)
- `--start-date`: Start date for analysis (YYYY-MM-DD format)
- `--end-date`: End date for analysis (YYYY-MM-DD format)
- `--config, -c`: Path to configuration file
- `--channel`: Slack channel to send report to (overrides config)
- `--dry-run`: Generate report but don't send to Slack
- `--save-report`: Save the generated report to a file

### `test-slack` Command

Test your Slack connection configuration.

**Options:**
- `--config, -c`: Path to configuration file

### `validate-repos` Command

Validate that specified paths are valid Git repositories.

**Arguments:**
- Repository paths to validate

## 📊 Report Contents

The generated reports include:

1. **Executive Summary**: High-level overview of repository activity
2. **Overall Statistics**: Total commits, contributors, lines changed, etc.
3. **Repository Breakdown**: Per-repository analysis with key metrics
4. **Individual Contributors**: Detailed analysis of each developer's contributions
5. **Insights and Patterns**: LLM-generated observations and trends

## 🔒 Security Notes

- **API Keys**: Never commit API keys to version control. Use environment variables or config files that are gitignored.
- **Slack Tokens**: Store Slack tokens securely and limit their permissions to only what's needed.
- **Repository Access**: Ensure the tool has appropriate read access to the repositories you want to analyze.

## 🛠️ Troubleshooting

### Common Issues

1. **GitInspector not found**
   ```
   Error: gitinspector command not found
   ```
   **Solution**: Install GitInspector or set the `GITINSPECTOR_PATH` environment variable.

2. **Repository not accessible**
   ```
   Error: Path is not a git repository
   ```
   **Solution**: Ensure the path points to a valid Git repository with a `.git` directory.

3. **Slack authentication failed**
   ```
   Error: Slack connection failed
   ```
   **Solution**: Verify your Slack token or webhook URL, and ensure the bot has permission to post to the channel.

4. **OpenAI API errors**
   ```
   Error: OpenAI API request failed
   ```
   **Solution**: Check your API key and ensure you have sufficient credits/quota.

### Debug Mode

For verbose output, you can modify the configuration to include debug logging.

## 🏗️ Architecture

The tool follows a modular pipeline architecture:

1. **Input Module** (`config.py`): Handles configuration and validation
2. **Data Collection Module** (`data_collector.py`): Executes GitInspector and Git commands
3. **Data Transformation Module** (`data_transformer.py`): Structures data for LLM processing
4. **LLM Integration Module** (`llm_generator.py`): Generates reports using OpenAI
5. **Output Module** (`slack_sender.py`): Delivers reports to Slack

## 🛠️ Development

### Development Commands

```bash
# Set up development environment
make dev-setup

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Run all checks (lint + test)
make check

# Clean up build artifacts
make clean

# Get environment info
make info
```

### Pre-commit Hooks

Install pre-commit hooks for automatic code quality checks:

```bash
# After running make dev-setup
source venv/bin/activate
pre-commit install
```

Now code will be automatically formatted and checked before each commit.

## 🤝 Contributing

1. Fork the repository
2. Set up development environment: `make dev-setup`
3. Create a feature branch (`git checkout -b feature/amazing-feature`)
4. Make your changes and ensure tests pass: `make check`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Look through existing GitHub issues
3. Create a new issue with detailed information about your problem

---

*Happy analyzing! 🔍✨*
