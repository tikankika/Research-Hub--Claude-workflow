#!/usr/bin/env python3
"""
Obsidian Tag Cleanup Tool
========================
This tool helps you clean up and organize tags in your Obsidian book project.
It identifies duplicate tags, similar tags, and provides interactive cleanup options.
"""

import os
import re
import json
from collections import defaultdict, Counter
from difflib import SequenceMatcher
from pathlib import Path
import argparse
from typing import List, Dict, Set, Tuple
import colorama
from colorama import Fore, Style, Back

colorama.init()

class TagAnalyzer:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tags = defaultdict(list)  # tag -> list of (file, line_number)
        self.tag_variations = defaultdict(set)  # normalized_tag -> set of variations
        self.file_tags = defaultdict(set)  # file -> set of tags
        
    def scan_vault(self):
        """Scan all markdown files for tags"""
        print(f"{Fore.CYAN}Scanning vault for tags...{Style.RESET_ALL}")
        
        for md_file in self.vault_path.rglob("*.md"):
            self._scan_file(md_file)
            
        print(f"{Fore.GREEN}Found {len(self.tags)} unique tags across {len(self.file_tags)} files{Style.RESET_ALL}")
        
    def _scan_file(self, file_path: Path):
        """Scan a single file for tags"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find hashtag-style tags
            hashtag_pattern = r'#([a-zA-Z0-9_\-åäöÅÄÖ/]+)'
            for match in re.finditer(hashtag_pattern, content):
                tag = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                self.tags[f"#{tag}"].append((str(file_path), line_num))
                self.file_tags[str(file_path)].add(f"#{tag}")
                
                # Store normalized version
                normalized = self._normalize_tag(tag)
                self.tag_variations[normalized].add(f"#{tag}")
                
            # Find YAML frontmatter tags
            yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                tag_line_match = re.search(r'^tags:\s*\[(.*?)\]', yaml_content, re.MULTILINE)
                if tag_line_match:
                    tags_str = tag_line_match.group(1)
                    tags = [t.strip() for t in tags_str.split(',')]
                    for tag in tags:
                        clean_tag = tag.strip('"').strip("'")
                        if clean_tag:
                            self.tags[clean_tag].append((str(file_path), 0))
                            self.file_tags[str(file_path)].add(clean_tag)
                            
                            normalized = self._normalize_tag(clean_tag)
                            self.tag_variations[normalized].add(clean_tag)
                            
        except Exception as e:
            print(f"{Fore.RED}Error reading {file_path}: {e}{Style.RESET_ALL}")
            
    def _normalize_tag(self, tag: str) -> str:
        """Normalize tag for comparison"""
        # Remove # if present, lowercase, replace spaces/dashes with underscore
        normalized = tag.lower()
        normalized = normalized.replace('#', '')
        normalized = normalized.replace('-', '_')
        normalized = normalized.replace(' ', '_')
        return normalized
        
    def find_similar_tags(self, threshold: float = 0.8) -> List[Tuple[str, str, float]]:
        """Find similar tags based on string similarity"""
        similar_pairs = []
        tag_list = list(self.tags.keys())
        
        for i in range(len(tag_list)):
            for j in range(i + 1, len(tag_list)):
                tag1, tag2 = tag_list[i], tag_list[j]
                
                # Skip if they're already variations of the same tag
                norm1 = self._normalize_tag(tag1)
                norm2 = self._normalize_tag(tag2)
                if norm1 == norm2:
                    continue
                    
                similarity = SequenceMatcher(None, tag1.lower(), tag2.lower()).ratio()
                if similarity >= threshold:
                    similar_pairs.append((tag1, tag2, similarity))
                    
        return sorted(similar_pairs, key=lambda x: x[2], reverse=True)
        
    def find_tag_variations(self) -> Dict[str, Set[str]]:
        """Find tags that are variations of each other"""
        variations = {}
        for normalized, tags in self.tag_variations.items():
            if len(tags) > 1:
                variations[normalized] = tags
        return variations
        
    def find_unused_tags(self, min_usage: int = 1) -> List[Tuple[str, int]]:
        """Find tags that are rarely used"""
        unused = []
        for tag, locations in self.tags.items():
            if len(locations) <= min_usage:
                unused.append((tag, len(locations)))
        return sorted(unused, key=lambda x: x[1])
        
    def generate_report(self) -> Dict:
        """Generate a comprehensive tag analysis report"""
        report = {
            'total_tags': len(self.tags),
            'total_files': len(self.file_tags),
            'tag_usage': {tag: len(locs) for tag, locs in self.tags.items()},
            'variations': self.find_tag_variations(),
            'similar_tags': self.find_similar_tags(),
            'unused_tags': self.find_unused_tags(),
            'most_used': Counter({tag: len(locs) for tag, locs in self.tags.items()}).most_common(20)
        }
        return report


class TagCleaner:
    def __init__(self, analyzer: TagAnalyzer):
        self.analyzer = analyzer
        self.changes = []  # Track all changes for review
        
    def interactive_cleanup(self):
        """Interactive cleanup process"""
        print(f"\n{Fore.YELLOW}=== Interactive Tag Cleanup ==={Style.RESET_ALL}\n")
        
        # 1. Handle tag variations
        self._handle_variations()
        
        # 2. Handle similar tags
        self._handle_similar_tags()
        
        # 3. Handle unused tags
        self._handle_unused_tags()
        
        # 4. Review and apply changes
        self._review_changes()
        
    def _handle_variations(self):
        """Handle tags that are variations of each other"""
        variations = self.analyzer.find_tag_variations()
        
        if not variations:
            print(f"{Fore.GREEN}No tag variations found!{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}Found {len(variations)} groups of tag variations:{Style.RESET_ALL}")
        
        for normalized, tags in variations.items():
            print(f"\n{Fore.YELLOW}Variations of '{normalized}':{Style.RESET_ALL}")
            tag_list = list(tags)
            
            for i, tag in enumerate(tag_list):
                count = len(self.analyzer.tags[tag])
                print(f"  {i+1}. {tag} (used {count} times)")
                
            print("\nOptions:")
            print("  [1-9] Merge all to this tag")
            print("  [s]   Skip this group")
            print("  [c]   Create custom tag for all")
            
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == 's':
                continue
            elif choice == 'c':
                new_tag = input("Enter new tag name (with #): ").strip()
                if new_tag:
                    for tag in tag_list:
                        if tag != new_tag:
                            self._add_change('merge', tag, new_tag)
            elif choice.isdigit() and 1 <= int(choice) <= len(tag_list):
                target_tag = tag_list[int(choice) - 1]
                for tag in tag_list:
                    if tag != target_tag:
                        self._add_change('merge', tag, target_tag)
                        
    def _handle_similar_tags(self):
        """Handle similar tags"""
        similar = self.analyzer.find_similar_tags(threshold=0.7)
        
        if not similar:
            print(f"\n{Fore.GREEN}No similar tags found!{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}Found {len(similar)} pairs of similar tags:{Style.RESET_ALL}")
        
        for tag1, tag2, similarity in similar[:20]:  # Show top 20
            count1 = len(self.analyzer.tags[tag1])
            count2 = len(self.analyzer.tags[tag2])
            
            print(f"\n{Fore.YELLOW}Similar tags (similarity: {similarity:.0%}):{Style.RESET_ALL}")
            print(f"  1. {tag1} (used {count1} times)")
            print(f"  2. {tag2} (used {count2} times)")
            
            print("\nOptions:")
            print("  [1] Merge to first tag")
            print("  [2] Merge to second tag")
            print("  [c] Create custom tag for both")
            print("  [s] Skip")
            
            choice = input("\nYour choice: ").strip().lower()
            
            if choice == '1':
                self._add_change('merge', tag2, tag1)
            elif choice == '2':
                self._add_change('merge', tag1, tag2)
            elif choice == 'c':
                new_tag = input("Enter new tag name (with #): ").strip()
                if new_tag:
                    self._add_change('merge', tag1, new_tag)
                    self._add_change('merge', tag2, new_tag)
                    
    def _handle_unused_tags(self):
        """Handle rarely used tags"""
        unused = self.analyzer.find_unused_tags(min_usage=2)
        
        if not unused:
            print(f"\n{Fore.GREEN}No rarely used tags found!{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}Found {len(unused)} rarely used tags:{Style.RESET_ALL}")
        
        # Group display
        print("\nTags used only once:")
        single_use = [tag for tag, count in unused if count == 1]
        for i in range(0, len(single_use), 5):
            print("  " + ", ".join(single_use[i:i+5]))
            
        print("\nOptions:")
        print("  [d] Delete all single-use tags")
        print("  [r] Review each tag individually")
        print("  [s] Skip")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'd':
            for tag, count in unused:
                if count == 1:
                    self._add_change('delete', tag, None)
        elif choice == 'r':
            for tag, count in unused[:20]:  # Review first 20
                locations = self.analyzer.tags[tag]
                print(f"\n{Fore.YELLOW}Tag: {tag} (used {count} times){Style.RESET_ALL}")
                for file, line in locations[:3]:
                    print(f"  {file}:{line}")
                    
                action = input("  [d]elete, [k]eep, [m]erge with another tag: ").strip().lower()
                
                if action == 'd':
                    self._add_change('delete', tag, None)
                elif action == 'm':
                    target = input("  Merge with tag: ").strip()
                    if target:
                        self._add_change('merge', tag, target)
                        
    def _add_change(self, change_type: str, old_tag: str, new_tag: str):
        """Add a change to the pending changes list"""
        self.changes.append({
            'type': change_type,
            'old': old_tag,
            'new': new_tag,
            'locations': self.analyzer.tags[old_tag]
        })
        
    def _review_changes(self):
        """Review and apply changes"""
        if not self.changes:
            print(f"\n{Fore.GREEN}No changes to apply!{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}=== Review Changes ==={Style.RESET_ALL}")
        print(f"Total changes: {len(self.changes)}")
        
        # Group changes by type
        merges = [c for c in self.changes if c['type'] == 'merge']
        deletes = [c for c in self.changes if c['type'] == 'delete']
        
        if merges:
            print(f"\n{Fore.YELLOW}Tag Merges:{Style.RESET_ALL}")
            for change in merges[:10]:  # Show first 10
                print(f"  {change['old']} → {change['new']} ({len(change['locations'])} occurrences)")
                
        if deletes:
            print(f"\n{Fore.YELLOW}Tag Deletions:{Style.RESET_ALL}")
            for change in deletes[:10]:  # Show first 10
                print(f"  {change['old']} ({len(change['locations'])} occurrences)")
                
        print("\nOptions:")
        print("  [a] Apply all changes")
        print("  [s] Save changes to file for review")
        print("  [c] Cancel all changes")
        
        choice = input("\nYour choice: ").strip().lower()
        
        if choice == 'a':
            self._apply_changes()
        elif choice == 's':
            self._save_changes_to_file()
        else:
            print(f"{Fore.YELLOW}Changes cancelled.{Style.RESET_ALL}")
            
    def _apply_changes(self):
        """Apply all pending changes"""
        print(f"\n{Fore.CYAN}Applying changes...{Style.RESET_ALL}")
        
        # Group changes by file
        file_changes = defaultdict(list)
        for change in self.changes:
            for file_path, line_num in change['locations']:
                file_changes[file_path].append(change)
                
        # Apply changes file by file
        for file_path, changes in file_changes.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Apply changes
                for change in changes:
                    if change['type'] == 'merge':
                        # Replace old tag with new tag
                        old_tag = change['old'].replace('#', '')
                        new_tag = change['new'].replace('#', '')
                        
                        # Replace in content
                        content = re.sub(
                            f'#({re.escape(old_tag)})\\b',
                            f'#{new_tag}',
                            content
                        )
                        
                        # Also handle YAML frontmatter
                        content = re.sub(
                            f'"{re.escape(change["old"])}"',
                            f'"{change["new"]}"',
                            content
                        )
                        
                    elif change['type'] == 'delete':
                        # Remove tag
                        old_tag = change['old'].replace('#', '')
                        content = re.sub(f'#({re.escape(old_tag)})\\s*', '', content)
                        
                        # Also handle YAML frontmatter
                        content = re.sub(f'"{re.escape(change["old"])}"\\s*,?\\s*', '', content)
                        
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"{Fore.GREEN}✓ Updated {file_path}{Style.RESET_ALL}")
                
            except Exception as e:
                print(f"{Fore.RED}✗ Error updating {file_path}: {e}{Style.RESET_ALL}")
                
        print(f"\n{Fore.GREEN}Changes applied successfully!{Style.RESET_ALL}")
        
    def _save_changes_to_file(self):
        """Save changes to a JSON file for review"""
        output_file = self.analyzer.vault_path / 'tag_cleanup_changes.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.changes, f, indent=2, ensure_ascii=False)
            
        print(f"{Fore.GREEN}Changes saved to {output_file}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description='Clean up Obsidian tags')
    parser.add_argument('--path', default='/Users/niklaskarlsson/Obsidian/Book project',
                        help='Path to Obsidian vault')
    parser.add_argument('--report-only', action='store_true',
                        help='Only generate report without cleanup')
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = TagAnalyzer(args.path)
    analyzer.scan_vault()
    
    # Generate report
    report = analyzer.generate_report()
    
    print(f"\n{Fore.CYAN}=== Tag Analysis Report ==={Style.RESET_ALL}")
    print(f"Total unique tags: {report['total_tags']}")
    print(f"Total files with tags: {report['total_files']}")
    
    print(f"\n{Fore.YELLOW}Most used tags:{Style.RESET_ALL}")
    for tag, count in report['most_used'][:10]:
        print(f"  {tag}: {count} uses")
        
    print(f"\n{Fore.YELLOW}Tag variations found: {len(report['variations'])}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Similar tag pairs found: {len(report['similar_tags'])}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Rarely used tags: {len(report['unused_tags'])}{Style.RESET_ALL}")
    
    # Save full report
    report_file = Path(args.path) / 'tag_analysis_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n{Fore.GREEN}Full report saved to {report_file}{Style.RESET_ALL}")
    
    # Interactive cleanup
    if not args.report_only:
        proceed = input(f"\n{Fore.CYAN}Proceed with interactive cleanup? [y/n]: {Style.RESET_ALL}").strip().lower()
        if proceed == 'y':
            cleaner = TagCleaner(analyzer)
            cleaner.interactive_cleanup()


if __name__ == '__main__':
    main()