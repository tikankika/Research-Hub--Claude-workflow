#!/usr/bin/env python3
"""Tag articles that have absolutely no tags - for use with Claude"""

import sys
import re
from pathlib import Path

sys.path.append('.')
from obsidian_article_tagger import ObsidianArticleTagger

class NoTagArticleTagger(ObsidianArticleTagger):
    """Modified tagger that only processes articles with NO tags"""
    
    def _is_untagged(self, file_path: Path) -> bool:
        """Check if article has NO tags at all"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for empty Tags section pattern
            has_empty_tags = re.search(r'## Tags\s*\n\n##', content, re.DOTALL)
            
            # Look for any hashtags
            hashtags = re.findall(r'#[\w_]+', content)
            
            # Filter out author tags ending with underscore
            real_tags = [tag for tag in hashtags if not tag.endswith('_')]
            
            # Only return True if empty tags section or no real tags
            return has_empty_tags is not None or len(real_tags) == 0
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False

def main():
    """Run tagging session for articles with NO tags"""
    tagger = NoTagArticleTagger('.')
    
    print("\n🎯 TAGGING ARTICLES WITH NO TAGS")
    print("="*60)
    print("This will process articles that have absolutely no tags")
    print("Claude will analyze each article and suggest appropriate tags\n")
    
    # Find articles with no tags
    articles = tagger.find_articles_without_tags(limit=100, require_abstract=True)
    
    # Filter to only those with truly no tags
    no_tag_articles = []
    for article in articles:
        if tagger._is_untagged(article):
            no_tag_articles.append(article)
    
    print(f"Found {len(no_tag_articles)} articles with NO tags (and abstracts)")
    
    if not no_tag_articles:
        print("All articles have at least some tags!")
        return
    
    # Process up to 10 articles
    limit = min(10, len(no_tag_articles))
    print(f"\nProcessing first {limit} articles...\n")
    
    for i, article in enumerate(no_tag_articles[:limit], 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{limit}] Processing: {article.name}")
        print(f"{'='*60}")
        
        # Extract metadata
        metadata = tagger.extract_article_metadata(article)
        
        print(f"Title: {metadata.get('title', 'Unknown')[:80]}...")
        print(f"Abstract: {metadata.get('abstract', 'No abstract')[:150]}...")
        
        # This is where Claude should analyze and suggest tags
        print("\n🤖 Claude should analyze this article and suggest 3-6 relevant tags based on:")
        print("- The abstract content")
        print("- The research methodology")
        print("- The educational level/context")
        print("- The technologies mentioned")
        print("- The theoretical framework")
        
        print("\nSuggested tags format:")
        print("#tag1, #tag2, #tag3, #tag4, #tag5")
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    main()