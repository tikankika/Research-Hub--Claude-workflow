#!/usr/bin/env python3
"""Tag articles with empty tag sections one by one"""

import sys
import re
from pathlib import Path

sys.path.append('claude_workspace/scripts/tagging')
from obsidian_article_tagger import ObsidianArticleTagger

def find_empty_tag_articles():
    """Find articles with empty tag sections"""
    vault_path = Path('.')
    articles_dir = vault_path / '4 Articles'
    
    empty_tag_articles = []
    for md_file in articles_dir.glob('*.md'):
        if md_file.is_file():
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for empty Tags section pattern
            if re.search(r'## Tags\s*\n\n##', content, re.DOTALL):
                # Check if has abstract
                if '## Abstract' in content:
                    abstract_text = content.split('## Abstract')[1].split('##')[0].strip()
                    if len(abstract_text) > 100:
                        empty_tag_articles.append(md_file)
    
    return empty_tag_articles

def process_article(article_path):
    """Process a single article"""
    tagger = ObsidianArticleTagger('.')
    
    print(f"\n🎯 Processing: {article_path.name}")
    print("="*60)
    
    # Extract metadata
    metadata = tagger.extract_article_metadata(article_path)
    
    print(f"Title: {metadata.get('title', 'Unknown')[:80]}...")
    print(f"Abstract: {metadata.get('abstract', 'No abstract')[:200]}...")
    
    # Analyze with Claude
    print("\n🤖 Analyzing with Claude...")
    print(f"Debug - Existing tags: {metadata.get('existing_tags', [])}")
    print(f"Debug - Keywords: {metadata.get('keywords', [])}")
    suggested_tags = tagger.analyze_with_claude(metadata, save_suggestion=True)
    
    if suggested_tags:
        print(f"\n✨ Suggested tags:")
        for tag in suggested_tags:
            print(f"   #{tag}")
        
        # Apply tags directly
        print("\n📝 Applying tags...")
        tagger.apply_tags_to_article(article_path, suggested_tags, replace_mode=True)
        print("✅ Tags applied successfully!")
        return True
    else:
        print("❌ No tags suggested by Claude")
        return False

def main():
    """Process articles one by one"""
    articles = find_empty_tag_articles()
    print(f"\n📊 Found {len(articles)} articles with empty tag sections")
    
    # Process first 5 articles
    limit = 5
    success_count = 0
    
    for i, article in enumerate(articles[:limit], 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{limit}] Processing articles...")
        
        if process_article(article):
            success_count += 1
        
        # Brief pause between articles (removed for non-interactive mode)
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY: Successfully tagged {success_count}/{limit} articles")

if __name__ == "__main__":
    main()