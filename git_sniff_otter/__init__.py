"""Git Sniff Otter - Automated Git repository analysis and reporting tool."""

__version__ = "1.0.0"
__author__ = "Git Sniff Otter Team"
__description__ = (
    "Automated Git repository analysis and reporting tool with LLM-powered insights"
)

from .config import Config, load_config
from .modules.data_collector import DataCollector
from .modules.data_transformer import DataTransformer
from .modules.llm_generator import LLMReportGenerator
from .modules.slack_sender import SlackSender

__all__ = [
    "Config",
    "load_config",
    "DataCollector",
    "DataTransformer",
    "LLMReportGenerator",
    "SlackSender",
]
