# Claude Workspace Scripts

This directory contains Python scripts for managing and maintaining the Obsidian vault.

## Active Scripts

### Tagging System (`tagging/` subfolder)
- **`obsidian_tag_tools.py`** - NEW! Unified tool combining all tag operations
- **`obsidian_article_tagger.py`** - Analyzes articles and suggests tags using Claude
- **`obsidian_tag_manager.py`** - Tag management: analysis, deduplication, merging
- **`standardize_all_tags.py`** - Converts tags to underscore format
- **`merge_duplicate_tags.py`** - Merges duplicate tags
- **`README.md`** - Complete tagging documentation and workflows

### Article Management
- **`paperpile_to_markdown.py`** - Imports articles from paperpile.bib with wikilinks
- **`rename_articles.py`** - Renames article files based on metadata

### Utilities
- **`extract_pdf.py`** - Extracts text from PDF files

## Archived Scripts
Legacy scripts have been moved to `archive/legacy_tag_scripts/`:
- `tag_cleanup.py` - Original interactive cleanup (replaced by obsidian_tag_manager.py)
- `tag_cleanup_simple.py` - Basic analysis (replaced by obsidian_tag_manager.py --analyze)
- `tag_cleanup_recommendations.py` - JSON recommendations (replaced by obsidian_tag_manager.py --report)
- `apply_tag_cleanup.py` - Applied JSON changes (replaced by direct merge functionality)

## Quick Start

### NEW: Unified Tag Management
```bash
cd tagging
python3 obsidian_tag_tools.py analyze          # Analyze vault
python3 obsidian_tag_tools.py cleanup          # Clean all tags (dry run)
python3 obsidian_tag_tools.py cleanup --execute # Clean all tags (apply)
python3 obsidian_tag_tools.py tag --limit 20   # Tag articles
```

### Import new articles
```bash
python3 paperpile_to_markdown.py
```

### Individual tag operations (advanced)
```bash
cd tagging
python3 obsidian_tag_manager.py --report       # Generate report
python3 standardize_all_tags.py --apply --force # Standardize tags
python3 merge_duplicate_tags.py --apply --force # Merge duplicates
```

## Script Dependencies
All scripts use standard Python libraries. No external dependencies required except for Claude API integration (when implemented).