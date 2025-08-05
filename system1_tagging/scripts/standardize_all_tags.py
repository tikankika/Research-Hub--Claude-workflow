#!/usr/bin/env python3
"""
Standardize all tags in Obsidian vault to use underscores
Converts spaces, hyphens, and other separators to underscores
"""

import os
import re
from pathlib import Path
from datetime import datetime
import argparse
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

class TagStandardizer:
    def __init__(self, vault_path: str):
        """Initialize with Obsidian vault path"""
        self.vault_path = Path(vault_path)
        
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault not found at {vault_path}")
        
        # Tags to completely remove (invalid tags)
        self.invalid_tags = {
            '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
            'you', 'i', 'we', 'they', 'it', 'a', 'an', 'the',
            'hfootnote', 'du', 'mathematical'
        }
        
        # Special replacements
        self.special_replacements = {
            'k-12': 'k_12',
            'k12': 'k_12',
            'e-learning': 'online_learning',
            'elearning': 'online_learning',
            'mooc': 'moocs',
            'ai': 'artificial_intelligence',
            'ml': 'machine_learning',
            'dl': 'deep_learning',
            'ict': 'information_communication_technology',
            'hci': 'human_computer_interaction',
            'ux': 'user_experience',
            'ui': 'user_interface',
            'pd': 'professional_development',
            'cpd': 'continuing_professional_development',
            'vr': 'virtual_reality',
            'ar': 'augmented_reality',
            'llm': 'large_language_models',
            'llms': 'large_language_models',
            'genai': 'generative_ai',
            'gen_ai': 'generative_ai',
            'gen-ai': 'generative_ai',
        }
    
    def standardize_tag(self, tag: str) -> str:
        """Convert tag to standardized format with underscores"""
        # Remove # if present
        tag = tag.lstrip('#')
        
        # Convert to lowercase
        tag_lower = tag.lower()
        
        # Check if it's invalid
        if tag_lower in self.invalid_tags:
            return None
        
        # Check for special replacements
        if tag_lower in self.special_replacements:
            return self.special_replacements[tag_lower]
        
        # Replace various separators with underscores
        # Replace spaces, hyphens, dots, and multiple underscores
        standardized = re.sub(r'[\s\-\.]+', '_', tag)
        
        # Remove any non-alphanumeric characters except underscores
        standardized = re.sub(r'[^\w_åäöÅÄÖ]', '', standardized)
        
        # Remove leading/trailing underscores
        standardized = standardized.strip('_')
        
        # Replace multiple underscores with single
        standardized = re.sub(r'_+', '_', standardized)
        
        # Convert to lowercase
        standardized = standardized.lower()
        
        # Skip if too short or just numbers
        if len(standardized) < 3 or standardized.isdigit():
            return None
        
        return standardized
    
    def scan_and_analyze_tags(self) -> Dict:
        """Scan vault and analyze all tags that need standardization"""
        tag_changes = defaultdict(lambda: {'count': 0, 'files': [], 'new_tag': ''})
        tags_to_remove = defaultdict(list)
        
        # Scan all markdown files
        for md_file in self.vault_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all hashtags (but not markdown headers)
                # Look for hashtags that are not at the start of a line
                # or are at the start but don't have a space after the #
                hashtags = []
                
                # Pattern 1: Hashtags not at start of line
                hashtags.extend(re.findall(r'(?<!^)(?<!^\s)#([a-zA-Z0-9_\-]+)', content, re.MULTILINE))
                
                # Pattern 2: Hashtags at start of line but without space (like #tag not # Header)
                for match in re.finditer(r'^#([a-zA-Z0-9_\-]+)', content, re.MULTILINE):
                    hashtags.append(match.group(1))
                
                for tag in hashtags:
                    # Skip author tags (ending with underscore)
                    if tag.endswith('_'):
                        continue
                    
                    standardized = self.standardize_tag(tag)
                    
                    if standardized is None:
                        # Tag should be removed
                        tags_to_remove[tag].append(md_file)
                    elif standardized != tag.lower():
                        # Tag needs changing
                        tag_changes[tag]['count'] += 1
                        tag_changes[tag]['files'].append(md_file)
                        tag_changes[tag]['new_tag'] = standardized
                
                # Also check YAML frontmatter
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end > 0:
                        frontmatter = content[3:yaml_end]
                        if 'tags:' in frontmatter:
                            # Extract YAML tags
                            yaml_tags = re.findall(r'^\s*-\s*(.+)$', frontmatter, re.MULTILINE)
                            for tag in yaml_tags:
                                tag = tag.strip()
                                standardized = self.standardize_tag(tag)
                                
                                if standardized is None:
                                    tags_to_remove[tag].append(md_file)
                                elif standardized != tag.lower():
                                    tag_changes[tag]['count'] += 1
                                    tag_changes[tag]['files'].append(md_file)
                                    tag_changes[tag]['new_tag'] = standardized
                        
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        return {
            'changes': dict(tag_changes),
            'removals': dict(tags_to_remove)
        }
    
    def apply_standardization(self, dry_run: bool = True) -> Dict:
        """Apply tag standardization to all files"""
        analysis = self.scan_and_analyze_tags()
        
        changes_made = 0
        removals_made = 0
        files_modified = set()
        errors = []
        
        # Process changes
        for old_tag, info in analysis['changes'].items():
            new_tag = info['new_tag']
            
            for file_path in info['files']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Replace hashtag occurrences (case-insensitive)
                    # Use word boundaries to avoid partial matches
                    pattern = rf'#{re.escape(old_tag)}\b'
                    content = re.sub(pattern, f'#{new_tag}', content, flags=re.IGNORECASE)
                    
                    # Also handle YAML frontmatter
                    if content.startswith('---'):
                        yaml_end = content.find('---', 3)
                        if yaml_end > 0:
                            frontmatter = content[3:yaml_end]
                            # Replace in YAML tags
                            new_frontmatter = re.sub(
                                rf'^(\s*-\s*){re.escape(old_tag)}$',
                                rf'\1{new_tag}',
                                frontmatter,
                                flags=re.MULTILINE | re.IGNORECASE
                            )
                            if new_frontmatter != frontmatter:
                                content = content[:3] + new_frontmatter + content[yaml_end:]
                    
                    if content != original_content:
                        if not dry_run:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        changes_made += 1
                        files_modified.add(file_path)
                        
                except Exception as e:
                    errors.append({'file': str(file_path), 'tag': old_tag, 'error': str(e)})
        
        # Process removals
        for tag, files in analysis['removals'].items():
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Remove hashtag
                    pattern = rf'#{re.escape(tag)}\b\s*'
                    content = re.sub(pattern, '', content)
                    
                    # Also handle YAML frontmatter
                    if content.startswith('---'):
                        yaml_end = content.find('---', 3)
                        if yaml_end > 0:
                            frontmatter = content[3:yaml_end]
                            # Remove from YAML tags
                            new_frontmatter = re.sub(
                                rf'^\s*-\s*{re.escape(tag)}\s*\n',
                                '',
                                frontmatter,
                                flags=re.MULTILINE
                            )
                            if new_frontmatter != frontmatter:
                                content = content[:3] + new_frontmatter + content[yaml_end:]
                    
                    if content != original_content:
                        if not dry_run:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                        removals_made += 1
                        files_modified.add(file_path)
                        
                except Exception as e:
                    errors.append({'file': str(file_path), 'tag': tag, 'error': str(e)})
        
        return {
            'changes_made': changes_made,
            'removals_made': removals_made,
            'files_modified': len(files_modified),
            'total_changes': len(analysis['changes']),
            'total_removals': len(analysis['removals']),
            'errors': errors,
            'dry_run': dry_run
        }
    
    def generate_report(self, output_path: str = None) -> str:
        """Generate a report of all tags that need standardization"""
        analysis = self.scan_and_analyze_tags()
        
        if not output_path:
            output_path = self.vault_path / 'claude_workspace' / 'export' / f'tag_standardization_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_lines = [
            f"TAG STANDARDIZATION REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            f"SUMMARY",
            f"- Tags needing changes: {len(analysis['changes'])}",
            f"- Tags to remove: {len(analysis['removals'])}",
            f"",
            f"TAGS TO STANDARDIZE",
            f"",
            f"Current Tag | New Tag | Uses | Example Files",
            f"-" * 60
        ]
        
        # Sort by frequency
        sorted_changes = sorted(analysis['changes'].items(), key=lambda x: x[1]['count'], reverse=True)
        
        for old_tag, info in sorted_changes[:100]:  # Top 100
            files_preview = ', '.join([f.name for f in info['files'][:2]])
            if len(info['files']) > 2:
                files_preview += f" +{len(info['files'])-2} more"
            report_lines.append(f"#{old_tag} | #{info['new_tag']} | {info['count']} | {files_preview}")
        
        if len(sorted_changes) > 100:
            report_lines.append(f"... | ... | ... | +{len(sorted_changes)-100} more tags")
        
        report_lines.extend([
            f"",
            f"TAGS TO REMOVE (INVALID)",
            f"",
            f"Tag | Uses | Reason",
            f"-" * 40
        ])
        
        sorted_removals = sorted(analysis['removals'].items(), key=lambda x: len(x[1]), reverse=True)
        
        for tag, files in sorted_removals[:50]:
            if tag.isdigit():
                reason = "Single digit"
            elif len(tag) < 3:
                reason = "Too short"
            elif tag in self.invalid_tags:
                reason = "Invalid/common word"
            else:
                reason = "Invalid format"
            report_lines.append(f"#{tag} | {len(files)} | {reason}")
        
        if len(sorted_removals) > 50:
            report_lines.append(f"... | ... | +{len(sorted_removals)-50} more")
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        return str(output_path)

