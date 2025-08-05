#!/usr/bin/env python3
"""
Fix all references to claude_workspace export paths
"""

import re
from pathlib import Path

# Files to update (excluding archive folders)
files_to_update = [
    "system1_tagging/scripts/deep_analysis_workflow.py",
    "Claude workflow - development/System 1 - tagging/update-manual-suggestions.py",
    "Claude workflow - development/System 1 - tagging/mpc-adapter-script.py",
    "system1_bridge/scripts/paperpile_sync.py",
    "system1_bridge/scripts/migrate_to_bibtex_keys.py",
    "system1_bridge/scripts/analyze_vault.py",
    "system1_tagging/scripts/standardize_all_tags.py",
    "system1_tagging/scripts/obsidian_tag_manager.py",
    "system1_tagging/scripts/obsidian_batch_tagger.py",
    "system1_tagging/scripts/obsidian_article_tagger.py",
    "system1_tagging/scripts/export_priority_articles.py",
    "system1_tagging/scripts/comprehensive_tag_report.py",
    "system1_tagging/scripts/article_tag_priority_analyzer.py"
]

# Patterns to replace
replacements = [
    # Replace claude_workspace export paths
    (r'claude_workspace/system1_tagging/export', 'system1_tagging/export'),
    (r'"claude_workspace".*?/.*?"export"', 'Path(__file__).parent.parent / "export"'),
    (r'vault.*?/.*?claude_workspace.*?/.*?export', 'Path(__file__).parent.parent / "export"'),
    # Fix manual_tag_suggestions.json path
    (r'claude_workspace/system1_tagging/manual_tag_suggestions\.json', 'system1_tagging/manual_tag_suggestions.json'),
]

def fix_file(file_path):
    """Fix export paths in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply replacements
        for old_pattern, new_pattern in replacements:
            content = re.sub(old_pattern, new_pattern, content)
        
        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all files"""
    print("Fixing export paths in Python files...")
    print("=" * 60)
    
    fixed = 0
    for file_path in files_to_update:
        if fix_file(file_path):
            fixed += 1
    
    print("=" * 60)
    print(f"✅ Fixed {fixed} files")

if __name__ == "__main__":
    main()