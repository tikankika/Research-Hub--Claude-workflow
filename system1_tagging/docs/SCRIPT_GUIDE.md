# Tagging Scripts Guide

## Quick Reference

### 🎯 Primary Workflow Script
```bash
# Run this for complete analysis and action plan
python3 deep_analysis_workflow.py
```
Output: `tagging_action_plan.txt` with prioritized article lists

### 📊 Reporting Scripts
```bash
# Comprehensive tag report with file associations
python3 comprehensive_tag_report.py

# Advanced tag analysis (bridge tags, trends, quality)
python3 obsidian_tag_manager.py --report --advanced
```

### 🏷️ Tag Application
```bash
# Apply tags from manual_tag_suggestions.json
python3 obsidian_article_tagger.py --apply-suggestions
```

## Script Details

### 1. **deep_analysis_workflow.py** (PRIMARY)
**Purpose:** Three-phase comprehensive analysis
**Phases:**
- Phase 1A: Tag system analysis
- Phase 1B: Article quality scoring (0-100)
- Phase 1C: Extract retagging candidates

**Usage:**
```bash
# Run all phases
python3 deep_analysis_workflow.py

# Run specific phase
python3 deep_analysis_workflow.py --phase 1a
```

**Main Output:** `tagging_action_plan.txt`
- HIGH PRIORITY: Articles with score 0-20 (need full tagging)
- MEDIUM PRIORITY: Articles with score 20-40 (need improvement)
- LOW QUALITY WITHOUT ABSTRACT: Articles needing abstracts first

### 2. **comprehensive_tag_report.py**
**Purpose:** Generate detailed tag reports with file associations
**Usage:**
```bash
# Full vault scan
python3 comprehensive_tag_report.py

# Focus on specific folder
python3 comprehensive_tag_report.py --focus-folder "4 Articles"

# Export as JSON
python3 comprehensive_tag_report.py --format json
```

### 3. **obsidian_article_tagger.py**
**Purpose:** Apply tag suggestions to articles
**Usage:**
```bash
# Apply saved suggestions
python3 obsidian_article_tagger.py --apply-suggestions

# Find untagged articles (informational)
python3 obsidian_article_tagger.py --find-untagged

# Review suggestions interactively
python3 obsidian_article_tagger.py --review
```

### 4. **obsidian_tag_manager.py**
**Purpose:** Advanced tag analysis and management
**Features:**
- Bridge tag detection
- Temporal trend analysis
- Tag quality metrics
- Semantic duplicate detection

**Usage:**
```bash
# Generate comprehensive report
python3 obsidian_tag_manager.py --report --advanced

# Merge duplicate tags
python3 obsidian_tag_manager.py --merge "old_tag" "new_tag"

# Clean low-quality tags
python3 obsidian_tag_manager.py --clean
```

### 5. **article_tag_priority_analyzer.py**
**Purpose:** Analyze articles to find tagging priorities
**Usage:**
```bash
# Generate priority analysis
python3 article_tag_priority_analyzer.py --limit 50

# Export to JSON
python3 article_tag_priority_analyzer.py --export-json
```

### 6. **standardize_all_tags.py**
**Purpose:** Standardize tag formats across vault
**Usage:**
```bash
# Preview changes
python3 standardize_all_tags.py --apply

# Apply changes
python3 standardize_all_tags.py --apply --force
```

### 7. **merge_duplicate_tags.py**
**Purpose:** Merge similar/duplicate tags
**Usage:**
```bash
# Preview merges
python3 merge_duplicate_tags.py

# Apply merges
python3 merge_duplicate_tags.py --apply --force
```

## Maintenance Scripts

### obsidian_tag_tools.py
All-in-one maintenance tool (wrapper for other scripts)
```bash
python3 obsidian_tag_tools.py analyze
python3 obsidian_tag_tools.py cleanup --execute
python3 obsidian_tag_tools.py report
```

### export_priority_articles.py
Export article lists for batch processing
```bash
python3 export_priority_articles.py --no-tags-limit 50
```

## Workflow Integration

1. **Analysis Phase**
   ```bash
   python3 deep_analysis_workflow.py
   ```
   
2. **Review Phase**
   - Check `tagging_action_plan.txt`
   - Identify HIGH PRIORITY articles
   
3. **Tagging Phase**
   - Add tags to `manual_tag_suggestions.json`
   - Use 7-category framework
   - Aim for 15-20 tags per article
   
4. **Application Phase**
   ```bash
   python3 obsidian_article_tagger.py --apply-suggestions
   ```
   
5. **Verification Phase**
   ```bash
   python3 deep_analysis_workflow.py  # Re-run to see progress
   ```

## Key Concepts

### Tag Quality Scoring (0-100)
- **Quantity** (0-20): Number of tags
- **Coverage** (0-30): Category coverage
- **Specificity** (0-25): Specific vs generic tags
- **Consistency** (0-25): Taxonomy alignment

### 7-Category Framework
1. methodology
2. education_level
3. technology
4. learning_theory
5. skills
6. research_focus
7. ai_specific

### Priority Levels
- **HIGH**: Score 0-20, has abstract
- **MEDIUM**: Score 20-40, has abstract
- **LOW**: Score <60, no abstract

## Output Locations
All outputs go to: `claude_workspace/system1_tagging/export/current/`
- `tagging_action_plan.txt` - Main actionable output
- `tag_data_*.json` - Raw tag data
- `manual_tag_suggestions.json` - Your tag additions
- Various analysis reports

Old reports auto-archive to: `claude_workspace/system1_tagging/export/archive/`