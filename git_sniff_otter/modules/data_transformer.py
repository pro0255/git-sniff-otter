"""Data transformation module for preparing repository data for LLM analysis."""

from collections import Counter
from datetime import datetime
from typing import Any, Dict, List

from .data_collector import CommitData, RepositoryData


class AuthorStats:
    """Statistics for a single author across all repositories."""

    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.total_commits = 0
        self.total_insertions = 0
        self.total_deletions = 0
        self.total_files_changed = 0
        self.repositories = set()
        self.file_types = Counter()
        self.commit_messages = []
        self.first_commit_date = None
        self.last_commit_date = None

    def add_commit(self, commit: CommitData, repo_name: str):
        """Add commit data to author statistics."""
        self.total_commits += 1
        self.total_insertions += commit.insertions
        self.total_deletions += commit.deletions
        self.total_files_changed += len(commit.files_changed)
        self.repositories.add(repo_name)
        self.commit_messages.append(commit.message)

        # Track file types
        for file_path in commit.files_changed:
            if "." in file_path:
                extension = file_path.split(".")[-1].lower()
                self.file_types[extension] += 1

        # Track date range
        if self.first_commit_date is None or commit.date < self.first_commit_date:
            self.first_commit_date = commit.date
        if self.last_commit_date is None or commit.date > self.last_commit_date:
            self.last_commit_date = commit.date

    def to_dict(self) -> Dict[str, Any]:
        """Convert author stats to dictionary."""
        return {
            "name": self.name,
            "email": self.email,
            "total_commits": self.total_commits,
            "total_insertions": self.total_insertions,
            "total_deletions": self.total_deletions,
            "net_lines": self.total_insertions - self.total_deletions,
            "total_files_changed": self.total_files_changed,
            "repositories": list(self.repositories),
            "top_file_types": dict(self.file_types.most_common(5)),
            "recent_commit_messages": self.commit_messages[:10],  # Last 10 commits
            "first_commit_date": self.first_commit_date.isoformat()
            if self.first_commit_date
            else None,
            "last_commit_date": self.last_commit_date.isoformat()
            if self.last_commit_date
            else None,
            "active_days": self._calculate_active_days(),
        }

    def _calculate_active_days(self) -> int:
        """Calculate number of days between first and last commit."""
        if self.first_commit_date and self.last_commit_date:
            return (self.last_commit_date - self.first_commit_date).days + 1
        return 0


class RepositoryStats:
    """Statistics for a single repository."""

    def __init__(self, repo_data: RepositoryData):
        self.name = repo_data.name
        self.path = repo_data.path
        self.total_commits = len(repo_data.commits)
        self.unique_authors = set()
        self.total_insertions = 0
        self.total_deletions = 0
        self.total_files_changed = set()
        self.file_types = Counter()
        self.commit_timeline = []

        for commit in repo_data.commits:
            self.unique_authors.add(commit.author_email)
            self.total_insertions += commit.insertions
            self.total_deletions += commit.deletions
            self.total_files_changed.update(commit.files_changed)

            # Track file types
            for file_path in commit.files_changed:
                if "." in file_path:
                    extension = file_path.split(".")[-1].lower()
                    self.file_types[extension] += 1

            self.commit_timeline.append(
                {
                    "date": commit.date.isoformat(),
                    "author": commit.author_name,
                    "message": commit.message[:100],  # Truncate long messages
                    "changes": commit.lines_changed,
                }
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert repository stats to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "total_commits": self.total_commits,
            "unique_authors": len(self.unique_authors),
            "total_insertions": self.total_insertions,
            "total_deletions": self.total_deletions,
            "net_lines": self.total_insertions - self.total_deletions,
            "total_files_changed": len(self.total_files_changed),
            "top_file_types": dict(self.file_types.most_common(10)),
            "recent_commits": self.commit_timeline[:20],  # Last 20 commits
        }


class TransformedData:
    """Container for all transformed data ready for LLM processing."""

    def __init__(self):
        self.overall_stats = {}
        self.repository_stats = []
        self.author_stats = []
        self.time_window = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert all transformed data to dictionary."""
        return {
            "overall_stats": self.overall_stats,
            "repository_stats": [repo.to_dict() for repo in self.repository_stats],
            "author_stats": [author.to_dict() for author in self.author_stats],
            "time_window": self.time_window,
            "summary": self._generate_summary(),
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a high-level summary of the data."""
        total_commits = sum(repo.total_commits for repo in self.repository_stats)
        total_authors = len(self.author_stats)
        total_repositories = len(self.repository_stats)

        return {
            "total_commits": total_commits,
            "total_authors": total_authors,
            "total_repositories": total_repositories,
            "avg_commits_per_author": total_commits / total_authors
            if total_authors > 0
            else 0,
            "avg_commits_per_repo": total_commits / total_repositories
            if total_repositories > 0
            else 0,
        }


class DataTransformer:
    """Main data transformation class."""

    def __init__(self, start_date: datetime, end_date: datetime):
        self.start_date = start_date
        self.end_date = end_date

    def transform(self, repository_data_list: List[RepositoryData]) -> TransformedData:
        """Transform raw repository data into structured format for LLM."""
        transformed = TransformedData()

        # Set time window information
        transformed.time_window = {
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "duration_days": (self.end_date - self.start_date).days,
        }

        # Process repository statistics
        transformed.repository_stats = [
            RepositoryStats(repo_data) for repo_data in repository_data_list
        ]

        # Aggregate author statistics across all repositories
        author_map = {}

        for repo_data in repository_data_list:
            for commit in repo_data.commits:
                author_key = f"{commit.author_name}:{commit.author_email}"

                if author_key not in author_map:
                    author_map[author_key] = AuthorStats(
                        commit.author_name, commit.author_email
                    )

                author_map[author_key].add_commit(commit, repo_data.name)

        transformed.author_stats = list(author_map.values())

        # Sort authors by total commits (descending)
        transformed.author_stats.sort(key=lambda a: a.total_commits, reverse=True)

        # Generate overall statistics
        transformed.overall_stats = self._calculate_overall_stats(
            transformed.repository_stats, transformed.author_stats
        )

        return transformed

    def _calculate_overall_stats(
        self, repo_stats: List[RepositoryStats], author_stats: List[AuthorStats]
    ) -> Dict[str, Any]:
        """Calculate overall statistics across all repositories and authors."""
        total_commits = sum(repo.total_commits for repo in repo_stats)
        total_insertions = sum(repo.total_insertions for repo in repo_stats)
        total_deletions = sum(repo.total_deletions for repo in repo_stats)

        # Aggregate file types across all repositories
        all_file_types = Counter()
        for repo in repo_stats:
            all_file_types.update(repo.file_types)

        # Find most active authors
        top_authors = author_stats[:5]  # Top 5 authors by commits

        return {
            "total_commits": total_commits,
            "total_insertions": total_insertions,
            "total_deletions": total_deletions,
            "net_lines": total_insertions - total_deletions,
            "total_repositories": len(repo_stats),
            "total_authors": len(author_stats),
            "top_file_types": dict(all_file_types.most_common(10)),
            "top_authors_by_commits": [
                {"name": author.name, "commits": author.total_commits}
                for author in top_authors
            ],
            "avg_commits_per_day": total_commits
            / max((self.end_date - self.start_date).days, 1),
        }
