# Research Hub - Claude Workflow

This repository contains Python scripts and tools for managing the Research Hub Obsidian vault, focusing on academic article tagging and organization.

## Overview

This repository serves as a dedicated workspace for managing research content, keeping scripts separate from the main Obsidian vault while maintaining easy access. The scripts work with content stored in the Research Hub vault at `/Users/niklaskarlsson/Obsidian Sandbox/Research Hub - Main folder/Research Hub`.

## Repository Structure

```
Research Hub - Claude workflow (Github)/
├── config.py                    # Central path configuration
├── system1_tagging/            # Article tagging system
│   ├── scripts/                # All tagging-related Python scripts
│   ├── export/                 # Output files (current/ and archive/)
│   └── manual_tag_suggestions.json  # Manual tagging queue
├── system1_bridge/             # Paperpile-Obsidian synchronization
│   └── scripts/                # Bridge scripts for BibTeX integration
├── Claude workflow - development/  # Development scripts
└── misc_scripts/               # Standalone utilities
```

## Quick Start

### Configuration

All paths are configured in `config.py`. To change the vault location, simply update `VAULT_PATH` in that file:

```python
VAULT_PATH = "/Users/niklaskarlsson/Obsidian Sandbox/Research Hub - Main folder/Research Hub"
```

### Key Commands

#### Deep Analysis Workflow (Recommended Starting Point)

```bash
cd "/Users/niklaskarlsson/Obsidian Sandbox/Research Hub - Main folder/Research Hub - Claude workflow (Github)"

# Run comprehensive three-phase analysis
python3 system1_tagging/scripts/deep_analysis_workflow.py

# Main output: system1_tagging/export/current/tagging_action_plan.txt
```

This generates:
- Tag system analysis report
- Article quality assessment
- Prioritized list of articles needing tags
- Actionable tagging plan

#### Tag Management

```bash
cd system1_tagging/scripts

# Analyze vault tags
python3 obsidian_tag_tools.py analyze

# Full cleanup (standardize, merge duplicates, remove invalid)
python3 obsidian_tag_tools.py cleanup --execute

# Generate comprehensive tag report
python3 comprehensive_tag_report.py
```

#### Article Tagging Workflows

**Batch Processing (Fast):**
```bash
# Process 50 articles automatically
python3 obsidian_article_tagger.py --batch --limit 50

# Review and apply suggestions
python3 obsidian_article_tagger.py --review
```

**Manual Review (Careful):**
```bash
# Analyze one article at a time
python3 obsidian_article_tagger.py --limit 1

# Apply all confirmed suggestions
python3 obsidian_article_tagger.py --apply-suggestions
```

## System Features

### Tag Management System
- **Deep Analysis**: Three-phase workflow for comprehensive tag assessment
- **Bridge Tag Detection**: Identifies tags connecting multiple research domains
- **Temporal Analysis**: Tracks emerging, declining, stable, and periodic tags
- **Quality Metrics**: Scores tags based on usage, diversity, clarity, and consistency
- **Semantic Deduplication**: Detects duplicates using stem matching, synonyms, and patterns
- **Batch Processing**: Tag multiple articles automatically with keyword matching

### Research Domains Covered
- Artificial Intelligence in Education (AIED)
- Machine Psychology
- Dialogic Learning
- Educational Technology
- Learning Sciences
- Research Methodology
- Cognitive Science
- Professional Development

### Current Statistics
- **Total Articles**: 1,501 in "4 Articles" folder
- **Unique Tags**: 704
- **Average Tags per Article**: 1.73
- **Average Quality Score**: 18.1/100

## Getting Started

1. Clone this repository:
   ```bash
   git clone https://github.com/tikankika/Research-Hub--Claude-workflow.git
   ```

2. Navigate to the project directory:
   ```bash
   cd "Research Hub - Claude workflow (Github)"
   ```

3. Run the deep analysis workflow to assess current state:
   ```bash
   python3 system1_tagging/scripts/deep_analysis_workflow.py
   ```

4. Review the tagging action plan in `system1_tagging/export/current/tagging_action_plan.txt`

5. Start tagging articles based on the prioritized list

## Important Notes

- All scripts work directly on the Obsidian vault files
- Most operations have dry-run mode by default (use `--execute` or `--apply` to make changes)
- Reports are saved to `export/current/` with automatic archiving
- The system preserves existing tags while adding new ones

## Recent Updates (2025-08-05)

- Migrated scripts to dedicated GitHub repository
- Created central configuration system (`config.py`)
- Fixed export path references throughout all scripts
- Improved archiving workflow to keep reports accessible

For detailed change history, see the git commit log.

## Contributing

When adding new scripts or features:
1. Use the central `config.py` for all path references
2. Follow the existing folder structure (scripts in appropriate system folder)
3. Add documentation for new functionality
4. Test thoroughly before committing changes

## License

This project is for research purposes.