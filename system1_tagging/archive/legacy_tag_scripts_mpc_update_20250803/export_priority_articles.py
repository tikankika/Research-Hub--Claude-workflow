#!/usr/bin/env python3
"""
Export Priority Articles for Tagging

Creates focused lists of articles that need immediate tag attention,
organized by priority level for efficient batch processing.

Usage:
    python3 export_priority_articles.py [--no-tags-limit N] [--few-tags-limit N]

Author: Claude Code Assistant  
Date: 2025-08-03
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import sys
from typing import Dict, List

# Import the analyzer
from article_tag_priority_analyzer import ArticleTagAnalyzer

def export_priority_lists(analyzer: ArticleTagAnalyzer, 
                         no_tags_limit: int = 50, 
                         few_tags_limit: int = 30) -> Dict[str, List]:
    """Export organized priority lists for different tagging workflows."""
    
    if not analyzer.analysis_results:
        analyzer.analyze_all_articles()
    
    results = analyzer.analysis_results
    
    # Categorize articles
    categories = {
        'no_tags_with_abstract': [],
        'no_tags_without_abstract': [],
        'few_tags_with_abstract': [],
        'few_tags_without_abstract': [],
        'format_issues': [],
        'author_tags_only': []
    }
    
    for filename, analysis in results.items():
        # No tags
        if analysis['total_tags'] == 0:
            if analysis['has_abstract']:
                categories['no_tags_with_abstract'].append((filename, analysis))
            else:
                categories['no_tags_without_abstract'].append((filename, analysis))
        
        # Few tags (1-2)
        elif 1 <= analysis['total_tags'] <= 2:
            if analysis['has_abstract']:
                categories['few_tags_with_abstract'].append((filename, analysis))
            else:
                categories['few_tags_without_abstract'].append((filename, analysis))
        
        # Author tags only
        if analysis['author_tags_only']:
            categories['author_tags_only'].append((filename, analysis))
        
        # Format issues
        if analysis['tag_format_issues']:
            categories['format_issues'].append((filename, analysis))
    
    # Sort each category by priority score
    for category in categories:
        categories[category].sort(key=lambda x: x[1]['priority_score'], reverse=True)
    
    return categories

def create_batch_file_lists(categories: Dict, output_dir: Path, 
                           no_tags_limit: int, few_tags_limit: int) -> None:
    """Create text files with article filenames for batch processing."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # High priority: No tags with abstracts (easiest to tag)
    high_priority_file = output_dir / f"batch_high_priority_{timestamp}.txt"
    with open(high_priority_file, 'w', encoding='utf-8') as f:
        f.write("# High Priority: No tags, has abstract (easiest to tag)\n")
        f.write(f"# Generated: {datetime.now()}\n")
        f.write(f"# Count: {len(categories['no_tags_with_abstract'][:no_tags_limit])}\n\n")
        
        for filename, analysis in categories['no_tags_with_abstract'][:no_tags_limit]:
            f.write(f"{filename}\n")
    
    # Medium priority: Few tags with abstracts
    medium_priority_file = output_dir / f"batch_medium_priority_{timestamp}.txt"
    with open(medium_priority_file, 'w', encoding='utf-8') as f:
        f.write("# Medium Priority: 1-2 tags, has abstract (needs tag expansion)\n")
        f.write(f"# Generated: {datetime.now()}\n")
        f.write(f"# Count: {len(categories['few_tags_with_abstract'][:few_tags_limit])}\n\n")
        
        for filename, analysis in categories['few_tags_with_abstract'][:few_tags_limit]:
            existing_tags = ', '.join(analysis['hashtag_tags'] + analysis['yaml_tags'])
            f.write(f"{filename}  # Current tags: {existing_tags}\n")
    
    # Manual review needed: No abstract articles
    manual_review_file = output_dir / f"manual_review_needed_{timestamp}.txt"
    with open(manual_review_file, 'w', encoding='utf-8') as f:
        f.write("# Manual Review Needed: No abstract (harder to tag automatically)\n")
        f.write(f"# Generated: {datetime.now()}\n")
        f.write(f"# Count: {len(categories['no_tags_without_abstract'][:25])}\n\n")
        
        for filename, analysis in categories['no_tags_without_abstract'][:25]:
            paperpile_status = "Paperpile" if analysis['has_paperpile_metadata'] else "Manual"
            f.write(f"{filename}  # {paperpile_status} metadata\n")
    
    print(f"📄 Created batch processing files:")
    print(f"   High Priority (no tags + abstract): {high_priority_file}")
    print(f"   Medium Priority (few tags + abstract): {medium_priority_file}")
    print(f"   Manual Review Needed (no abstract): {manual_review_file}")

