# Deep Analysis Workflow Summary

## Overview
The tagging workflow has been reorganized into a comprehensive three-phase deep analysis system that prioritizes quality over quantity.

## Three-Phase Analysis

### Phase 1A: Tag System Analysis
- Analyzes existing tags across the entire vault
- Identifies systematic issues (formatting, redundancy, missing categories)
- Tracks temporal trends and bridge tags
- Output: `tag_system_analysis_report.md`

### Phase 1B: Article Quality Analysis
- Assesses tag quality for each article (0-100 score)
- Evaluates based on:
  - Quantity (0-20 points)
  - Category coverage (0-30 points)
  - Specificity (0-25 points)
  - Taxonomy alignment (0-25 points)
- Output: `article_tag_quality_analysis.json`

### Phase 1C: Extract Retagging Candidates
- Filters articles that:
  - Have abstracts (can be properly analyzed)
  - Quality score < 60 (need improvement)
- Prioritizes based on quality score and importance
- Output: `articles_for_retagging.md`

## Key Commands

```bash
# Run complete analysis
python3 claude_workspace/scripts/tagging/deep_analysis_workflow.py

# Run individual phases
python3 claude_workspace/scripts/tagging/deep_analysis_workflow.py --phase 1a
python3 claude_workspace/scripts/tagging/deep_analysis_workflow.py --phase 1b
python3 claude_workspace/scripts/tagging/deep_analysis_workflow.py --phase 1c
```

## Export Structure

```
export/tagging/
├── current/                    # Current reports
│   ├── tag_system_analysis_report.md
│   ├── article_tag_quality_analysis.json
│   ├── articles_for_retagging.md
│   ├── deep_analysis_summary.md
│   └── manual_tag_suggestions.json
└── archive/                    # Automatically archived old reports
    └── 20250804_190000/
        └── [previous reports]
```

## Workflow Integration

1. **Deep Analysis**: Run the comprehensive analysis to understand current state
2. **Claude Tagging**: Use reports to guide manual tagging in Claude Code
3. **Apply Tags**: Use `obsidian_article_tagger.py --apply-suggestions`

## Quality Metrics

- **Excellent (80-100)**: 15+ tags, covers most categories, highly specific
- **Good (60-79)**: 10+ tags, good coverage, mostly specific
- **Fair (40-59)**: 5+ tags, some coverage, mix of specific/generic
- **Poor (20-39)**: 3+ tags, limited coverage, mostly generic
- **Very Poor (0-19)**: <3 tags, minimal coverage, generic only

## Archived Scripts

The following redundant scripts have been archived:
- `tag_articles_no_tags.py`
- `tag_empty_articles.py`

Their functionality is now integrated into the main workflow.