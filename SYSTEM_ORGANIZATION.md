# Claude Workspace System Organization

This workspace is organized by system/function, with each system having its own complete structure.

## Current Systems

### 1. system1_tagging/
Article tagging system for academic papers
- **scripts/** - All tagging-related Python scripts
- **export/** - Output files (current/ and archive/)
- **docs/** - Documentation (README.md, SCRIPT_GUIDE.md)
- **archive/** - Archived scripts and old files

### 2. system1_bridge/
Paperpile-Obsidian synchronization system
- **scripts/** - Bridge scripts (analyze_vault.py, migrate_to_bibtex_keys.py, paperpile_sync.py)
- **export/** - Analysis reports and migration logs
- **docs/** - System documentation
- **archive/** - Old logs and outputs

### 3. misc_scripts/
Standalone utilities that don't belong to a specific system
- extract_pdf.py - PDF text extraction
- rename_articles.py - Article file renaming
- paperpile_to_markdown.py - Paperpile export conversion

## Benefits of System-Based Organization

1. **Self-contained systems** - Each system has everything it needs in one place
2. **Clear separation** - No mixing of exports, scripts, or docs between systems
3. **Easy to add new systems** - Just create a new system folder with the same structure
4. **Better scalability** - As the project grows, systems remain organized

## Adding a New System

To add a new system (e.g., system2_analysis):
```
mkdir -p system2_analysis/{scripts,export,docs,archive}
```

Then move relevant scripts and create documentation specific to that system.