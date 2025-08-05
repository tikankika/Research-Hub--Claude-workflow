#!/usr/bin/env python3
"""
Tag Cleanup Recommendations Script
==================================
This script provides specific recommendations for cleaning up your Obsidian tags
based on the analysis report.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple

class TagRecommendations:
    def __init__(self, report_path: str):
        with open(report_path, 'r', encoding='utf-8') as f:
            self.report = json.load(f)
            
        self.recommendations = []
        
    def analyze_and_recommend(self):
        """Generate specific recommendations based on the report"""
        
        # 1. Case variations (should be standardized)
        print("=== CASE STANDARDIZATION RECOMMENDATIONS ===\n")
        self._recommend_case_standardization()
        
        # 2. Plural/Singular variations
        print("\n=== PLURAL/SINGULAR STANDARDIZATION ===\n")
        self._recommend_plural_singular()
        
        # 3. Hyphen/Underscore variations
        print("\n=== HYPHEN/UNDERSCORE STANDARDIZATION ===\n")
        self._recommend_separator_standardization()
        
        # 4. Very similar tags
        print("\n=== MERGE SIMILAR TAGS ===\n")
        self._recommend_similar_merges()
        
        # 5. Single-use tags that might be typos
        print("\n=== POTENTIAL TYPOS (Single Use Tags) ===\n")
        self._recommend_typo_fixes()
        
        # 6. Create automated fix script
        self._generate_fix_script()
        
    def _recommend_case_standardization(self):
        """Recommend standardizing tag cases"""
        case_groups = defaultdict(list)
        
        for normalized, variations in self.report['variations'].items():
            # Check if it's just case differences
            lower_set = {v.lower() for v in variations}
            if len(lower_set) == 1:
                case_groups[normalized] = list(variations)
                
        for group, tags in case_groups.items():
            # Recommend the most used version
            tag_usage = [(tag, self.report['tag_usage'][tag]) for tag in tags]
            tag_usage.sort(key=lambda x: x[1], reverse=True)
            
            recommended = tag_usage[0][0]
            others = [t[0] for t in tag_usage[1:]]
            
            print(f"Standardize to '{recommended}' (used {tag_usage[0][1]} times):")
            for other in others:
                usage = self.report['tag_usage'][other]
                print(f"  - Replace '{other}' (used {usage} times)")
                self.recommendations.append({
                    'type': 'case_standardization',
                    'from': other,
                    'to': recommended,
                    'reason': 'case variation'
                })
                
    def _recommend_plural_singular(self):
        """Recommend standardizing plural/singular forms"""
        for tag1, tag2, similarity in self.report['similar_tags']:
            # Check if one is plural of the other
            if (tag1.rstrip('s') == tag2 or tag2.rstrip('s') == tag1) and similarity > 0.9:
                usage1 = self.report['tag_usage'][tag1]
                usage2 = self.report['tag_usage'][tag2]
                
                if usage1 > usage2:
                    print(f"Merge '{tag2}' ({usage2} uses) -> '{tag1}' ({usage1} uses)")
                    self.recommendations.append({
                        'type': 'plural_singular',
                        'from': tag2,
                        'to': tag1,
                        'reason': 'plural/singular variation'
                    })
                else:
                    print(f"Merge '{tag1}' ({usage1} uses) -> '{tag2}' ({usage2} uses)")
                    self.recommendations.append({
                        'type': 'plural_singular',
                        'from': tag1,
                        'to': tag2,
                        'reason': 'plural/singular variation'
                    })
                    
    def _recommend_separator_standardization(self):
        """Recommend standardizing separators (hyphens vs underscores)"""
        for tag1, tag2, similarity in self.report['similar_tags']:
            # Check if they differ only in separators
            norm1 = tag1.replace('-', '_').replace(' ', '_')
            norm2 = tag2.replace('-', '_').replace(' ', '_')
            
            if norm1.lower() == norm2.lower() and tag1 != tag2:
                usage1 = self.report['tag_usage'][tag1]
                usage2 = self.report['tag_usage'][tag2]
                
                if usage1 > usage2:
                    print(f"Standardize '{tag2}' ({usage2} uses) -> '{tag1}' ({usage1} uses)")
                    self.recommendations.append({
                        'type': 'separator',
                        'from': tag2,
                        'to': tag1,
                        'reason': 'separator variation'
                    })
                    
    def _recommend_similar_merges(self):
        """Recommend merging very similar tags"""
        seen_pairs = set()
        
        for tag1, tag2, similarity in self.report['similar_tags'][:30]:
            # Skip if we've already processed this pair
            pair = tuple(sorted([tag1, tag2]))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            
            # Skip if it's just case/separator/plural differences
            if tag1.lower().replace('-', '_') == tag2.lower().replace('-', '_'):
                continue
            if tag1.rstrip('s') == tag2 or tag2.rstrip('s') == tag1:
                continue
                
            if similarity >= 0.95:
                usage1 = self.report['tag_usage'][tag1]
                usage2 = self.report['tag_usage'][tag2]
                
                print(f"Similar tags ({similarity:.0%} match):")
                print(f"  '{tag1}' ({usage1} uses)")
                print(f"  '{tag2}' ({usage2} uses)")
                print(f"  -> Recommend merging to more used tag")
                
    def _recommend_typo_fixes(self):
        """Identify potential typos in single-use tags"""
        single_use = [tag for tag, usage in self.report['tag_usage'].items() if usage == 1]
        
        # Check against common tags
        common_tags = [tag for tag, usage in self.report['tag_usage'].items() if usage > 5]
        
        potential_typos = []
        for single in single_use[:50]:  # Check first 50
            for common in common_tags:
                # Simple edit distance check
                if self._is_likely_typo(single, common):
                    potential_typos.append((single, common))
                    break
                    
        for typo, correct in potential_typos[:20]:
            print(f"'{typo}' might be a typo of '{correct}'")
            
    def _is_likely_typo(self, tag1: str, tag2: str) -> bool:
        """Check if tag1 might be a typo of tag2"""
        # Remove # and normalize
        t1 = tag1.replace('#', '').lower()
        t2 = tag2.replace('#', '').lower()
        
        # Check for single character difference
        if abs(len(t1) - len(t2)) <= 1:
            differences = sum(1 for a, b in zip(t1, t2) if a != b)
            if differences <= 1:
                return True
                
        return False
        
    def _generate_fix_script(self):
        """Generate a script to apply the recommendations"""
        script_path = Path(self.report['tag_usage']).parent / 'apply_tag_fixes.py'
        
        print(f"\n=== GENERATING FIX SCRIPT ===")
        print(f"Total recommendations: {len(self.recommendations)}")
        
        # Save recommendations
        rec_path = Path('tag_cleanup_recommendations.json')
        with open(rec_path, 'w', encoding='utf-8') as f:
            json.dump(self.recommendations, f, indent=2, ensure_ascii=False)
            
        print(f"Recommendations saved to: {rec_path}")
        
        # Group by type
        by_type = defaultdict(list)
        for rec in self.recommendations:
            by_type[rec['type']].append(rec)
            
        print("\nSummary by type:")
        for type_name, recs in by_type.items():
            print(f"  {type_name}: {len(recs)} changes")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate tag cleanup recommendations')
    parser.add_argument('--report', default='tag_analysis_report.json',
                        help='Path to analysis report')
    args = parser.parse_args()
    
    recommender = TagRecommendations(args.report)
    recommender.analyze_and_recommend()


if __name__ == '__main__':
    main()