def create_detailed_report(categories: Dict, output_dir: Path) -> None:
    """Create a detailed markdown report with actionable insights."""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = output_dir / f"priority_tagging_action_plan_{timestamp}.md"
    
    # Calculate statistics
    total_no_tags = len(categories['no_tags_with_abstract']) + len(categories['no_tags_without_abstract'])
    total_few_tags = len(categories['few_tags_with_abstract']) + len(categories['few_tags_without_abstract'])
    
    report_content = f"""
# Priority Tagging Action Plan
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

### Immediate Action Required
- **🔴 No Tags (Total: {total_no_tags})**: {len(categories['no_tags_with_abstract'])} with abstracts, {len(categories['no_tags_without_abstract'])} without
- **🟡 Few Tags (Total: {total_few_tags})**: {len(categories['few_tags_with_abstract'])} with abstracts, {len(categories['few_tags_without_abstract'])} without  
- **⚠️ Format Issues**: {len(categories['format_issues'])} articles need tag cleanup

## Recommended Workflow

### Phase 1: Quick Wins (Batch Processing)
**Target**: Articles with abstracts but no tags (easiest to process)

```bash
# Process top 50 no-tag articles with abstracts
python3 obsidian_article_tagger.py --batch --limit 50 --target-list batch_high_priority_{timestamp.split('_')[0]}.txt
python3 obsidian_article_tagger.py --review
```

**Top 20 High-Priority Articles (No Tags + Abstract):**
"""
    
    # Add top high-priority articles
    for i, (filename, analysis) in enumerate(categories['no_tags_with_abstract'][:20], 1):
        paperpile = "📋" if analysis['has_paperpile_metadata'] else "📝"
        report_content += f"{i:2d}. {filename} {paperpile}\n"
    
    report_content += f"""

### Phase 2: Tag Enhancement
**Target**: Articles with 1-2 tags that need expansion

**Top 15 Articles Needing Tag Enhancement:**
"""
    
    for i, (filename, analysis) in enumerate(categories['few_tags_with_abstract'][:15], 1):
        existing_tags = ', '.join(analysis['hashtag_tags'] + analysis['yaml_tags'])
        report_content += f"{i:2d}. {filename}\n"
        report_content += f"    Current tags: `{existing_tags}`\n"
    
    report_content += f"""

### Phase 3: Manual Review Required
**Target**: Articles without abstracts (need careful manual review)

**Top 10 Articles for Manual Review:**
"""
    
    for i, (filename, analysis) in enumerate(categories['no_tags_without_abstract'][:10], 1):
        paperpile = "📋 Paperpile" if analysis['has_paperpile_metadata'] else "📝 Manual"
        report_content += f"{i:2d}. {filename} ({paperpile})\n"
    
    if categories['format_issues']:
        report_content += f"""

### Phase 4: Format Cleanup
**Target**: Fix tag format issues across all articles

```bash
# Clean up tag formats
python3 obsidian_tag_tools.py cleanup --execute
```

**Common Format Issues Found:**
"""
        
        # Analyze format issues
        format_issue_counts = {}
        for filename, analysis in categories['format_issues'][:100]:  # Sample first 100
            for issue in analysis['tag_format_issues']:
                format_issue_counts[issue] = format_issue_counts.get(issue, 0) + 1
        
        for issue, count in sorted(format_issue_counts.items(), key=lambda x: x[1], reverse=True):
            report_content += f"- **{issue}**: {count} articles\n"
    
    report_content += f"""

## Success Metrics

Track progress by running the analyzer again after each phase:

```bash
python3 article_tag_priority_analyzer.py --limit 20
```

### Target Goals:
- **Phase 1**: Reduce no-tag articles by 50+ (from {len(categories['no_tags_with_abstract'])})
- **Phase 2**: Enhance tags for 30+ articles  
- **Phase 3**: Manually review 20+ difficult cases
- **Phase 4**: Fix format issues in 100+ articles

## Next Steps

1. **Start with Phase 1** - Use the batch tagging tool on articles with abstracts
2. **Review generated tags** - Use the review mode to ensure quality
3. **Move to Phase 2** - Expand existing tags for better specificity
4. **Track progress** - Re-run this analyzer weekly to monitor improvements

---
*Generated by Article Tag Priority Analyzer*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📋 Detailed action plan created: {report_file}")

def main():
    parser = argparse.ArgumentParser(description='Export priority article lists for tagging')
    parser.add_argument('--no-tags-limit', type=int, default=50,
                       help='Number of no-tag articles to export (default: 50)')
    parser.add_argument('--few-tags-limit', type=int, default=30,
                       help='Number of few-tag articles to export (default: 30)')
    parser.add_argument('--vault-path', type=str,
                       default='/Users/niklaskarlsson/Obsidian Sandbox/Book project, Sandbox',
                       help='Path to the Obsidian vault')
    
    args = parser.parse_args()
    
    try:
        analyzer = ArticleTagAnalyzer(args.vault_path)
        
        print("🔍 Analyzing articles for priority export...")
        categories = export_priority_lists(analyzer, args.no_tags_limit, args.few_tags_limit)
        
        # Create output directory
        output_dir = Path(args.vault_path) / "claude_workspace" / "export"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("📤 Creating batch processing files...")
        create_batch_file_lists(categories, output_dir, args.no_tags_limit, args.few_tags_limit)
        
        print("📋 Creating detailed action plan...")
        create_detailed_report(categories, output_dir)
        
        # Print summary
        print(f"\n✅ Export completed!")
        print(f"📊 Summary:")
        print(f"   • No tags with abstract: {len(categories['no_tags_with_abstract'])}")
        print(f"   • No tags without abstract: {len(categories['no_tags_without_abstract'])}")
        print(f"   • Few tags with abstract: {len(categories['few_tags_with_abstract'])}")
        print(f"   • Few tags without abstract: {len(categories['few_tags_without_abstract'])}")
        print(f"   • Format issues: {len(categories['format_issues'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())