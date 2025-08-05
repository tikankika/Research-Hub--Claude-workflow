# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Obsidian vault for a book project focused on AI in Education, Machine Psychology, and Pedagogical Perspectives on AI. The repository combines research materials (markdown files) with Python scripts for vault maintenance.

## Key Commands

### Tag Management

#### Deep Analysis Workflow (HIGH QUALITY THREE-PHASE ANALYSIS)
```bash
cd "/Users/niklaskarlsson/Obsidian Sandbox/Book project, Sandbox"

# NEW COMPREHENSIVE WORKFLOW:
# Run all three phases of deep analysis
python3 claude_workspace/system1_tagging/scripts/deep_analysis_workflow.py

# Or run individual phases:
python3 claude_workspace/system1_tagging/scripts/deep_analysis_workflow.py --phase 1a  # Tag system analysis
python3 claude_workspace/system1_tagging/scripts/deep_analysis_workflow.py --phase 1b  # Article quality analysis
python3 claude_workspace/system1_tagging/scripts/deep_analysis_workflow.py --phase 1c  # Extract retagging candidates

# Main output: tagging_action_plan.txt (simple, actionable list)
# Reports are saved to: claude_workspace/system1_tagging/export/current/
# Old reports are automatically archived to: claude_workspace/system1_tagging/export/archive/
```

#### Manual Tagging in Claude Code
```bash
# After running deep analysis, use the reports to guide tagging:
# 1. Check articles_for_retagging.md for priority list
# 2. Analyze articles with 7-category framework
# 3. Add tags to: claude_workspace/system1_tagging/manual_tag_suggestions.json

# Apply tags from manual suggestions
python3 claude_workspace/system1_tagging/scripts/obsidian_article_tagger.py --apply-suggestions
```

**Batch Processing Workflow (RECOMMENDED FOR SPEED):**
1. **Batch analyze**: `python3 claude_workspace/system1_tagging/scripts/obsidian_article_tagger.py --batch --limit 50`
   - Processes 50 articles automatically using keyword matching
   - Saves all suggestions to `claude_workspace/system1_tagging/export/tag_suggestions/`
   - Tracks progress in `batch_progress.json` - can be resumed if interrupted
   - Skips already processed files automatically
2. **Review suggestions**: `python3 claude_workspace/system1_tagging/scripts/obsidian_article_tagger.py --review`
   - Interactive review: [a]pply, [s]kip, [d]elete, [e]dit tags, [q]uit
   - Edit tags before applying if needed
   - Shows whether tags were generated in batch mode
3. **Or apply all at once**: `python3 claude_workspace/system1_tagging/scripts/obsidian_article_tagger.py --apply-suggestions`
   - Applies all pending suggestions without review

**Semi-Manual Workflow (For careful review with Claude):**
1. Run analysis for one article: `python3 claude_workspace/system1_tagging/scripts/obsidian_article_tagger.py --limit 1`
2. Claude analyzes and shows suggested tags
3. Confirm tags with user
4. Tags are saved to `claude_workspace/system1_tagging/export/tag_suggestions/`
5. Apply confirmed tags: `python3 claude_workspace/system1_tagging/scripts/obsidian_article_tagger.py --apply-suggestions`

#### Batch Tagging (For "4 Articles" folder)
```bash
# Batch tag articles in "4 Articles" folder
python3 claude_workspace/system1_tagging/scripts/obsidian_batch_tagger.py --mode claude --limit 20
# Save Claude's JSON output, then apply:
python3 claude_workspace/system1_tagging/scripts/obsidian_batch_tagger.py --apply suggestions.json
```

#### Tag Maintenance Tools (ENHANCED WITH ADVANCED ANALYTICS)
```bash
cd claude_workspace/system1_tagging/scripts

# Unified tool for maintenance
python3 obsidian_tag_tools.py analyze          # Analyze vault tags
python3 obsidian_tag_tools.py cleanup --execute # Full cleanup
python3 obsidian_tag_tools.py report           # Generate tag report

# Advanced tag analysis with new features
python3 obsidian_tag_manager.py --report --advanced  # Full report with all analytics
python3 obsidian_tag_manager.py --analyze           # Quick analysis

# Comprehensive tag report with file associations (NEW)
python3 comprehensive_tag_report.py              # Full vault scan with file details
python3 comprehensive_tag_report.py --focus-folder "4 Articles"  # Focus on specific folder
python3 comprehensive_tag_report.py --format json  # JSON export with full file lists

# Individual scripts (for advanced use)
python3 obsidian_tag_manager.py --merge "old_tag" "new_tag"
python3 standardize_all_tags.py --apply --force
python3 merge_duplicate_tags.py --apply --force
```

