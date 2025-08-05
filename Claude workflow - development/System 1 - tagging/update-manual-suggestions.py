#!/usr/bin/env python3
"""
Simple script to add Claude's tag suggestions to manual_tag_suggestions.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from ..config import VAULT_PATH

def update_suggestions(article_file: str, tags: str, vault_path: str):
    """Update manual_tag_suggestions.json with new tags"""
    
    suggestions_file = Path(vault_path) / 'claude_workspace' / 'scripts' / 'tagging' / 'manual_tag_suggestions.json'
    
    # Load existing suggestions
    if suggestions_file.exists():
        with open(suggestions_file, 'r') as f:
            suggestions = json.load(f)
    else:
        suggestions = {}
    
    # Parse tags (comma or space separated)
    tag_list = [tag.strip() for tag in tags.replace(',', ' ').split() if tag.strip()]
    
    # Clean tags (remove # if present)
    tag_list = [tag.lstrip('#') for tag in tag_list]
    
    # Update suggestions
    suggestions[article_file] = tag_list
    
    # Backup existing file
    if suggestions_file.exists():
        backup_path = suggestions_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        suggestions_file.rename(backup_path)
        print(f"📁 Backed up to: {backup_path.name}")
    
    # Write updated suggestions
    with open(suggestions_file, 'w') as f:
        json.dump(suggestions, f, indent=2)
    
    print(f"✅ Updated manual_tag_suggestions.json")
    print(f"📝 Added tags for {article_file}: {', '.join(tag_list)}")
    print(f"\n🔧 To apply these tags, run:")
    print(f"   python3 obsidian_article_tagger.py --auto-apply")

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 update_manual_suggestions.py 'ArticleName.md' 'tag1 tag2 tag3'")
        print("Example: python3 update_manual_suggestions.py 'Hines2008-ms.md' 'teacher_education blogging case_study'")
        sys.exit(1)
    
    article_file = sys.argv[1]
    tags = sys.argv[2]
    vault_path = str(VAULT_PATH)
    
    update_suggestions(article_file, tags, vault_path)

if __name__ == "__main__":
    main()
