#!/usr/bin/env python3
"""
Obsidian Tag Tools - Unified tagging management system
Combines functionality from multiple scripts into one comprehensive tool
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import VAULT_PATH

# Import the existing modules
sys.path.append(str(Path(__file__).parent.parent))
from obsidian_tag_manager import ObsidianTagManager
from obsidian_article_tagger import ObsidianArticleTagger
from standardize_all_tags import TagStandardizer
from merge_duplicate_tags import TAG_MERGES, ADDITIONAL_MERGES

class ObsidianTagTools:
    """Unified interface for all tag operations"""
    
    def __init__(self, vault_path: str = None):
        # Use config default if not specified
        if vault_path is None:
            vault_path = str(VAULT_PATH)
        self.vault_path = Path(vault_path)
        self.tag_manager = ObsidianTagManager(vault_path)
        self.article_tagger = ObsidianArticleTagger(vault_path)
        self.tag_standardizer = TagStandardizer(vault_path)
        
    def run_full_cleanup(self, dry_run: bool = True):
        """Run complete tag cleanup workflow"""
        print("\n🏷️  Obsidian Tag Cleanup Workflow")
        print("="*60)
        
        # Step 1: Standardize tags to underscores
        print("\n📌 Step 1: Standardizing tags to use underscores...")
        std_result = self.tag_standardizer.apply_standardization(dry_run=dry_run)
        print(f"{'Would standardize' if dry_run else 'Standardized'} {std_result['changes_made']} tags")
        
        # Step 2: Merge duplicates
        print("\n📌 Step 2: Merging duplicate tags...")
        merge_count = 0
        for old_tag, new_tag, reason in TAG_MERGES:
            result = self.tag_manager.merge_tags(old_tag, new_tag, dry_run=dry_run)
            if 'error' not in result and result['files_affected'] > 0:
                merge_count += 1
        print(f"{'Would merge' if dry_run else 'Merged'} {merge_count} duplicate tag sets")
        
        # Step 3: Clean invalid tags
        print("\n📌 Step 3: Cleaning invalid tags...")
        clean_result = self.tag_manager.clean_tags(remove_single_use=False, dry_run=dry_run)
        print(f"{'Would remove' if dry_run else 'Removed'} {clean_result['tags_removed']} invalid tags")
        
        # Step 4: Generate report
        print("\n📌 Step 4: Generating tag report...")
        report_path = self.tag_manager.export_tag_report(format='txt', include_advanced=True)
        print(f"Report saved to: {report_path}")
        
        if dry_run:
            print("\n✅ Dry run complete. Use --execute to apply changes.")
        else:
            print("\n✅ Tag cleanup complete!")
            
    def tag_articles_workflow(self, limit: int = 5):
        """Workflow for tagging untagged articles"""
        print("\n📚 Article Tagging Workflow")
        print("="*60)
        
        # Find untagged articles
        untagged = self.article_tagger.find_articles_without_tags()
        print(f"\nFound {len(untagged)} articles without sufficient tags")
        
        if not untagged:
            print("All articles have tags!")
            return
            
        # Show sample and confirm
        print(f"\nWill tag up to {limit} articles:")
        for article in untagged[:limit]:
            print(f"  - {article.name}")
            
        response = input("\nProceed with tagging? (y/n): ")
        if response.lower() != 'y':
            print("Tagging cancelled.")
            return
            
        # Tag articles (would integrate with Claude here)
        print(f"\n🤖 Would tag {min(limit, len(untagged))} articles with Claude...")
        print("Note: Claude integration pending implementation")
        
    def analyze_vault(self):
        """Comprehensive vault analysis"""
        print("\n📊 Vault Tag Analysis")
        print("="*60)
        
        # Get analysis
        analysis = self.tag_manager.analyze_tags()
        
        # Display results
        print(f"\n📈 Statistics:")
        print(f"  Total unique tags: {analysis['total_unique_tags']}")
        print(f"  Total tag uses: {analysis['total_tag_uses']}")
        print(f"  Average uses per tag: {analysis['total_tag_uses'] / max(1, analysis['total_unique_tags']):.1f}")
        
        print(f"\n🏷️  Tag Distribution:")
        for category, count in analysis['tag_distribution'].items():
            print(f"  {category}: {count}")
            
        print(f"\n🔝 Top 10 Tags:")
        for tag, count in analysis['most_common'][:10]:
            print(f"  #{tag}: {count} uses")
            
        print(f"\n🔄 Potential Duplicates: {len(analysis['potential_duplicates'])}")
        for tag1, tag2, similarity in analysis['potential_duplicates'][:5]:
            print(f"  '{tag1}' ↔ '{tag2}' ({similarity:.1%})")
            
        # Find untagged articles
        untagged = self.article_tagger.find_articles_without_tags()
        print(f"\n📑 Articles needing tags: {len(untagged)}")

def main():
    parser = argparse.ArgumentParser(
        description='Obsidian Tag Tools - Comprehensive tag management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  analyze     - Analyze vault tags and show statistics
  cleanup     - Run full tag cleanup workflow (standardize, merge, clean)
  tag         - Find and tag articles without tags
  report      - Generate comprehensive tag report

Examples:
  # Analyze vault
  python obsidian_tag_tools.py analyze
  
  # Run full cleanup (dry run)
  python obsidian_tag_tools.py cleanup
  
  # Run full cleanup (execute)
  python obsidian_tag_tools.py cleanup --execute
  
  # Tag articles
  python obsidian_tag_tools.py tag --limit 10
"""
    )
    
    parser.add_argument('command', choices=['analyze', 'cleanup', 'tag', 'report'],
                       help='Command to execute')
    parser.add_argument('--vault-path', default='.',
                       help='Path to Obsidian vault')
    parser.add_argument('--execute', action='store_true',
                       help='Execute changes (not dry run)')
    parser.add_argument('--limit', type=int, default=5,
                       help='Number of articles to tag (default: 5)')
    parser.add_argument('--advanced', action='store_true',
                       help='Include advanced analysis in reports')
    
    args = parser.parse_args()
    
    try:
        tools = ObsidianTagTools(args.vault_path)
        
        if args.command == 'analyze':
            tools.analyze_vault()
            
        elif args.command == 'cleanup':
            tools.run_full_cleanup(dry_run=not args.execute)
            
        elif args.command == 'tag':
            tools.tag_articles_workflow(limit=args.limit)
            
        elif args.command == 'report':
            report_path = tools.tag_manager.export_tag_report(format='txt', include_advanced=args.advanced)
            print(f"Tag report saved to: {report_path}")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())