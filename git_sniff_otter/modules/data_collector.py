"""Data collection module for gathering Git repository statistics and commit information."""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional

try:
    from git import Commit, Repo
    from git.exc import GitCommandError
except ImportError:
    # Handle case where GitPython is not installed
    print("Warning: GitPython not installed. Some features may not work.")

    class MockCommit:
        def __init__(self):
            self.hexsha = ""
            self.author = type("Author", (), {"name": "", "email": ""})()
            self.message = ""
            self.committed_datetime = None
            self.stats = type(
                "Stats",
                (),
                {"files": {}, "total": {"insertions": 0, "deletions": 0, "lines": 0}},
            )()

    class MockRepo:
        def __init__(self, path: str):
            self.path = path

        def iter_commits(self, **kwargs):
            return []

    Commit = MockCommit  # type: ignore
    Repo = MockRepo  # type: ignore
    GitCommandError = Exception  # type: ignore

from ..config import Config


class GitInspectorData:
    """Container for GitInspector output data."""

    def __init__(self, raw_output: str, json_output: Dict[str, Any]):
        self.raw_output = raw_output
        self.json_output = json_output

    @property
    def authors(self) -> List[Dict[str, Any]]:
        """Get author statistics from GitInspector data."""
        return self.json_output.get("authors", [])

    @property
    def file_types(self) -> Dict[str, Any]:
        """Get file type statistics."""
        return self.json_output.get("file_types", {})

    @property
    def timeline(self) -> List[Dict[str, Any]]:
        """Get timeline data."""
        return self.json_output.get("timeline", [])


class CommitData:
    """Container for commit information."""

    def __init__(self, commit):
        self.sha = commit.hexsha
        self.author_name = commit.author.name
        self.author_email = commit.author.email
        self.message = commit.message.strip()
        self.date = commit.committed_datetime
        self.files_changed = list(commit.stats.files.keys())
        self.insertions = commit.stats.total["insertions"]
        self.deletions = commit.stats.total["deletions"]
        self.lines_changed = commit.stats.total["lines"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert commit data to dictionary."""
        return {
            "sha": self.sha,
            "author_name": self.author_name,
            "author_email": self.author_email,
            "message": self.message,
            "date": self.date.isoformat(),
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "lines_changed": self.lines_changed,
        }


class RepositoryData:
    """Container for all repository data."""

    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
        self.gitinspector_data: Optional[GitInspectorData] = None
        self.commits: List[CommitData] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert repository data to dictionary."""
        return {
            "path": self.path,
            "name": self.name,
            "gitinspector_data": {
                "authors": self.gitinspector_data.authors
                if self.gitinspector_data
                else [],
                "file_types": self.gitinspector_data.file_types
                if self.gitinspector_data
                else {},
                "timeline": self.gitinspector_data.timeline
                if self.gitinspector_data
                else [],
            },
            "commits": [commit.to_dict() for commit in self.commits],
        }


class DataCollector:
    """Main data collection class that orchestrates Git and GitInspector data gathering."""

    def __init__(self, config: Config):
        self.config = config

    def collect_all_data(self) -> List[RepositoryData]:
        """Collect data from all configured repositories."""
        all_repo_data = []

        for repo_path in self.config.repository_paths:
            print(f"Processing repository: {repo_path}")
            repo_data = self._collect_repository_data(repo_path)
            all_repo_data.append(repo_data)

        return all_repo_data

    def _collect_repository_data(self, repo_path: str) -> RepositoryData:
        """Collect data for a single repository."""
        repo_name = os.path.basename(repo_path)
        repo_data = RepositoryData(repo_path, repo_name)

        # Collect GitInspector data
        try:
            repo_data.gitinspector_data = self._run_gitinspector(repo_path)
        except Exception as e:
            print(f"Warning: Failed to run GitInspector on {repo_path}: {e}")

        # Collect commit data
        try:
            repo_data.commits = self._collect_commits(repo_path)
        except Exception as e:
            print(f"Warning: Failed to collect commits from {repo_path}: {e}")

        return repo_data

    def _run_gitinspector(self, repo_path: str) -> GitInspectorData:
        """Run GitInspector on a repository and parse the output."""
        start_date = self.config.analysis_start_date.strftime("%Y-%m-%d")
        end_date = self.config.analysis_end_date.strftime("%Y-%m-%d")

        # Run GitInspector with JSON output
        cmd = [
            self.config.gitinspector_path,
            "--format=json",
            f"--since={start_date}",
            f"--until={end_date}",
            repo_path,
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, cwd=repo_path
            )

            # Parse JSON output
            json_data = json.loads(result.stdout)
            return GitInspectorData(result.stdout, json_data)

        except subprocess.CalledProcessError:
            # If JSON format fails, try with text format
            cmd_text = [
                self.config.gitinspector_path,
                f"--since={start_date}",
                f"--until={end_date}",
                repo_path,
            ]

            result = subprocess.run(
                cmd_text, capture_output=True, text=True, check=True, cwd=repo_path
            )

            # Create minimal JSON structure from text output
            json_data = {
                "authors": [],
                "file_types": {},
                "timeline": [],
                "raw_text": result.stdout,
            }

            return GitInspectorData(result.stdout, json_data)

        except json.JSONDecodeError:
            # Fallback to empty structure if JSON parsing fails
            json_data = {
                "authors": [],
                "file_types": {},
                "timeline": [],
                "raw_text": result.stdout,
            }
            return GitInspectorData(result.stdout, json_data)

    def _collect_commits(self, repo_path: str) -> List[CommitData]:
        """Collect commit data from a Git repository."""
        repo = Repo(repo_path)
        commits = []

        start_date = self.config.analysis_start_date
        end_date = self.config.analysis_end_date

        try:
            # Get commits from all branches within the time window
            for commit in repo.iter_commits(all=True, since=start_date, until=end_date):
                commit_data = CommitData(commit)
                commits.append(commit_data)

        except GitCommandError as e:
            print(f"Warning: Git command error in {repo_path}: {e}")

        # Sort commits by date (newest first)
        commits.sort(key=lambda c: c.date, reverse=True)

        return commits
