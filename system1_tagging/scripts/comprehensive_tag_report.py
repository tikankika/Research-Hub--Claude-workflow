#!/usr/bin/env python3
"""
Comprehensive Tag Report Generator
Generates detailed tag analysis reports with file associations
Similar to the old tag_report format but with enhanced features

Author: Claude Code Assistant
Date: 2025-08-04
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
import argparse

class ComprehensiveTagReporter:
    def __init__(self, vault_path: str, focus_folder: str = None):
        self.vault_path = Path(vault_path)
        self.focus_folder = focus_folder
        self.export_path = self.vault_path / "claude_workspace" / "system1_tagging" / "export" / "current"
        self.export_path.mkdir(parents=True, exist_ok=True)
        
    def scan_vault_tags(self) -> Dict[str, List[str]]:
        """Scan vault for all tags and their file associations"""
        tag_locations = defaultdict(list)
        
        # Determine search path
        if self.focus_folder:
            search_path = self.vault_path / self.focus_folder
        else:
            search_path = self.vault_path
            
        # Scan all markdown files
        for md_file in search_path.rglob("*.md"):
            # Skip certain folders
            if any(skip in str(md_file) for skip in ['.obsidian', 'claude_workspace', 'archive']):
                continue
                
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract tags from content
                tags = self._extract_all_tags(content)
                
                # Record file for each tag
                relative_path = md_file.relative_to(self.vault_path)
                for tag in tags:
                    tag_locations[tag].append(str(relative_path))
                    
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
                
        return dict(tag_locations)
    
    def _extract_all_tags(self, content: str) -> Set[str]:
        """Extract all tags from file content"""
        tags = set()
        
        # Extract YAML frontmatter tags
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            # Look for tags in YAML
            tags_match = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n)*)', yaml_content, re.MULTILINE)
            if tags_match:
                yaml_tags = re.findall(r'-\s*([^#\n]+)', tags_match.group(1))
                tags.update(tag.strip().strip('"\'') for tag in yaml_tags if tag.strip())
            # Also check for inline format
            inline_match = re.search(r'^tags:\s*\[(.*?)\]', yaml_content, re.MULTILINE)
            if inline_match:
                inline_tags = [t.strip().strip('"\'') for t in inline_match.group(1).split(',')]
                tags.update(t for t in inline_tags if t)
        
        # Extract hashtag tags
        hashtag_tags = re.findall(r'#([a-zA-Z0-9_åäöÅÄÖ-]+)', content)
        tags.update(hashtag_tags)
        
        return tags
    
    def analyze_tags(self, tag_locations: Dict[str, List[str]]) -> Dict:
        """Comprehensive tag analysis"""
        total_uses = sum(len(files) for files in tag_locations.values())
        
        # Calculate distribution
        distribution = {
            'single_use': 0,
            'rare_use': 0,      # 2-5 uses
            'moderate_use': 0,  # 6-20 uses
            'common_use': 0     # >20 uses
        }
        
        for tag, files in tag_locations.items():
            count = len(files)
            if count == 1:
                distribution['single_use'] += 1
            elif 2 <= count <= 5:
                distribution['rare_use'] += 1
            elif 6 <= count <= 20:
                distribution['moderate_use'] += 1
            else:
                distribution['common_use'] += 1
        
        # Find most common tags
        tag_counts = {tag: len(files) for tag, files in tag_locations.items()}
        most_common = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'total_unique_tags': len(tag_locations),
            'total_tag_uses': total_uses,
            'avg_uses_per_tag': round(total_uses / len(tag_locations), 1) if tag_locations else 0,
            'distribution': distribution,
            'most_common': most_common[:100]  # Top 100
        }
    
    def find_potential_duplicates(self, tag_locations: Dict[str, List[str]]) -> List[Tuple[str, str, float]]:
        """Find potential duplicate tags using similarity metrics"""
        duplicates = []
        tags = list(tag_locations.keys())
        
        # Simple similarity check
        for i, tag1 in enumerate(tags):
            for tag2 in tags[i+1:]:
                # Calculate similarity
                similarity = self._calculate_similarity(tag1, tag2)
                if similarity > 90:  # 90% threshold
                    duplicates.append((tag1, tag2, similarity))
        
        # Sort by similarity
        duplicates.sort(key=lambda x: x[2], reverse=True)
        return duplicates[:20]  # Top 20 potential duplicates
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity percentage"""
        # Simple Levenshtein-based similarity
        if s1 == s2:
            return 100.0
            
        # Normalize strings
        s1_norm = s1.lower().replace('_', '').replace('-', '')
        s2_norm = s2.lower().replace('_', '').replace('-', '')
        
        if s1_norm == s2_norm:
            return 98.0
            
        # Check for subset
        if s1 in s2 or s2 in s1:
            return 95.0
            
        # Simple character overlap
        common = len(set(s1_norm) & set(s2_norm))
        total = len(set(s1_norm) | set(s2_norm))
        
        if total == 0:
            return 0.0
            
        return (common / total) * 100
    
    def generate_standardization_suggestions(self, tag_locations: Dict[str, List[str]]) -> List[Dict]:
        """Generate tag standardization suggestions"""
        suggestions = []
        
        # Common standardizations
        patterns = [
            (r'^ict$', 'information_communication_technology'),
            (r'^llm$', 'large_language_models'),
            (r'^k_12$', 'k-12'),
            (r'^meta_analysis$', 'meta-analysis'),
            (r'^ai$', 'artificial_intelligence'),
            (r'^ml$', 'machine_learning'),
            (r'^dl$', 'deep_learning'),
            (r'^nlp$', 'natural_language_processing')
        ]
        
        for tag, files in tag_locations.items():
            for pattern, replacement in patterns:
                if re.match(pattern, tag, re.IGNORECASE):
                    suggestions.append({
                        'current': tag,
                        'suggested': replacement,
                        'uses': len(files)
                    })
                    break
        
        return suggestions
    
    def generate_report(self, tag_locations: Dict[str, List[str]], 
                       analysis: Dict, 
                       duplicates: List, 
                       suggestions: List) -> str:
        """Generate comprehensive report in old format"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = []
        report.append("OBSIDIAN VAULT TAG ANALYSIS REPORT")
        report.append(f"Generated: {timestamp}")
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append(f"- Total unique tags: {analysis['total_unique_tags']}")
        report.append(f"- Total tag uses: {analysis['total_tag_uses']}")
        report.append(f"- Average uses per tag: {analysis['avg_uses_per_tag']}")
        report.append("")
        
        # Distribution
        report.append("TAG DISTRIBUTION")
        report.append(f"- Single use tags: {analysis['distribution']['single_use']}")
        report.append(f"- Rare use (2-5): {analysis['distribution']['rare_use']}")
        report.append(f"- Moderate use (6-20): {analysis['distribution']['moderate_use']}")
        report.append(f"- Common use (>20): {analysis['distribution']['common_use']}")
        report.append("")
        
        # Most common tags
        report.append("MOST COMMON TAGS")
        for tag, count in analysis['most_common'][:20]:
            report.append(f"- #{tag}: {count} uses")
        report.append("")
        
        # Potential duplicates
        if duplicates:
            report.append("POTENTIAL DUPLICATES")
            for tag1, tag2, similarity in duplicates:
                report.append(f"- '{tag1}' <-> '{tag2}' (similarity: {similarity:.2f}%)")
            report.append("")
        
        # Standardization suggestions
        if suggestions:
            report.append("STANDARDIZATION SUGGESTIONS")
            for sugg in suggestions:
                report.append(f"- Change '#{sugg['current']}' -> '#{sugg['suggested']}' ({sugg['uses']} uses)")
            report.append("")
        
        # Complete tag list with file associations (top 100)
        report.append("COMPLETE TAG LIST (TOP 100)")
        report.append("")
        report.append("Tag | Uses | Files")
        report.append("-" * 60)
        
        for tag, count in analysis['most_common'][:100]:
            files = tag_locations[tag]
            # Show first 3 files
            file_list = ", ".join(files[:3])
            if len(files) > 3:
                file_list += f" +{len(files)-3} more"
            report.append(f"#{tag} | {count} | {file_list}")
        
        return "\n".join(report)
    
    def generate_json_export(self, tag_locations: Dict[str, List[str]], 
                            analysis: Dict) -> Dict:
        """Generate detailed JSON export"""
        return {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'vault_path': str(self.vault_path),
                'focus_folder': self.focus_folder,
                'total_tags': analysis['total_unique_tags'],
                'total_uses': analysis['total_tag_uses']
            },
            'summary': {
                'avg_uses_per_tag': analysis['avg_uses_per_tag'],
                'distribution': analysis['distribution']
            },
            'tag_details': {
                tag: {
                    'count': len(files),
                    'files': files
                } for tag, files in tag_locations.items()
            }
        }
    
    def run(self, output_format='both'):
        """Run comprehensive tag analysis"""
        print("Scanning vault for tags...")
        tag_locations = self.scan_vault_tags()
        
        if not tag_locations:
            print("No tags found!")
            return
            
        print(f"Found {len(tag_locations)} unique tags")
        
        # Analyze tags
        print("Analyzing tag usage...")
        analysis = self.analyze_tags(tag_locations)
        
        # Find duplicates
        print("Finding potential duplicates...")
        duplicates = self.find_potential_duplicates(tag_locations)
        
        # Generate suggestions
        print("Generating standardization suggestions...")
        suggestions = self.generate_standardization_suggestions(tag_locations)
        
        # Generate reports
        if output_format in ['text', 'both']:
            print("Generating text report...")
            text_report = self.generate_report(tag_locations, analysis, duplicates, suggestions)
            
            # Save text report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            text_path = self.export_path / f"comprehensive_tag_report_{timestamp}.txt"
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text_report)
            print(f"✓ Text report saved: {text_path.name}")
        
        if output_format in ['json', 'both']:
            print("Generating JSON export...")
            json_data = self.generate_json_export(tag_locations, analysis)
            
            # Save JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = self.export_path / f"comprehensive_tag_data_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            print(f"✓ JSON export saved: {json_path.name}")
        
        # Print summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print(f"Total unique tags: {analysis['total_unique_tags']}")
        print(f"Total tag uses: {analysis['total_tag_uses']}")
        print(f"Average uses per tag: {analysis['avg_uses_per_tag']}")
        print(f"Potential duplicates found: {len(duplicates)}")
        print(f"Standardization suggestions: {len(suggestions)}")


def main():
    parser = argparse.ArgumentParser(description='Generate comprehensive tag report')
    parser.add_argument('--vault-path', type=str, default='.',
                       help='Path to Obsidian vault (default: current directory)')
    parser.add_argument('--focus-folder', type=str,
                       help='Focus on specific folder (e.g., "4 Articles")')
    parser.add_argument('--format', choices=['text', 'json', 'both'], default='both',
                       help='Output format (default: both)')
    
    args = parser.parse_args()
    
    # Create reporter and run
    reporter = ComprehensiveTagReporter(args.vault_path, args.focus_folder)
    reporter.run(args.format)


if __name__ == "__main__":
    main()