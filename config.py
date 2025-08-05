#!/usr/bin/env python3
"""
Central configuration file for all scripts in the Research Hub Claude workflow.

This file contains shared settings that are used across multiple scripts,
making it easy to update paths and other configuration in one place.
"""

import os
from pathlib import Path

# Main Obsidian vault path - Update this if your vault moves
VAULT_PATH = "/Users/niklaskarlsson/Obsidian Sandbox/Research Hub - Main folder/Research Hub"

# Alternative: Use environment variable if set
VAULT_PATH = os.environ.get('OBSIDIAN_VAULT_PATH', VAULT_PATH)

# Specific folder paths within the vault
ARTICLES_FOLDER = Path(VAULT_PATH) / "4 Articles"
CONCEPTS_FOLDER = Path(VAULT_PATH) / "1 CONCEPTS - KEYWORDS"
AUTHORS_FOLDER = Path(VAULT_PATH) / "2 AUTHORS - SCHOLLARS"
JOURNALS_FOLDER = Path(VAULT_PATH) / "3 JOURNALS"
DAILY_NOTES_FOLDER = Path(VAULT_PATH) / "0 Daily notes"

# Claude workspace paths (relative to this repository)
CLAUDE_WORKSPACE = Path(__file__).parent
SYSTEM1_TAGGING = CLAUDE_WORKSPACE / "system1_tagging"
SYSTEM1_BRIDGE = CLAUDE_WORKSPACE / "system1_bridge"
MISC_SCRIPTS = CLAUDE_WORKSPACE / "misc_scripts"

# Export and archive paths
EXPORT_PATH = SYSTEM1_TAGGING / "export"
CURRENT_EXPORT = EXPORT_PATH / "current"
ARCHIVE_EXPORT = EXPORT_PATH / "archive"

# File patterns
MARKDOWN_PATTERN = "*.md"
BIBTEX_PATTERN = "*.bib"

# Tag-related settings
TAG_SUGGESTIONS_FILE = SYSTEM1_TAGGING / "manual_tag_suggestions.json"
BATCH_PROGRESS_FILE = EXPORT_PATH / "batch_progress.json"

# Default batch sizes
DEFAULT_BATCH_SIZE = 50
DEFAULT_ANALYSIS_LIMIT = 100

# Logging settings
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'