**New Tag Manager Features:**
- **Bridge Tag Detection**: Identifies tags that connect multiple research domains
- **Temporal Trend Analysis**: Classifies tags as emerging (>70% recent), declining (<30% recent), stable, or periodic
- **Enhanced Semantic Duplicates**: Multi-method detection using stem matching, synonyms, and pattern analysis
- **Tag Quality Metrics**: Calculates quality scores based on usage, diversity, clarity, and temporal consistency
- **Advanced Domain Analysis**: Auto-categorizes tags into 8 research domains with improved accuracy

**Reports Now Include:**
- Bridge tags connecting interdisciplinary research areas
- Emerging and declining tag trends with emergence/decline strength
- Stable tags showing consistent usage over time
- Periodic tags appearing intermittently
- Tag quality scores with recommendations to promote or review
- Collection-wide metrics (avg tags/file, tag density, reuse ratio)
- Semantic duplicate groups with confidence scores

### Legacy Scripts (Archived)
The original tag management scripts have been moved to `claude_workspace/scripts/archive/legacy_tag_scripts/`.
They have been replaced by the new Obsidian-compatible tagging system above.

### System 1: Paperpile-Obsidian Bridge (COMPLETED ✅)
```bash
cd "/Users/niklaskarlsson/Obsidian Sandbox/Book project, Sandbox/claude_workspace/system1_bridge"

# 1. Analyze vault to check BibTeX match rate
python3 analyze_vault.py --bibtex "../paperpile/paperpile.bib"

# 2. Migrate files to BibTeX keys (with minimal aliases)
python3 migrate_to_bibtex_keys.py --bibtex "../Paperpile - References - 3 aug.bib" --execute --batch 100

# 3. Sync Paperpile metadata (after migration)
python3 paperpile_sync.py --bibtex "../Paperpile - References - 3 aug.bib"

# Full workflow for System 1:
python3 analyze_vault.py --bibtex "../paperpile/paperpile.bib"     # Check readiness
python3 migrate_to_bibtex_keys.py --bibtex "../Paperpile - References - 3 aug.bib" --execute --batch 100  # Batch migration
python3 paperpile_sync.py --bibtex "../Paperpile - References - 3 aug.bib"  # Add metadata
```

**System 1 Status: COMPLETE**
- ✅ 1,165 BibTeX key files in "4 Articles" folder
- ✅ All files have Paperpile metadata with content provenance
- ✅ Ready for continuous Paperpile synchronization

### Article Management
```bash
# Rename article files to citation format
cd claude_workspace/scripts
python rename_articles.py
```

### PDF Processing
```bash
# Extract text from PDF files
cd claude_workspace/scripts
python extract_pdf.py [path_to_pdf]
```

## Codebase Architecture

### Content Structure
- **Numbered folders (0-5)**: Research content organized by type (daily notes, concepts, authors, journals, articles, methods)
- **Markdown files**: All content uses Obsidian-flavored markdown with wiki-links `[[]]` and tags `#tag`
- **Special folders**: XX (work in progress), YY (other work), ZZ (ideas) for temporary content

### Claude Workspace (`/claude_workspace`)
- **scripts/**: Python utilities for vault maintenance
  - Tag cleanup scripts use regex patterns to find hashtags and YAML frontmatter tags
  - Scripts operate directly on markdown files, modifying content in-place
- **archive/**: Output from script runs (JSON reports, markdown summaries)
- **docs/**: Documentation (currently empty)

### Script Patterns
All Python scripts follow similar patterns:
1. Scan vault using `Path.rglob("*.md")` to find markdown files
2. Use regex to extract tags, metadata, or content
3. Provide interactive CLI interfaces using colorama for colored output
4. Generate reports in JSON or markdown format

### Special Considerations
- **Swedish characters**: Scripts handle åäöÅÄÖ in tags and filenames
- **Tag formats**: Both `#tag` and YAML frontmatter `tags: [tag1, tag2]` are supported
- **File safety**: Scripts create backups or operate in dry-run mode by default
- **Obsidian compatibility**: Preserve wiki-links, embeds, and other Obsidian syntax

## Research Areas
The vault focuses on:
- Artificial Intelligence in Education (AIED)
- Machine Psychology
- Dialogic Learning
- Voice-Based AI Interaction
- Educational Technology

## Changelog

### Latest Updates (2025-08-03)

**Tag Management System Enhancements:**
- Enhanced bridge tag detection algorithm with 8 domain patterns and connection strength scoring
- Improved temporal trend analysis with emergence/decline classification, stable/periodic tag detection
- Upgraded semantic duplicate detection with multi-method approach (stem, synonym, pattern matching)
- Added comprehensive tag quality metrics and scoring system
- Implemented batch mode for article tagger (process 50+ articles automatically)
- Added interactive review mode for batch-generated suggestions
- Added progress tracking for resumable batch processing

See [CHANGELOG.md](CHANGELOG.md) for all project updates and version history.