def main():
    parser = argparse.ArgumentParser(description='Standardize all tags in Obsidian vault to use underscores')
    parser.add_argument('--vault-path', default='.',
                       help='Path to Obsidian vault (default: current directory)')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze tags that need standardization')
    parser.add_argument('--report', action='store_true',
                       help='Generate detailed standardization report')
    parser.add_argument('--apply', action='store_true',
                       help='Apply standardization to all files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes (default for --apply)')
    parser.add_argument('--force', action='store_true',
                       help='Apply changes without dry-run')
    
    args = parser.parse_args()
    
    try:
        standardizer = TagStandardizer(args.vault_path)
        
        if args.analyze:
            analysis = standardizer.scan_and_analyze_tags()
            print(f"\n## Tag Standardization Analysis")
            print(f"Tags needing changes: {len(analysis['changes'])}")
            print(f"Tags to remove: {len(analysis['removals'])}")
            
            print(f"\nTop 10 tags to standardize:")
            sorted_changes = sorted(analysis['changes'].items(), key=lambda x: x[1]['count'], reverse=True)
            for old_tag, info in sorted_changes[:10]:
                print(f"  #{old_tag} → #{info['new_tag']} ({info['count']} uses)")
                
        elif args.report:
            report_path = standardizer.generate_report()
            print(f"Standardization report saved to: {report_path}")
            
        elif args.apply:
            # Default to dry-run unless --force is used
            dry_run = not args.force or args.dry_run
            
            if dry_run:
                print("\n🔍 DRY RUN - No changes will be made")
            else:
                print("\n⚠️  WARNING: This will modify all tags in your vault!")
                print("Proceeding with tag standardization...")
            
            print("\nApplying tag standardization...")
            result = standardizer.apply_standardization(dry_run=dry_run)
            
            print(f"\n{'Would make' if dry_run else 'Made'} the following changes:")
            print(f"- Tag changes: {result['changes_made']} / {result['total_changes']}")
            print(f"- Tag removals: {result['removals_made']} / {result['total_removals']}")
            print(f"- Files modified: {result['files_modified']}")
            
            if result['errors']:
                print(f"\nErrors encountered: {len(result['errors'])}")
                for error in result['errors'][:5]:
                    print(f"  - {error['file']}: {error['error']}")
            
            if dry_run:
                print("\nTo apply these changes, run with --apply --force")
        
        else:
            parser.print_help()
            print("\nExamples:")
            print("  python3 standardize_all_tags.py --analyze")
            print("  python3 standardize_all_tags.py --report")
            print("  python3 standardize_all_tags.py --apply           # Dry run")
            print("  python3 standardize_all_tags.py --apply --force   # Actually apply changes")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())