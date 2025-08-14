#!/usr/bin/env python3
"""Demo script showing Git Sniff Otter functionality."""

import os
import sys
from datetime import datetime, timedelta

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_sniff_otter.config import Config
from git_sniff_otter.modules.data_collector import DataCollector
from git_sniff_otter.modules.data_transformer import DataTransformer


def demo_data_collection():
    """Demo the data collection functionality."""
    print("🔍 Demo: Data Collection")
    print("=" * 50)

    # Create a demo config (you'll need to adjust the repository path)
    current_repo = os.path.dirname(os.path.abspath(__file__))

    config = Config(
        openai_api_key="demo-key",
        repository_paths=[current_repo],  # Use current repository as demo
        time_window_days=30,
        slack_channel="#demo",
        slack_token="demo-token",  # Add demo token to satisfy validation
    )

    print(f"Analyzing repository: {current_repo}")
    print(f"Time window: last {config.time_window_days} days")

    try:
        collector = DataCollector(config)
        repo_data = collector.collect_all_data()

        if repo_data:
            repo = repo_data[0]
            print("\n✅ Data collected successfully!")
            print(f"Repository: {repo.name}")
            print(f"Commits found: {len(repo.commits)}")

            if repo.commits:
                latest_commit = repo.commits[0]
                print(f"Latest commit: {latest_commit.message[:50]}...")
                print(f"Author: {latest_commit.author_name}")
                print(f"Date: {latest_commit.date.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("❌ No data collected")

    except Exception as e:
        print(f"⚠️  Demo limitation: {e}")
        print("Note: This demo requires a valid Git repository")


def demo_data_transformation():
    """Demo the data transformation functionality."""
    print("\n🔄 Demo: Data Transformation")
    print("=" * 50)

    # Create mock data for transformation demo
    from git_sniff_otter.modules.data_collector import CommitData, RepositoryData

    # Create a mock commit
    class MockCommit:
        def __init__(self):
            self.hexsha = "abc123def456"
            self.author = type(
                "obj", (object,), {"name": "Demo User", "email": "demo@example.com"}
            )
            self.message = (
                "Add awesome new feature\n\nThis commit adds functionality..."
            )
            self.committed_datetime = datetime.now() - timedelta(days=1)
            self.stats = type(
                "obj",
                (object,),
                {
                    "files": {"demo.py": {}, "README.md": {}},
                    "total": {"insertions": 50, "deletions": 10, "lines": 60},
                },
            )

    mock_commit = MockCommit()
    commit_data = CommitData(mock_commit)

    repo_data = RepositoryData("/demo/repo", "demo-repo")
    repo_data.commits = [commit_data]

    # Transform the data
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()

    transformer = DataTransformer(start_date, end_date)
    transformed_data = transformer.transform([repo_data])

    print("✅ Data transformation completed!")
    print(f"Repositories: {len(transformed_data.repository_stats)}")
    print(f"Authors: {len(transformed_data.author_stats)}")
    print(f"Time window: {transformed_data.time_window['duration_days']} days")

    if transformed_data.author_stats:
        author = transformed_data.author_stats[0]
        print("\nSample author stats:")
        print(f"- Name: {author.name}")
        print(f"- Commits: {author.total_commits}")
        print(f"- Lines added: {author.total_insertions}")
        print(f"- Lines removed: {author.total_deletions}")


def demo_report_structure():
    """Demo the report structure without calling the LLM."""
    print("\n📄 Demo: Report Structure")
    print("=" * 50)

    sample_report = """# Git Repository Analysis Report

## Executive Summary
Analysis of 2 repositories over the past 7 days shows moderate development activity with 15 commits from 3 contributors.

## Overall Activity
- **Total Commits**: 15
- **Total Contributors**: 3  
- **Total Repositories**: 2
- **Lines Added**: 450
- **Lines Removed**: 120
- **Net Lines Changed**: +330

## Repository Breakdown

### project-alpha
- Commits: 10
- Contributors: 2
- Files Changed: 8
- Net Lines: +250

### project-beta  
- Commits: 5
- Contributors: 2
- Files Changed: 4
- Net Lines: +80

## Individual Contributors

### Alice Developer
- **Commits**: 8 (53% of total)
- **Lines Added**: 320
- **Lines Removed**: 50
- **Key Contributions**: Feature development, bug fixes
- **Most Active In**: project-alpha

### Bob Engineer
- **Commits**: 5 (33% of total)
- **Lines Added**: 100
- **Lines Removed**: 60
- **Key Contributions**: Code refactoring, documentation
- **Most Active In**: project-beta

### Charlie Maintainer
- **Commits**: 2 (13% of total)
- **Lines Added**: 30
- **Lines Removed**: 10
- **Key Contributions**: CI/CD improvements
- **Most Active In**: project-alpha

## Key Insights

- Alice shows the highest productivity with consistent commits
- Bob focused on code quality improvements
- Both repositories show healthy development activity
- No concerning patterns detected

---
*Report generated by Git Sniff Otter*
"""

    print("Sample report structure:")
    print(sample_report[:500] + "...")
    print("\n✅ This shows the type of comprehensive reports Git Sniff Otter generates!")


def main():
    """Run all demos."""
    print("🔍 Git Sniff Otter - Demo Script")
    print("=" * 50)
    print("This script demonstrates the capabilities of Git Sniff Otter")
    print("without requiring full configuration.\n")

    demo_data_collection()
    demo_data_transformation()
    demo_report_structure()

    print("\n🎉 Demo completed!")
    print("\nTo use Git Sniff Otter with real data:")
    print("1. Set up your .env file with API keys")
    print("2. Run: python main.py analyze --repos /path/to/repo")
    print("3. Check the generated report in Slack!")


if __name__ == "__main__":
    main()
