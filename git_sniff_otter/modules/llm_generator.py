"""LLM integration module for generating human-readable reports."""

import json
from typing import Any, Dict

try:
    from openai import OpenAI
except ImportError:
    # Handle case where OpenAI library is not installed
    print("Warning: OpenAI library not installed. LLM features may not work.")

    class MockOpenAI:
        def __init__(self, api_key: str):
            self.api_key = api_key

        @property
        def chat(self):
            class MockCompletions:
                def create(self, **kwargs):
                    class MockChoice:
                        def __init__(self):
                            self.message = type(
                                "Message", (), {"content": "Mock response from LLM"}
                            )()

                    return type("Response", (), {"choices": [MockChoice()]})()

            class MockChat:
                def __init__(self):
                    self.completions = MockCompletions()

            return MockChat()

    OpenAI = MockOpenAI  # type: ignore

from ..config import Config
from .data_transformer import TransformedData


class LLMReportGenerator:
    """Generates reports using Large Language Models."""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)

    def generate_report(self, transformed_data: TransformedData) -> str:
        """Generate a comprehensive report from transformed data."""

        # Prepare the data for the LLM
        data_dict = transformed_data.to_dict()

        # Create the system prompt
        system_prompt = self._create_system_prompt()

        # Create the user prompt with data
        user_prompt = self._create_user_prompt(data_dict)

        try:
            response = self.client.chat.completions.create(
                model=self.config.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=4000,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            return content.strip() if content else "No response from LLM"

        except Exception as e:
            print(f"Error generating LLM report: {e}")
            # Return a fallback report
            return self._generate_fallback_report(data_dict)

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the LLM."""
        return """You are a technical report writer specializing in Git repository analysis. 
        
Your task is to create comprehensive, well-structured reports based on Git repository statistics and commit data. The reports should be:

1. **Professional and Clear**: Use clear, professional language suitable for engineering teams and management
2. **Well-Structured**: Organize information logically with clear sections and subsections
3. **Insightful**: Provide meaningful analysis, not just raw statistics
4. **Actionable**: Where appropriate, suggest insights or observations that could be useful

Report Structure:
- Executive Summary (2-3 sentences)
- Overall Repository Activity
- Repository-Specific Analysis
- Individual Contributor Analysis
- Key Insights and Observations

Use markdown formatting for better readability. Focus on trends, patterns, and notable contributions rather than just listing numbers."""

    def _create_user_prompt(self, data: Dict[str, Any]) -> str:
        """Create the user prompt with the data."""
        time_window = data.get("time_window", {})
        start_date = time_window.get("start_date", "Unknown")
        end_date = time_window.get("end_date", "Unknown")
        duration = time_window.get("duration_days", 0)

        prompt = f"""Please generate a comprehensive Git repository analysis report for the period from {start_date} to {end_date} ({duration} days).

Here is the data to analyze:

## Overall Statistics
{json.dumps(data.get("overall_stats", {}), indent=2)}

## Summary
{json.dumps(data.get("summary", {}), indent=2)}

## Repository Details
{json.dumps(data.get("repository_stats", []), indent=2)}

## Author Contributions
{json.dumps(data.get("author_stats", []), indent=2)}

## Time Window
{json.dumps(time_window, indent=2)}

Please create a report that includes:
1. An executive summary highlighting the most important findings
2. Overall activity analysis (total commits, contributors, repositories)
3. Per-repository breakdown with key metrics
4. Individual contributor analysis with their key contributions
5. Notable patterns, trends, or insights from the data

Make the report engaging and informative for both technical and non-technical stakeholders."""

        return prompt

    def _generate_fallback_report(self, data: Dict[str, Any]) -> str:
        """Generate a basic fallback report if LLM fails."""
        overall_stats = data.get("overall_stats", {})
        summary = data.get("summary", {})
        time_window = data.get("time_window", {})

        start_date = time_window.get("start_date", "Unknown")
        end_date = time_window.get("end_date", "Unknown")

        report = f"""# Git Repository Analysis Report
        
## Executive Summary
Analysis of {summary.get("total_repositories", 0)} repositories from {start_date} to {end_date}.

## Overall Activity
- **Total Commits**: {overall_stats.get("total_commits", 0)}
- **Total Contributors**: {summary.get("total_authors", 0)}
- **Total Repositories**: {summary.get("total_repositories", 0)}
- **Lines Added**: {overall_stats.get("total_insertions", 0):,}
- **Lines Removed**: {overall_stats.get("total_deletions", 0):,}
- **Net Lines Changed**: {overall_stats.get("net_lines", 0):,}

## Repository Summary
"""

        # Add repository details
        repo_stats = data.get("repository_stats", [])
        for repo in repo_stats[:5]:  # Top 5 repositories
            report += f"""
### {repo.get("name", "Unknown")}
- Commits: {repo.get("total_commits", 0)}
- Contributors: {repo.get("unique_authors", 0)}
- Files Changed: {repo.get("total_files_changed", 0)}
- Net Lines: {repo.get("net_lines", 0):,}
"""

        # Add author summary
        report += "\n## Top Contributors\n"
        author_stats = data.get("author_stats", [])
        for i, author in enumerate(author_stats[:5], 1):
            report += f"""
{i}. **{author.get("name", "Unknown")}**
   - Commits: {author.get("total_commits", 0)}
   - Lines Added: {author.get("total_insertions", 0):,}
   - Lines Removed: {author.get("total_deletions", 0):,}
   - Files Changed: {author.get("total_files_changed", 0)}
"""

        report += "\n---\n*Report generated by Git Sniff Otter*"

        return report
