#!/usr/bin/env python3
"""Process articles that have manual tag suggestions"""

import sys
from pathlib import Path

sys.path.append('.')
from obsidian_article_tagger import ObsidianArticleTagger

def main():
    """Process articles with manual suggestions"""
    tagger = ObsidianArticleTagger('.')
    
    # Articles we have manual suggestions for
    target_articles = [
        "Hines2008-ms.md",
        "Van_Le2024-fg.md", 
        "Chatti2007-ss.md",
        "Scardamalia2004-qv.md",
        "Ivarsson2010-dx.md"
    ]
    
    success_count = 0
    
    for article_name in target_articles:
        article_path = Path('4 Articles') / article_name
        
        if not article_path.exists():
            print(f"❌ Article not found: {article_name}")
            continue
            
        print(f"\n{'='*60}")
        print(f"📄 Processing: {article_name}")
        print(f"{'='*60}")
        
        # Extract metadata
        metadata = tagger.extract_article_metadata(article_path)
        print(f"Title: {metadata.get('title', 'Unknown')[:80]}...")
        
        # Get tags from manual suggestions
        tags = tagger.analyze_with_claude(metadata, save_suggestion=True)
        
        if tags:
            print(f"\n✅ Tags found: {', '.join(['#' + t for t in tags])}")
            
            # Apply tags
            print("📝 Applying tags to article...")
            tagger.apply_tags_to_article(article_path, tags, replace_mode=True)
            print("✅ Tags applied successfully!")
            success_count += 1
        else:
            print("❌ No tags found")
    
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY: Tagged {success_count}/{len(target_articles)} articles")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()