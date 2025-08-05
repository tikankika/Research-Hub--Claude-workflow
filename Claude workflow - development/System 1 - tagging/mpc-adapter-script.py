#!/usr/bin/env python3
"""
Adapt the existing batch tagger to create single MPC files for Claude Desktop
This is a simple wrapper that uses the existing functionality
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Import the existing batch tagger
sys.path.append(str(Path(__file__).parent))
from obsidian_batch_tagger import ObsidianBatchTagger
from ..config import VAULT_PATH

def load_tag_statistics(vault_path):
    """Load the most recent tag statistics from tag_data_*.json"""
    tag_data_files = list(Path(vault_path).glob('claude_workspace/scripts/tagging/tag_data_*.json'))
    if not tag_data_files:
        return {}
    
    # Get most recent file
    latest_file = max(tag_data_files, key=lambda p: p.stat().st_mtime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    # Get top 20 tags by usage
    tag_usage = data.get('tag_usage', {})
    sorted_tags = sorted(tag_usage.items(), key=lambda x: x[1], reverse=True)[:20]
    
    return sorted_tags

def create_mpc_for_article(article_file: str, vault_path: str):
    """Create an MPC file for a single article"""
    
    # Initialize the batch tagger
    tagger = ObsidianBatchTagger(vault_path)
    
    # Find the article
    article_path = Path(vault_path) / "4 Articles" / article_file
    if not article_path.exists():
        print(f"Error: Article not found: {article_file}")
        return None
    
    # Extract article info using existing functionality
    article_info = tagger.extract_article_info(article_path)
    
    # Load tag statistics
    top_tags = load_tag_statistics(vault_path)
    
    # Create MPC content
    mpc_content = f"""# Tagging Request for Claude Desktop

## Article: {article_info.get('title', 'Untitled')}

**File:** {article_info['filename']}
**Authors:** {article_info.get('authors', 'Unknown')}
**Year:** {article_info.get('year', 'Unknown')}
**Journal:** {article_info.get('journal', 'N/A')}

## Abstract
{article_info.get('abstract', '[No abstract found]')}

## Content Preview
{article_info.get('full_text', '[No content preview available]')}

## Current Vault Tag Statistics
Your vault uses these tags most frequently (for consistency):
"""
    
    # Add top tags
    for tag, count in top_tags:
        if not tag.startswith(('said', 'sade', 'perspective', 'who', 'what')):  # Skip noise tags
            mpc_content += f"- #{tag} ({count} uses)\n"
    
    mpc_content += """
## Tagging Guidelines
1. Suggest 3-7 relevant tags based on the article content
2. Prefer existing tags from the list above when appropriate
3. Use snake_case format (e.g., machine_learning, higher_education)
4. Focus on:
   - Main topic/domain
   - Research methodology
   - Educational level
   - Technology mentioned
   - Key concepts

## Your Tag Suggestions:
[Please provide 3-7 tags below]

"""
    
    # Save MPC file
    mpc_dir = Path(vault_path) / 'claude_workspace' / 'mpc_files'
    mpc_dir.mkdir(parents=True, exist_ok=True)
    
    mpc_filename = article_path.stem + '.mpc'
    mpc_path = mpc_dir / mpc_filename
    
    with open(mpc_path, 'w', encoding='utf-8') as f:
        f.write(mpc_content)
    
    print(f"✅ Created MPC file: {mpc_path}")
    print(f"\n📋 Next steps:")
    print(f"1. Open {mpc_filename} in Claude Desktop")
    print(f"2. Copy Claude's tag suggestions")
    print(f"3. Add to manual_tag_suggestions.json:")
    print(f'   "{article_file}": ["tag1", "tag2", "tag3"]')
    
    return mpc_path

def main():
    """Main function for command line usage"""
    if len(sys.argv) != 2:
        print("Usage: python3 adapt_batch_tagger_for_mpc.py 'ArticleName.md'")
        print("Example: python3 adapt_batch_tagger_for_mpc.py 'Hines2008-ms.md'")
        sys.exit(1)
    
    article_file = sys.argv[1]
    vault_path = str(VAULT_PATH)
    
    create_mpc_for_article(article_file, vault_path)

if __name__ == "__main__":
    main()
