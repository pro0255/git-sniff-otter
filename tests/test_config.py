"""Tests for configuration module."""

from datetime import datetime

import pytest

from git_sniff_otter.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_creation(self):
        """Test basic config creation."""
        config = Config(
            openai_api_key="test-key",
            repository_paths=["."],  # Current directory should be a git repo
            slack_channel="#test",
            slack_token="test-token",
        )

        assert config.openai_api_key == "test-key"
        assert config.slack_channel == "#test"
        assert config.llm_model == "gpt-4"  # Default value
        assert config.time_window_days == 7  # Default value

    def test_analysis_dates(self):
        """Test analysis date properties."""
        config = Config(
            openai_api_key="test-key",
            repository_paths=["."],
            slack_channel="#test",
            slack_token="test-token",
            time_window_days=14,
        )

        # Check that dates are calculated correctly
        start_date = config.analysis_start_date
        end_date = config.analysis_end_date

        # Should be approximately 14 days apart
        diff = end_date - start_date
        assert abs(diff.days - 14) <= 1  # Allow for some timing variation

    def test_custom_dates(self):
        """Test config with custom start/end dates."""
        start = datetime(2024, 1, 1)
        end = datetime(2024, 1, 31)

        config = Config(
            openai_api_key="test-key",
            repository_paths=["."],
            slack_channel="#test",
            slack_token="test-token",
            start_date=start,
            end_date=end,
        )

        assert config.analysis_start_date == start
        assert config.analysis_end_date == end

    def test_invalid_repository_path(self):
        """Test validation of invalid repository paths."""
        with pytest.raises(ValueError, match="Repository path does not exist"):
            Config(
                openai_api_key="test-key",
                repository_paths=["/nonexistent/path"],
                slack_channel="#test",
                slack_token="test-token",
            )

    def test_slack_validation(self):
        """Test Slack configuration validation."""
        # Should fail when neither token nor webhook is provided
        with pytest.raises(
            ValueError, match="Either slack_token or slack_webhook_url must be provided"
        ):
            Config(
                openai_api_key="test-key", repository_paths=["."], slack_channel="#test"
            )
