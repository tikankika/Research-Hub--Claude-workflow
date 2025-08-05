# Claude Code Instructions: System 1 Implementation

## Project Context
Building System 1 of an Academic Knowledge-to-Writing System. This system syncs Paperpile references with Obsidian while preserving user content.

## Current Situation
- **700+ articles** in `/4 Articles/` with long descriptive filenames
- **PDFs** in `/9 Paperpile/All Papers/[Letter]/[Filename].pdf`
- **BibTeX** export available with all metadata
- **Working PDF links** like `[[../9 Paperpile/All Papers/S/Sporrong et al. 2024.pdf]]`

## What We're Building

### Component 1: Smart Import & Sync
**Goal**: Rename files to BibTeX keys, enhance metadata, preserve user content

**Key Decisions Made**:
1. Use BibTeX keys as filenames (e.g., `Sporrong2024-jh.md`)
2. Keep files in `/4 Articles/` root (NO subfolders)
3. Add aliases for searchability
4. Use tags for organization (not folders)
5. Preserve ALL user content

### Component 2: PDF Annotation Extraction
**Goal**: Extract annotations from PDFs if possible
**Status**: Investigation needed first

## Implementation Steps

### Step 1: Analyze Current Vault
Create `analyze_vault.py`:

```python
"""
Analyze current vault to prepare for migration
- Find all markdown files in /4 Articles/
- Match them to BibTeX entries
- Check PDF links
- Identify user content vs. Paperpile content
"""

import re
from pathlib import Path
import bibtexparser

class VaultAnalyzer:
    def __init__(self, vault_path, bibtex_path):
        self.vault_path = Path(vault_path)
        self.bibtex_path = Path(bibtex_path)
        
    def analyze(self):
        # 1. Parse BibTeX
        # 2. Scan markdown files
        # 3. Match files to BibTeX entries
        # 4. Check PDF links
        # 5. Report findings
```

### Step 2: Migration Script
Create `migrate_to_bibtex_keys.py`:

```python
"""
Migrate files to BibTeX key naming
- Rename files from descriptive names to BibTeX keys
- Add aliases for the old filename
- Add tags for organization
- Update internal wiki links
"""

class Migration:
    def migrate_file(self, old_path, bibtex_entry):
        # 1. Generate new filename
        new_name = f"{bibtex_entry['ID']}.md"
        
        # 2. Add frontmatter with aliases
        aliases = [
            old_path.stem,  # Original filename
            f"{authors} {year}",  # Citation style
            title_short,  # Short title
        ]
        
        # 3. Add organization tags
        tags = ['from_paperpile']
        
        # 4. Preserve user content
        # 5. Update file
```

### Step 3: Enhanced Sync
Create `paperpile_sync.py`:

```python
"""
Sync Paperpile to Obsidian with all fields
- Extract ALL BibTeX fields including 'note'
- Create proper PDF links
- Add content markers for provenance
- Never overwrite user content
"""

class PaperpileSync:
    def sync_article(self, bibtex_entry):
        # Build complete metadata including:
        # - DOI with clickable link
        # - Publisher information
        # - PDF path with correct link
        # - Paperpile notes from 'note' field
```

## File Structure to Maintain

```
/4 Articles/
├── Sporrong2024-jh.md      # After migration (was: Sporrong et al. (2024). Situating AI...)
├── Fields2009-ai.md        # After migration
├── [other articles]
└── [user's own notes]      # Don't touch these
```

## Markdown Structure After Migration

```markdown
---
aliases:
  - "Sporrong, McGrath & Cerratto Pargman (2024). Situating AI in assessment"
  - "Sporrong et al. 2024"
  - "Situating AI in assessment"
tags:
  - from_paperpile
source: paperpile
---

# Sporrong, McGrath & Cerratto Pargman (2024). Situating AI in assessment—an exploration of university teachers' valuing practices

<!-- PAPERPILE METADATA START -->
## Metadata
**Type:** Article
**Author(s):** [[Sporrong, Elin]], [[McGrath, Cormac]], [[Cerratto Pargman, Teresa]]
**Year:** 2024
**Journal:** [[AI and Ethics]]
**Publisher:** Springer Science and Business Media LLC
**DOI:** [10.1007/s43681-024-00558-8](https://doi.org/10.1007/s43681-024-00558-8)

## Abstract
[Abstract text...]

## Additional Information
**URL:** [View Online](http://dx.doi.org/10.1007/s43681-024-00558-8)
**PDF:** [[../9 Paperpile/All Papers/S/Sporrong et al. 2024 - Situating AI in assessment.pdf]] 📄

## Paperpile Notes
[Content from 'note' field in BibTeX]

## Reference Information
**BibTeX Key:** Sporrong2024-jh
<!-- PAPERPILE METADATA END -->

<!-- USER CONTENT START -->
## My Notes
[Any user notes - NEVER modify this section]
<!-- USER CONTENT END -->
```

## Critical Rules

1. **NEVER move files to subfolders** - Keep in /4 Articles/ root
2. **NEVER break PDF links** - They currently work as `[[../9 Paperpile/...]]`
3. **NEVER delete user content** - Preserve everything between USER CONTENT markers
4. **ALWAYS add aliases** - Include original filename as alias
5. **ALWAYS backup first** - Create safety copy before any changes

## BibTeX Fields to Extract

```python
REQUIRED_FIELDS = {
    'ID': 'bibtex_key',
    'title': 'title',
    'author': 'authors',  # Format as "Last, First"
    'year': 'year',
    'journaltitle': 'journal',
}

OPTIONAL_FIELDS = {
    'doi': 'doi',
    'url': 'url', 
    'publisher': 'publisher',
    'abstract': 'abstract',
    'file': 'pdf_path',  # Extract path from "All Papers/..."
    'note': 'paperpile_notes',  # User's notes in Paperpile
    'keywords': 'keywords',
    'volume': 'volume',
    'number': 'issue',
    'pages': 'pages',
}
```

## Testing Protocol

1. **Test with 5 articles first**
2. **Verify PDF links still work**
3. **Check aliases work in Obsidian**
4. **Ensure user content preserved**
5. **Run full migration only after validation**

## Success Criteria

- ✅ All files renamed to BibTeX keys
- ✅ Original filenames preserved as aliases
- ✅ PDF links working
- ✅ All BibTeX fields extracted
- ✅ User content untouched
- ✅ Can find articles by title, author, or key

## Start Here

```python
# First script to create
python analyze_vault.py --vault "/4 Articles" --bibtex "paperpile.bib"
```

This will show what needs to be done before starting migration.