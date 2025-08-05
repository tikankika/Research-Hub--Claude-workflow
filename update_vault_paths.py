#!/usr/bin/env python3
"""
Script to update all Python files to use the central config.py
"""

import os
import re
from pathlib import Path

# Files that need updating
files_to_update = [
    "Claude workflow - development/System 1 - tagging/mpc-adapter-script.py",
    "Claude workflow - development/System 1 - tagging/update-manual-suggestions.py",
    "misc_scripts/rename_articles.py",
    "misc_scripts/paperpile_to_markdown.py",
    "system1_bridge/scripts/analyze_vault.py",
    "system1_bridge/scripts/migrate_to_bibtex_keys.py",
    "system1_bridge/scripts/paperpile_sync.py",
    "system1_tagging/scripts/article_tag_priority_analyzer.py",
    "system1_tagging/scripts/comprehensive_tag_report.py",
    "system1_tagging/scripts/deep_analysis_workflow.py",
    "system1_tagging/scripts/export_priority_articles.py",
    "system1_tagging/scripts/obsidian_article_tagger.py",
    "system1_tagging/scripts/obsidian_batch_tagger.py",
    "system1_tagging/scripts/obsidian_tag_manager.py",
    "system1_tagging/scripts/process_manual_suggestions.py",
    "system1_tagging/scripts/standardize_all_tags.py",
    "system1_tagging/scripts/merge_duplicate_tags.py"
]

# Pattern to find the old vault path
old_path_pattern = r'"/Users/niklaskarlsson/Obsidian Sandbox/Research Hub"'
old_path_pattern2 = r"'/Users/niklaskarlsson/Obsidian Sandbox/Research Hub'"

def update_file(file_path):
    """Update a single file to use config.py"""
    full_path = Path(file_path)
    if not full_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False
    
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file contains the old path
    if old_path_pattern not in content and old_path_pattern2 not in content:
        print(f"ℹ️  No old path found in: {file_path}")
        return False
    
    # Calculate relative import path to config.py
    file_dir = full_path.parent
    root_dir = Path(__file__).parent
    
    # Calculate how many levels up to go
    rel_path = os.path.relpath(root_dir, file_dir)
    import_parts = rel_path.split(os.sep)
    
    if rel_path == '.':
        import_line = "from config import VAULT_PATH"
    else:
        dots = '.' * len(import_parts)
        import_line = f"from {dots}config import VAULT_PATH"
    
    # Add import if not already present
    if "from config import" not in content and "from .config import" not in content:
        # Find a good place to add the import
        lines = content.split('\n')
        import_index = 0
        
        # Find the last import statement
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                import_index = i + 1
        
        # Add our import after other imports
        lines.insert(import_index, import_line)
        content = '\n'.join(lines)
    
    # Replace the old path with VAULT_PATH
    content = re.sub(old_path_pattern, 'str(VAULT_PATH)', content)
    content = re.sub(old_path_pattern2, 'str(VAULT_PATH)', content)
    
    # Write back
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated: {file_path}")
    return True

def main():
    """Update all files"""
    print("Updating Python files to use config.py...")
    print("=" * 60)
    
    updated = 0
    for file_path in files_to_update:
        if update_file(file_path):
            updated += 1
    
    print("=" * 60)
    print(f"✅ Updated {updated} files")
    print("\nNow all scripts will use the vault path from config.py")
    print("To change the vault path, edit config.py")

if __name__ == "__main__":
    main()