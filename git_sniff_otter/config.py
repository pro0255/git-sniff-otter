"""Configuration management for Git Sniff Otter."""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator


class Config(BaseModel):
    """Configuration model for the Git Sniff Otter application."""

    # LLM Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    llm_model: str = Field(default="gpt-4", description="LLM model to use")

    # Slack Configuration
    slack_token: Optional[str] = Field(None, description="Slack bot token")
    slack_webhook_url: Optional[str] = Field(None, description="Slack webhook URL")
    slack_channel: str = Field(..., description="Slack channel to send reports to")

    # Git Configuration
    repository_paths: List[str] = Field(..., description="List of git repository paths")
    time_window_days: int = Field(default=7, description="Number of days to analyze")
    start_date: Optional[datetime] = Field(None, description="Start date for analysis")
    end_date: Optional[datetime] = Field(None, description="End date for analysis")

    # Tool Configuration
    gitinspector_path: str = Field(
        default="gitinspector", description="Path to gitinspector tool"
    )

    @field_validator("repository_paths")
    @classmethod
    def validate_repository_paths(cls, v):
        """Validate that repository paths exist and are git repositories."""
        for path in v:
            if not os.path.exists(path):
                raise ValueError(f"Repository path does not exist: {path}")
            if not os.path.exists(os.path.join(path, ".git")):
                raise ValueError(f"Path is not a git repository: {path}")
        return v

    @model_validator(mode="after")
    def validate_slack_config(self):
        """Ensure at least one Slack configuration method is provided."""
        if not self.slack_token and not self.slack_webhook_url:
            raise ValueError("Either slack_token or slack_webhook_url must be provided")
        return self

    @property
    def analysis_start_date(self) -> datetime:
        """Get the start date for analysis."""
        if self.start_date:
            return self.start_date
        return datetime.now() - timedelta(days=self.time_window_days)

    @property
    def analysis_end_date(self) -> datetime:
        """Get the end date for analysis."""
        if self.end_date:
            return self.end_date
        return datetime.now()


def load_config(config_file: Optional[str] = None) -> Config:
    """Load configuration from environment variables and file."""
    if config_file:
        load_dotenv(config_file)
    else:
        load_dotenv()  # Load from .env file if it exists

    return Config(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        llm_model=os.getenv("LLM_MODEL", "gpt-4"),
        slack_token=os.getenv("SLACK_TOKEN"),
        slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
        slack_channel=os.getenv("SLACK_CHANNEL", "#general"),
        repository_paths=[],  # Will be set via CLI
        time_window_days=int(os.getenv("TIME_WINDOW_DAYS", "7")),
        start_date=None,
        end_date=None,
        gitinspector_path=os.getenv("GITINSPECTOR_PATH", "gitinspector"),
    )
