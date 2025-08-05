#!/usr/bin/env python3
"""
Apply Tag Cleanup Script
========================
This script applies the recommended tag cleanups to your Obsidian vault.
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict
import shutil
from datetime import datetime

class TagCleanupApplier:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.changes_applied = 0
        self.files_modified = set()
        
        # Create backup directory
        self.backup_dir = self.vault_path / f"tag_cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def apply_recommendations(self, recommendations_file: str = None):
        """Apply tag cleanup recommendations"""
        
        # Load recommendations
        if recommendations_file and Path(recommendations_file).exists():
            with open(recommendations_file, 'r', encoding='utf-8') as f:
                recommendations = json.load(f)
        else:
            # Use default recommendations based on common issues
            recommendations = self._generate_default_recommendations()
            
        print(f"=== TAG CLEANUP PROCESS ===")
        print(f"Found {len(recommendations)} recommended changes")
        
        # Group by type for better organization
        by_type = defaultdict(list)
        for rec in recommendations:
            by_type[rec['type']].append(rec)
            
        print("\nChanges by type:")
        for change_type, changes in by_type.items():
            print(f"  {change_type}: {len(changes)} changes")
            
        # Ask for confirmation
        response = input("\nDo you want to:\n  [a] Apply all changes\n  [r] Review each type\n  [c] Cancel\nChoice: ")
        
        if response.lower() == 'c':
            print("Cancelled.")
            return
        elif response.lower() == 'r':
            self._review_and_apply(by_type)
        else:
            self._apply_all(recommendations)
            
    def _generate_default_recommendations(self):
        """Generate recommendations based on the analysis report"""
        recommendations = []
        
        # Load the analysis report
        report_path = self.vault_path / 'tag_analysis_report.json'
        if not report_path.exists():
            print("No analysis report found. Run tag_cleanup_simple.py first.")
            return []
            
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
            
        # 1. Case standardization
        for normalized, variations in report['variations'].items():
            if len(variations) > 1:
                # Find most used version
                usage_list = [(tag, report['tag_usage'][tag]) for tag in variations]
                usage_list.sort(key=lambda x: x[1], reverse=True)
                
                target = usage_list[0][0]
                for tag, usage in usage_list[1:]:
                    recommendations.append({
                        'type': 'case_standardization',
                        'from': tag,
                        'to': target,
                        'reason': f'Standardize to most used version ({usage_list[0][1]} uses)'
                    })
                    
        # 2. Common fixes
        common_fixes = [
            # Plural/singular
            ('#cognitive_architectures', '#cognitive_architecture'),
            ('#language_learning_app', '#language_learning_apps'),
            ('#clinical_application', '#clinical_applications'),
            ('#openNARS_applications', '#openNARS_application'),
            ('#educational_practice', '#educational_practices'),
            ('#experimental_methods', '#experimental_method'),
            ('#confidence_value', '#confidence_values'),
            ('#neural_networks', '#neural_network'),
            ('#truth_value', '#truth_values'),
            
            # Separator standardization
            ('#online_teacher_communities', '#on-line_teacher_communities'),
            ('#sociocultural_perspective', '#socio-cultural_perspective'),
            ('#sociocultural_theory', '#socio-cultural_theory'),
            ('#preservice_teachers', '#pre-service_teachers'),
            ('#meta_regularities', '#metaregularities'),
            
            # Very similar
            ('#massive_open_online_courses', '#massively_open_online_courses'),
            ('#pedagogical_content_knowledge_', '#pedagogical_content_knowledge'),
            ('#social_sciences_', '#social_sciences'),
            ('#personal_learning_networks_', '#personal_learning_networks'),
        ]
        
        for from_tag, to_tag in common_fixes:
            if from_tag in report['tag_usage'] and to_tag in report['tag_usage']:
                # Merge to the more used one
                if report['tag_usage'][to_tag] > report['tag_usage'][from_tag]:
                    recommendations.append({
                        'type': 'merge',
                        'from': from_tag,
                        'to': to_tag,
                        'reason': 'Merge similar tags'
                    })
                else:
                    recommendations.append({
                        'type': 'merge',
                        'from': to_tag,
                        'to': from_tag,
                        'reason': 'Merge similar tags'
                    })
                    
        return recommendations
        
    def _review_and_apply(self, by_type):
        """Review and apply changes by type"""
        for change_type, changes in by_type.items():
            print(f"\n=== {change_type.upper().replace('_', ' ')} ===")
            print(f"Total changes: {len(changes)}")
            
            # Show examples
            print("\nExamples:")
            for change in changes[:5]:
                print(f"  '{change['from']}' -> '{change['to']}'")
                
            if len(changes) > 5:
                print(f"  ... and {len(changes) - 5} more")
                
            response = input("\nApply these changes? [y/n]: ")
            if response.lower() == 'y':
                for change in changes:
                    self._apply_single_change(change)
                    
    def _apply_all(self, recommendations):
        """Apply all recommendations"""
        print("\nApplying all changes...")
        
        for i, change in enumerate(recommendations):
            self._apply_single_change(change)
            
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(recommendations)} changes...")
                
    def _apply_single_change(self, change):
        """Apply a single tag change across all files"""
        from_tag = change['from']
        to_tag = change['to']
        
        # Find all files containing the tag
        for md_file in self.vault_path.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    original_content = content
                    
                # Check if file contains the tag
                if from_tag not in content:
                    continue
                    
                # Backup file if first modification
                if md_file not in self.files_modified:
                    self._backup_file(md_file)
                    self.files_modified.add(md_file)
                    
                # Replace hashtag-style tags
                from_tag_clean = from_tag.replace('#', '')
                to_tag_clean = to_tag.replace('#', '')
                
                # Replace in content (hashtag style)
                content = re.sub(
                    f'#({re.escape(from_tag_clean)})\\b',
                    f'#{to_tag_clean}',
                    content
                )
                
                # Replace in YAML frontmatter
                content = re.sub(
                    f'"{re.escape(from_tag)}"',
                    f'"{to_tag}"',
                    content
                )
                content = re.sub(
                    f"'{re.escape(from_tag)}'",
                    f"'{to_tag}'",
                    content
                )
                
                # Write back if changed
                if content != original_content:
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.changes_applied += 1
                    
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                
    def _backup_file(self, file_path):
        """Create backup of file before modification"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir(parents=True)
            
        relative_path = file_path.relative_to(self.vault_path)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(file_path, backup_path)
        
    def finish(self):
        """Print summary and cleanup"""
        print(f"\n=== CLEANUP COMPLETE ===")
        print(f"Changes applied: {self.changes_applied}")
        print(f"Files modified: {len(self.files_modified)}")
        
        if self.backup_dir.exists():
            print(f"\nBackups saved to: {self.backup_dir}")
            print("You can delete the backup directory once you've verified the changes.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Apply tag cleanup to Obsidian vault')
    parser.add_argument('--path', default='/Users/niklaskarlsson/Obsidian/Book project',
                        help='Path to Obsidian vault')
    parser.add_argument('--recommendations', help='Path to recommendations JSON file')
    args = parser.parse_args()
    
    applier = TagCleanupApplier(args.path)
    applier.apply_recommendations(args.recommendations)
    applier.finish()


if __name__ == '__main__':
    main()