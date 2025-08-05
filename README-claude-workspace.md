# Claude Workspace

This directory contains all scripts and files related to Claude Code operations on this Obsidian vault.

## Structure

### /scripts
Python scripts for various operations:
- **NEW** `obsidian_article_tagger.py` - Analyzes articles and suggests tags using Claude
- **NEW** `obsidian_tag_manager.py` - Manages, deduplicates, and standardizes tags
- **NEW** `paperpile_to_markdown.py` - Imports articles from paperpile.bib with wikilinks
- `apply_tag_cleanup.py` - Applies tag cleanup recommendations
- `extract_pdf.py` - Extracts text from PDF files
- `rename_articles.py` - Renames article files based on metadata
- `tag_cleanup.py` - Main tag cleanup script
- `tag_cleanup_simple.py` - Simplified version of tag cleanup
- `tag_cleanup_recommendations.py` - Generates tag cleanup recommendations

### /archive
Historical outputs and backups from script runs:
- `tag_analysis_report.json` - Detailed tag analysis report
- `tag_cleanup_summary.md` - Summary of tag cleanup operations

### /export
Current exports and reports (NEW):
- Tag analysis reports
- Article lists
- Other generated exports

### /docs
Documentation for scripts and workflows (to be added)

### /tag_management
Legacy Zotero tagging scripts

### /zotero_tagging_v2
Advanced Zotero tagging system with logs and utilities

## Usage

To run any script, navigate to the scripts directory:
```bash
cd claude_workspace/scripts
python script_name.py
```

## Script Descriptions

### Tag Management Scripts
These scripts help analyze and clean up tags in the Obsidian vault:
- Generate recommendations: `python tag_cleanup_recommendations.py`
- Apply cleanup: `python apply_tag_cleanup.py`

### Article Management
- Rename articles based on citation format: `python rename_articles.py`

### PDF Processing
- Extract text from PDFs: `python extract_pdf.py [pdf_file]`