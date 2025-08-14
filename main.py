#!/usr/bin/env python3
"""Main entry point for Git Sniff Otter."""

import sys

from git_sniff_otter.cli import cli

if __name__ == "__main__":
    sys.exit(cli())
