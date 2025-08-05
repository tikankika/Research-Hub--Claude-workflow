#!/usr/bin/env python3
"""
Obsidian Tag Cleanup Tool (Simple Version)
=========================================
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

class TagAnalyzer:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.tags = defaultdict(list)  # tag -> list of (file, line_number)
        self.tag_variations = defaultdict(set)  # normalized_tag -> set of variations
        self.file_tags = defaultdict(set)  # file -> set of tags
        
    def scan_vault(self):
        """Scan all markdown files for tags"""
        print("Scanning vault for tags...")
        
        for md_file in self.vault_path.rglob("*.md"):
            self._scan_file(md_file)
            
        print(f"Found {len(self.tags)} unique tags across {len(self.file_tags)} files")
        
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
            print(f"Error reading {file_path}: {e}")
            
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
        # Convert sets to lists for JSON serialization
        variations_dict = {}
        for k, v in self.find_tag_variations().items():
            variations_dict[k] = list(v)
            
        report = {
            'total_tags': len(self.tags),
            'total_files': len(self.file_tags),
            'tag_usage': {tag: len(locs) for tag, locs in self.tags.items()},
            'variations': variations_dict,
            'similar_tags': self.find_similar_tags(),
            'unused_tags': self.find_unused_tags(),
            'most_used': Counter({tag: len(locs) for tag, locs in self.tags.items()}).most_common(20)
        }
        return report


def main():
    parser = argparse.ArgumentParser(description='Clean up Obsidian tags')
    parser.add_argument('--path', default='/Users/niklaskarlsson/Obsidian/Book project',
                        help='Path to Obsidian vault')
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = TagAnalyzer(args.path)
    analyzer.scan_vault()
    
    # Generate report
    report = analyzer.generate_report()
    
    print("\n=== Tag Analysis Report ===")
    print(f"Total unique tags: {report['total_tags']}")
    print(f"Total files with tags: {report['total_files']}")
    
    print("\nMost used tags:")
    for tag, count in report['most_used'][:10]:
        print(f"  {tag}: {count} uses")
        
    print(f"\nTag variations found: {len(report['variations'])}")
    print(f"Similar tag pairs found: {len(report['similar_tags'])}")
    print(f"Rarely used tags: {len(report['unused_tags'])}")
    
    # Save full report
    report_file = Path(args.path) / 'tag_analysis_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nFull report saved to {report_file}")
    
    # Show some examples
    if report['variations']:
        print("\nExample tag variations:")
        for normalized, tags in list(report['variations'].items())[:5]:
            print(f"  '{normalized}': {list(tags)}")
            
    if report['similar_tags']:
        print("\nExample similar tags:")
        for tag1, tag2, similarity in report['similar_tags'][:5]:
            print(f"  '{tag1}' <-> '{tag2}' (similarity: {similarity:.0%})")


if __name__ == '__main__':
    main()