#!/usr/bin/env python3
"""
Article Tag Priority Analyzer

Analyzes all articles in the '4 Articles' folder to identify which ones are most
in need of tag updates. Provides a comprehensive report with priority rankings.

Usage:
    python3 article_tag_priority_analyzer.py [--limit N] [--export-json]

Author: Claude Code Assistant
Date: 2025-08-03
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime
from collections import defaultdict, Counter
import sys

# Add the parent directory to Python path for shared utilities
sys.path.append(str(Path(__file__).parent.parent.parent))

class ArticleTagAnalyzer:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.articles_path = self.vault_path / "4 Articles"
        
        # Quality indicators
        self.author_tag_pattern = re.compile(r'#[^#\s]+_$')  # Tags ending with underscore
        self.generic_tags = {
            'ai', 'education', 'technology', 'learning', 'study', 'research',
            'article', 'paper', 'analysis', 'review', 'method', 'data'
        }
        self.outdated_formats = {
            'hashtag_only',  # Only hashtag tags, no yaml
            'mixed_format',  # Both hashtag and yaml inconsistently  
            'malformed'      # Broken tag syntax
        }
        
        # Analysis results
        self.analysis_results = {}
        self.priority_scores = {}
        
    def extract_tags_from_file(self, file_path: Path) -> Dict:
        """Extract all tag information from a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {'error': str(e)}
            
        result = {
            'file_path': str(file_path),
            'filename': file_path.name,
            'hashtag_tags': [],
            'yaml_tags': [],
            'has_abstract': False,
            'has_paperpile_metadata': False,
            'tag_format_issues': [],
            'total_tags': 0,
            'author_tags_only': False,
            'generic_tags_only': False,
            'tag_quality_score': 0
        }
        
        # Check for abstract
        result['has_abstract'] = bool(re.search(r'## Abstract\s*\n\s*\n\s*[A-Z]', content, re.MULTILINE))
        
        # Check for Paperpile metadata
        result['has_paperpile_metadata'] = '<!-- PAPERPILE METADATA START -->' in content
        
        # Extract YAML frontmatter tags
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            # Look for tags in YAML
            tags_match = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n)*)', yaml_content, re.MULTILINE)
            if tags_match:
                tags_text = tags_match.group(1)
                yaml_tags = re.findall(r'-\s*([^#\n]+)', tags_text)
                result['yaml_tags'] = [tag.strip().strip('"\'') for tag in yaml_tags if tag.strip()]
        
        # Extract hashtag tags (looking in Tags section specifically)
        tags_section_match = re.search(r'<!-- SCRIPT GENERATED START -->\s*## Tags\s*\n(.*?)<!-- SCRIPT GENERATED END -->', content, re.DOTALL)
        if tags_section_match:
            tags_section = tags_section_match.group(1)
            # Find hashtag tags
            hashtag_tags = re.findall(r'#([a-zA-Z0-9_åäöÅÄÖ-]+)', tags_section)
            result['hashtag_tags'] = list(set(hashtag_tags))  # Remove duplicates
        else:
            # Look for hashtag tags anywhere in the document
            hashtag_tags = re.findall(r'#([a-zA-Z0-9_åäöÅÄÖ-]+)', content)
            result['hashtag_tags'] = list(set(hashtag_tags))
        
        # Analyze tag format issues
        if result['yaml_tags'] and result['hashtag_tags']:
            result['tag_format_issues'].append('mixed_format')
        
        # Check for malformed tags
        malformed_patterns = [
            r'#[^#\s]*,[^#\s]*',  # Tags with commas
            r'##\s*$',            # Empty double hashtags
            r'#\s+[a-zA-Z]',      # Hashtag with space
        ]
        for pattern in malformed_patterns:
            if re.search(pattern, content):
                result['tag_format_issues'].append('malformed')
                break
        
        # Calculate totals and quality metrics
        all_tags = result['hashtag_tags'] + result['yaml_tags']
        result['total_tags'] = len(all_tags)
        
        # Check if only author tags (ending with underscore)
        if all_tags:
            author_tags = [tag for tag in all_tags if tag.endswith('_')]
            result['author_tags_only'] = len(author_tags) == len(all_tags) and len(author_tags) > 0
        
        # Check if only generic tags
        if all_tags:
            generic_count = sum(1 for tag in all_tags if tag.lower() in self.generic_tags)
            result['generic_tags_only'] = generic_count == len(all_tags) and generic_count > 0
        
        # Calculate tag quality score (0-100)
        score = 0
        if result['total_tags'] > 0:
            score += min(result['total_tags'] * 10, 50)  # Up to 50 points for having tags
            if result['total_tags'] >= 3:
                score += 20  # Bonus for sufficient tags
            if not result['author_tags_only']:
                score += 15  # Bonus for non-author tags
            if not result['generic_tags_only']:
                score += 15  # Bonus for specific tags
        
        result['tag_quality_score'] = score
        
        return result
    
    def calculate_priority_score(self, analysis: Dict) -> int:
        """Calculate priority score for tag updates (higher = more urgent)."""
        score = 0
        
        # No tags at all - highest priority
        if analysis['total_tags'] == 0:
            score += 100
        
        # Very few tags
        elif analysis['total_tags'] <= 2:
            score += 80
        
        # Only author tags
        if analysis['author_tags_only']:
            score += 60
        
        # Only generic tags
        if analysis['generic_tags_only']:
            score += 50
        
        # Missing abstract - harder to tag properly
        if not analysis['has_abstract']:
            score += 30
        
        # Tag format issues
        if analysis['tag_format_issues']:
            score += 25
        
        # Has Paperpile metadata but few tags - missed opportunity
        if analysis['has_paperpile_metadata'] and analysis['total_tags'] <= 2:
            score += 15
        
        # Penalize if already has good tags
        if analysis['tag_quality_score'] > 75:
            score -= 50
        
        return max(0, score)  # Ensure non-negative
    
    def analyze_all_articles(self) -> Dict:
        """Analyze all articles in the 4 Articles folder."""
        if not self.articles_path.exists():
            raise FileNotFoundError(f"Articles path not found: {self.articles_path}")
        
        print(f"Analyzing articles in: {self.articles_path}")
        
        markdown_files = list(self.articles_path.glob("*.md"))
        total_files = len(markdown_files)
        
        print(f"Found {total_files} markdown files to analyze...")
        
        results = {}
        for i, file_path in enumerate(markdown_files, 1):
            if i % 100 == 0:
                print(f"Processed {i}/{total_files} files...")
            
            analysis = self.extract_tags_from_file(file_path)
            if 'error' not in analysis:
                priority_score = self.calculate_priority_score(analysis)
                analysis['priority_score'] = priority_score
                results[file_path.name] = analysis
        
        self.analysis_results = results
        print(f"Analysis complete! Processed {len(results)} files.")
        return results
    
    def generate_report(self, limit: int = 30) -> str:
        """Generate a comprehensive report."""
        if not self.analysis_results:
            return "No analysis results available. Run analyze_all_articles() first."
        
        # Sort by priority score (descending)
        sorted_results = sorted(
            self.analysis_results.items(),
            key=lambda x: x[1]['priority_score'],
            reverse=True
        )
        
        # Statistics
        total_articles = len(self.analysis_results)
        no_tags = sum(1 for _, analysis in self.analysis_results.items() if analysis['total_tags'] == 0)
        few_tags = sum(1 for _, analysis in self.analysis_results.items() if 1 <= analysis['total_tags'] <= 2)
        author_only = sum(1 for _, analysis in self.analysis_results.items() if analysis['author_tags_only'])
        no_abstract = sum(1 for _, analysis in self.analysis_results.items() if not analysis['has_abstract'])
        format_issues = sum(1 for _, analysis in self.analysis_results.items() if analysis['tag_format_issues'])
        
        report = f"""
# Article Tag Priority Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary Statistics
- **Total Articles Analyzed:** {total_articles:,}
- **Articles with No Tags:** {no_tags:,} ({no_tags/total_articles*100:.1f}%)
- **Articles with 1-2 Tags Only:** {few_tags:,} ({few_tags/total_articles*100:.1f}%)
- **Articles with Only Author Tags:** {author_only:,} ({author_only/total_articles*100:.1f}%)
- **Articles Missing Abstracts:** {no_abstract:,} ({no_abstract/total_articles*100:.1f}%)
- **Articles with Tag Format Issues:** {format_issues:,} ({format_issues/total_articles*100:.1f}%)

## Priority Categories

### 🔴 CRITICAL PRIORITY: Articles with No Tags
"""
        
        # Critical priority - no tags
        no_tag_articles = [(name, analysis) for name, analysis in sorted_results 
                          if analysis['total_tags'] == 0]
        
        report += f"**Count:** {len(no_tag_articles)} articles\n\n"
        
        for name, analysis in no_tag_articles[:15]:  # Show top 15
            abstract_status = "✅ Has Abstract" if analysis['has_abstract'] else "❌ No Abstract"
            paperpile_status = "📋 Paperpile" if analysis['has_paperpile_metadata'] else "📄 Manual"
            report += f"- **{name}** (Score: {analysis['priority_score']}) - {abstract_status}, {paperpile_status}\n"
        
        if len(no_tag_articles) > 15:
            report += f"... and {len(no_tag_articles) - 15} more\n"
        
        # High priority - insufficient tags
        insufficient_tags = [(name, analysis) for name, analysis in sorted_results 
                           if 1 <= analysis['total_tags'] <= 2]
        
        report += f"""

### 🟡 HIGH PRIORITY: Articles with Insufficient Tags (1-2 tags)
**Count:** {len(insufficient_tags)} articles

"""
        
        for name, analysis in insufficient_tags[:10]:  # Show top 10
            tags_info = f"Tags: {analysis['total_tags']} ({'hashtag' if analysis['hashtag_tags'] else 'yaml'})"
            abstract_status = "✅ Abstract" if analysis['has_abstract'] else "❌ No Abstract"
            report += f"- **{name}** (Score: {analysis['priority_score']}) - {tags_info}, {abstract_status}\n"
        
        if len(insufficient_tags) > 10:
            report += f"... and {len(insufficient_tags) - 10} more\n"
        
        # Medium priority - author tags only
        author_only_articles = [(name, analysis) for name, analysis in sorted_results 
                               if analysis['author_tags_only'] and analysis['total_tags'] > 2]
        
        if author_only_articles:
            report += f"""

### 🟠 MEDIUM PRIORITY: Articles with Only Author Tags
**Count:** {len(author_only_articles)} articles

"""
            
            for name, analysis in author_only_articles[:8]:  # Show top 8
                tags_count = analysis['total_tags']
                report += f"- **{name}** (Score: {analysis['priority_score']}) - {tags_count} author tags only\n"
        
        # Format issues
        format_issue_articles = [(name, analysis) for name, analysis in sorted_results 
                               if analysis['tag_format_issues']]
        
        if format_issue_articles:
            report += f"""

### ⚠️ FORMAT ISSUES: Articles with Tag Format Problems
**Count:** {len(format_issue_articles)} articles

"""
            
            for name, analysis in format_issue_articles[:8]:  # Show top 8
                issues = ', '.join(analysis['tag_format_issues'])
                report += f"- **{name}** (Score: {analysis['priority_score']}) - Issues: {issues}\n"
        
        # Top priority list for immediate action
        report += f"""

## 🎯 TOP {limit} ARTICLES FOR IMMEDIATE TAG UPDATES

These articles have been ranked by priority score combining multiple factors:
- Lack of tags (highest weight)
- Insufficient tag count
- Only author/generic tags
- Missing abstracts
- Format issues

"""
        
        for i, (name, analysis) in enumerate(sorted_results[:limit], 1):
            tags_desc = f"{analysis['total_tags']} tags"
            if analysis['total_tags'] == 0:
                tags_desc = "❌ NO TAGS"
            elif analysis['author_tags_only']:
                tags_desc += " (author only)"
            elif analysis['generic_tags_only']:
                tags_desc += " (generic only)"
            
            abstract_icon = "📄" if analysis['has_abstract'] else "❓"
            paperpile_icon = "📋" if analysis['has_paperpile_metadata'] else "📝"
            
            issues = ""
            if analysis['tag_format_issues']:
                issues = f" ⚠️ {', '.join(analysis['tag_format_issues'])}"
            
            report += f"{i:2d}. **{name}** (Priority: {analysis['priority_score']}) {abstract_icon}{paperpile_icon}\n"
            report += f"    {tags_desc}{issues}\n\n"
        
        # Additional insights
        report += """

## 💡 Recommendations

### For Articles with No Tags:
1. Start with articles that have abstracts (easier to tag)
2. Use the batch tagging tool: `python3 obsidian_article_tagger.py --batch --limit 20`
3. Focus on Paperpile-synced articles first (better metadata)

### For Articles with Few Tags:
1. Review existing tags for quality and specificity
2. Add domain-specific tags based on abstracts
3. Consider methodology, research area, and key concepts

### For Format Issues:
1. Standardize to hashtag format in the Tags section
2. Remove malformed tags and fix syntax
3. Use tag cleanup tools: `python3 obsidian_tag_tools.py cleanup`

## 🔧 Suggested Workflow

1. **Batch process no-tag articles:**
   ```bash
   python3 obsidian_article_tagger.py --batch --limit 50
   python3 obsidian_article_tagger.py --review
   ```

2. **Review and update priority articles manually**

3. **Run this analyzer again to track progress:**
   ```bash
   python3 article_tag_priority_analyzer.py --limit 20
   ```
"""
        
        return report
    
    def export_json(self, output_path: Path) -> None:
        """Export analysis results to JSON for further processing."""
        if not self.analysis_results:
            print("No analysis results to export.")
            return
        
        # Prepare data for JSON export
        export_data = {
            'analysis_date': datetime.now().isoformat(),
            'total_articles': len(self.analysis_results),
            'statistics': {
                'no_tags': sum(1 for analysis in self.analysis_results.values() if analysis['total_tags'] == 0),
                'few_tags': sum(1 for analysis in self.analysis_results.values() if 1 <= analysis['total_tags'] <= 2),
                'author_only': sum(1 for analysis in self.analysis_results.values() if analysis['author_tags_only']),
                'no_abstract': sum(1 for analysis in self.analysis_results.values() if not analysis['has_abstract']),
                'format_issues': sum(1 for analysis in self.analysis_results.values() if analysis['tag_format_issues'])
            },
            'articles': self.analysis_results
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis results exported to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Analyze articles for tag update priorities')
    parser.add_argument('--limit', type=int, default=30, 
                       help='Number of top priority articles to show (default: 30)')
    parser.add_argument('--export-json', action='store_true',
                       help='Export detailed results to JSON file')
    parser.add_argument('--vault-path', type=str, 
                       default='/Users/niklaskarlsson/Obsidian Sandbox/Book project, Sandbox',
                       help='Path to the Obsidian vault')
    
    args = parser.parse_args()
    
    try:
        analyzer = ArticleTagAnalyzer(args.vault_path)
        
        print("🔍 Starting article tag analysis...")
        analyzer.analyze_all_articles()
        
        print("\n📊 Generating report...")
        report = analyzer.generate_report(limit=args.limit)
        
        # Save report to file
        output_dir = Path(args.vault_path) / Path(__file__).parent.parent / "export"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = output_dir / f"article_tag_priority_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📝 Report saved to: {report_file}")
        
        # Export JSON if requested
        if args.export_json:
            json_file = output_dir / f"article_tag_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            analyzer.export_json(json_file)
        
        # Print report to console
        print("\n" + "="*80)
        print(report)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())