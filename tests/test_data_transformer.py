"""Tests for data transformation module."""

from datetime import datetime, timedelta

from git_sniff_otter.modules.data_collector import CommitData, RepositoryData
from git_sniff_otter.modules.data_transformer import (
    AuthorStats,
    DataTransformer,
    RepositoryStats,
)


class MockCommit:
    """Mock commit for testing."""

    def __init__(
        self,
        author_name="Test Author",
        author_email="test@example.com",
        message="Test commit",
        insertions=10,
        deletions=5,
        files=None,
    ):
        self.hexsha = "abc123"
        self.author = type(
            "obj", (object,), {"name": author_name, "email": author_email}
        )
        self.message = message
        self.committed_datetime = datetime.now()
        self.stats = type(
            "obj",
            (object,),
            {
                "files": files or {"test.py": {}},
                "total": {
                    "insertions": insertions,
                    "deletions": deletions,
                    "lines": insertions + deletions,
                },
            },
        )


class TestAuthorStats:
    """Test cases for AuthorStats class."""

    def test_author_stats_creation(self):
        """Test basic author stats creation."""
        author = AuthorStats("John Doe", "john@example.com")
        assert author.name == "John Doe"
        assert author.email == "john@example.com"
        assert author.total_commits == 0

    def test_add_commit(self):
        """Test adding commit to author stats."""
        author = AuthorStats("John Doe", "john@example.com")
        mock_commit = MockCommit()
        commit_data = CommitData(mock_commit)

        author.add_commit(commit_data, "test-repo")

        assert author.total_commits == 1
        assert author.total_insertions == 10
        assert author.total_deletions == 5
        assert "test-repo" in author.repositories

    def test_to_dict(self):
        """Test converting author stats to dictionary."""
        author = AuthorStats("John Doe", "john@example.com")
        mock_commit = MockCommit(files={"test.py": {}, "main.js": {}})
        commit_data = CommitData(mock_commit)

        author.add_commit(commit_data, "test-repo")
        result = author.to_dict()

        assert result["name"] == "John Doe"
        assert result["total_commits"] == 1
        assert result["net_lines"] == 5  # 10 - 5


class TestRepositoryStats:
    """Test cases for RepositoryStats class."""

    def test_repository_stats_creation(self):
        """Test creating repository stats from repository data."""
        repo_data = RepositoryData("/test/repo", "test-repo")

        # Add a mock commit
        mock_commit = MockCommit()
        commit_data = CommitData(mock_commit)
        repo_data.commits = [commit_data]

        repo_stats = RepositoryStats(repo_data)

        assert repo_stats.name == "test-repo"
        assert repo_stats.total_commits == 1
        assert repo_stats.total_insertions == 10


class TestDataTransformer:
    """Test cases for DataTransformer class."""

    def test_transform_data(self):
        """Test transforming repository data."""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        transformer = DataTransformer(start_date, end_date)

        # Create mock repository data
        repo_data = RepositoryData("/test/repo", "test-repo")
        mock_commit = MockCommit()
        commit_data = CommitData(mock_commit)
        repo_data.commits = [commit_data]

        # Transform the data
        result = transformer.transform([repo_data])

        assert len(result.repository_stats) == 1
        assert len(result.author_stats) == 1
        assert result.time_window["duration_days"] == 7

        # Check summary
        summary = result._generate_summary()
        assert summary["total_commits"] == 1
        assert summary["total_repositories"] == 1
        assert summary["total_authors"] == 1
