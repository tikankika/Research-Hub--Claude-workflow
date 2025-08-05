# Legacy Tag Scripts (Archived)

These scripts were the original tag management tools, now replaced by the new Obsidian-compatible tagging system.

## Archived Scripts

### 1. tag_cleanup.py
- Original interactive tag cleanup tool
- Features: Find invalid tags, suggest standardizations, apply changes
- **Replaced by**: `obsidian_tag_manager.py` (more comprehensive)

### 2. tag_cleanup_simple.py
- Simplified version of tag_cleanup.py
- Basic tag analysis and cleanup
- **Replaced by**: `obsidian_tag_manager.py --analyze`

### 3. tag_cleanup_recommendations.py
- Generated JSON recommendations for tag cleanup
- Analyzed tag usage and suggested merges
- **Replaced by**: `obsidian_tag_manager.py --report`

### 4. apply_tag_cleanup.py
- Applied recommendations from tag_cleanup_recommendations.py
- Read JSON file and executed tag changes
- **Replaced by**: Direct merge functionality in `obsidian_tag_manager.py`

## Why Archived

These scripts were replaced because:
1. They had overlapping functionality
2. The new scripts are more comprehensive and Obsidian-specific
3. Better integration with Claude API for intelligent tagging
4. More robust tag standardization and deduplication

## Migration Guide

Old command → New command:
- `python tag_cleanup.py` → `python obsidian_tag_manager.py --deduplicate`
- `python tag_cleanup_simple.py` → `python obsidian_tag_manager.py --analyze`
- `python tag_cleanup_recommendations.py` → `python obsidian_tag_manager.py --report`
- `python apply_tag_cleanup.py` → `python obsidian_tag_manager.py --merge`

## Archive Date
2025-01-31