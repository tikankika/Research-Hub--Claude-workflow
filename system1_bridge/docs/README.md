# System 1: Paperpile-Obsidian Literature Bridge

## Overview
Smart synchronization system that maintains perfect sync between Paperpile library and Obsidian vault while preserving user content.

## Key Design Decisions
1. **BibTeX keys as filenames** (e.g., `Sporrong2024-jh.md`)
2. **Keep files in `/4 Articles/` root** (NO subfolders)
3. **Content provenance tracking** (Paperpile vs User content)
4. **Never overwrite user content**
5. **Rich aliases for searchability**

## Components

### 1. Vault Analyzer (`analyze_vault.py`)
Analyzes current state before migration:
- Matches markdown files to BibTeX entries
- Checks PDF links
- Identifies user vs. Paperpile content
- Reports migration readiness

### 2. Migration Tool (`migrate_to_bibtex_keys.py`)
Renames files to BibTeX keys:
- Preserves original filenames as aliases
- Updates internal wiki links
- Adds organization tags
- Creates backup before changes

### 3. Paperpile Sync (`paperpile_sync.py`)
Ongoing synchronization:
- Imports all BibTeX fields including 'note'
- Updates only Paperpile sections
- Preserves user content
- Tracks content provenance

### 4. PDF Annotation Extractor (`extract_annotations.py`)
Extract highlights and comments from PDFs (if possible)

## Usage

### Initial Analysis
```bash
python analyze_vault.py --vault "/4 Articles" --bibtex "~/Desktop/paperpile.bib"
```

### Migration
```bash
python migrate_to_bibtex_keys.py --dry-run  # Preview changes
python migrate_to_bibtex_keys.py --execute  # Apply migration
```

### Ongoing Sync
```bash
python paperpile_sync.py --sync  # Update from BibTeX
```

## File Structure

### Before Migration
```
/4 Articles/
├── Sporrong, McGrath & Cerratto Pargman (2024). Situating AI in assessment.md
└── [other long filenames].md
```

### After Migration
```
/4 Articles/
├── Sporrong2024-jh.md  # With aliases for old filename
└── [other bibtex keys].md
```

## Content Structure

```markdown
---
aliases:
  - "Original long filename"
  - "Short citation"
  - "Title keywords"
tags:
  - from_paperpile
---

# Full Title

<!-- PAPERPILE METADATA START -->
[All Paperpile data - can be updated by sync]
<!-- PAPERPILE METADATA END -->

<!-- USER CONTENT START -->
[Your notes - NEVER modified by sync]
<!-- USER CONTENT END -->
```