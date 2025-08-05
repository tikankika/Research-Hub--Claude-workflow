# Obsidian Article Tagging System

A comprehensive tagging system for academic articles in Obsidian, featuring deep analysis, quality scoring, and actionable reporting.

## 🚀 Quick Start

### Step 1: Run Deep Analysis
```bash
cd "/Users/niklaskarlsson/Obsidian Sandbox/Research Hub"

# Run complete three-phase analysis
python3 claude_workspace/system1_tagging/scripts/deep_analysis_workflow.py

# Main output: tagging_action_plan.txt - A simple, actionable list
```

### Step 2: Tag Articles Using the Action Plan
1. Open `claude_workspace/system1_tagging/export/current/tagging_action_plan.txt`
2. Start with HIGH PRIORITY articles (score 0-20, has abstract)
3. Analyze each article using the 7-category framework
4. Add tags to `claude_workspace/system1_tagging/manual_tag_suggestions.json`

### Step 3: Apply Tags
```bash
# Apply all pending tag suggestions
python3 claude_workspace/system1_tagging/scripts/obsidian_article_tagger.py --apply-suggestions
```

## 📊 Current Status (2025-08-05)
- **Total Articles:** 1,501
- **Articles needing retagging:** 868 (with abstracts)
- **Articles without abstracts:** 618
- **Average quality score:** 17.9/100
- **Recently tagged:** 28 articles (19 pending due to filename mismatches)

## 🎯 Main Workflows

### 1. Deep Analysis Workflow (PRIMARY)
```bash
# Complete analysis with actionable output
python3 claude_workspace/system1_tagging/scripts/deep_analysis_workflow.py
```

**Outputs:**
- `tagging_action_plan.txt` - Simple actionable list of articles by priority
- `tag_data_[timestamp].json` - Raw tag data for further analysis
- Detailed reports in `current/` folder

### 2. Comprehensive Tag Report
```bash
# Generate detailed tag report with file associations
python3 claude_workspace/system1_tagging/scripts/comprehensive_tag_report.py

# Focus on specific folder
python3 claude_workspace/system1_tagging/scripts/comprehensive_tag_report.py --focus-folder "4 Articles"
```

### 3. Tag Maintenance
```bash
cd claude_workspace/system1_tagging/scripts

# Advanced tag analysis
python3 obsidian_tag_manager.py --report --advanced

# Merge duplicate tags
python3 obsidian_tag_manager.py --merge "old_tag" "new_tag"

# Standardize tag formats
python3 standardize_all_tags.py --apply --force
```

## 📋 7-Category Tagging Framework

When tagging articles, aim for 15-20 tags covering these categories:

1. **methodology** - Research methods (e.g., `empirical_study`, `case_study`, `systematic_review`)
2. **education_level** - Context (e.g., `k_12`, `higher_education`, `adult_education`)
3. **technology** - Technologies (e.g., `artificial_intelligence`, `chatbots`, `learning_analytics`)
4. **learning_theory** - Frameworks (e.g., `constructivism`, `collaborative_learning`)
5. **skills** - Competencies (e.g., `critical_thinking`, `digital_literacy`)
6. **research_focus** - Main emphasis (e.g., `student_engagement`, `assessment`)
7. **ai_specific** - AI aspects (e.g., `ai_ethics`, `prompt_engineering`, `generative_ai`)

## 🔧 Key Scripts

### Core Workflow Scripts
- **deep_analysis_workflow.py** - Three-phase analysis and action plan generation
- **comprehensive_tag_report.py** - Detailed tag reports with file associations
- **obsidian_article_tagger.py** - Apply tag suggestions to articles

### Maintenance Scripts
- **obsidian_tag_manager.py** - Advanced tag analysis and management
- **standardize_all_tags.py** - Convert tags to standard format
- **merge_duplicate_tags.py** - Merge similar/duplicate tags

### Analysis Scripts
- **article_tag_priority_analyzer.py** - Find articles needing tags
- **export_priority_articles.py** - Export article lists for batch processing

## 📁 Export Structure

```
claude_workspace/system1_tagging/
├── manual_tag_suggestions.json # Your tag additions go here (edit this file!)
├── scripts/                    # All tagging scripts
├── export/
│   ├── current/               # Latest reports
│   │   ├── tagging_action_plan.txt        # Main actionable output
│   │   ├── tag_data_[timestamp].json      # Raw tag data
│   │   └── [other analysis reports]
│   │   └── [other analysis reports]
│   └── archive/               # Automatically archived old reports
│       └── [timestamp]/
├── archive/                   # Archived scripts and docs
└── docs/                      # Documentation
```

## 🏷️ Tag Format Guidelines

1. **Use underscores**: `machine_learning` not `machine-learning`
2. **Lowercase only**: `artificial_intelligence` not `Artificial_Intelligence`
3. **Be specific**: `higher_education` not just `education`
4. **Standard terms**: `k_12` not `k12` or `K-12`

## 💡 Best Practices

1. **Start with tagging_action_plan.txt** - Focus on HIGH PRIORITY articles first
2. **Use 7-category framework** - Ensures comprehensive tagging
3. **Aim for 15-20 tags** - Balances detail with usability
4. **Regular maintenance** - Run deep analysis weekly/monthly
5. **Archive old reports** - Happens automatically

## 🔄 Complete Workflow Example

```bash
# 1. Run deep analysis
cd "/Users/niklaskarlsson/Obsidian Sandbox/Research Hub"
python3 claude_workspace/system1_tagging/scripts/deep_analysis_workflow.py

# 2. Review action plan
cat claude_workspace/system1_tagging/export/current/tagging_action_plan.txt

# 3. Add tags to claude_workspace/system1_tagging/manual_tag_suggestions.json

# 4. Apply the tags
python3 claude_workspace/system1_tagging/scripts/obsidian_article_tagger.py --apply-suggestions

# 5. Re-run analysis to track progress
python3 claude_workspace/system1_tagging/scripts/deep_analysis_workflow.py
```

## 🚧 Known Issues

- **Filename Mismatches**: Some articles in manual_tag_suggestions.json have newlines in filenames
  - Solution: Clean filenames in the JSON file or use exact filename matching

## 🔮 Future Features

- Claude API integration for automated tag suggestions
- Batch processing with AI analysis
- Real-time tag quality monitoring
- Automatic filename validation and correction