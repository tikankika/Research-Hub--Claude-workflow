#!/usr/bin/env python3
"""
Obsidian Tag Manager
Manages, deduplicates, and standardizes tags across the vault
"""

import os
import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import argparse
from typing import List, Dict, Set, Tuple
from difflib import SequenceMatcher

class ObsidianTagManager:
    def __init__(self, vault_path: str):
        """Initialize with Obsidian vault path"""
        self.vault_path = Path(vault_path)
        
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault not found at {vault_path}")
        
        # Tag similarity threshold for deduplication
        self.similarity_threshold = 0.85
        
        # Common tag variations to standardize
        self.tag_mappings = {
            # Educational levels
            'higher_ed': 'higher_education',
            'higher-education': 'higher_education',
            'university': 'higher_education',
            'k12': 'k-12',
            'k_12': 'k-12',
            
            # AI/ML variations
            'ai': 'artificial_intelligence',
            'ml': 'machine_learning',
            'dl': 'deep_learning',
            'llm': 'large_language_models',
            'llms': 'large_language_models',
            'genai': 'generative_ai',
            'gen_ai': 'generative_ai',
            
            # Learning variations
            'e-learning': 'online_learning',
            'elearning': 'online_learning',
            'distance_learning': 'online_learning',
            'mooc': 'moocs',
            'massive_open_online_courses': 'moocs',
            
            # Research methods
            'lit_review': 'literature_review',
            'systematic_literature_review': 'systematic_review',
            'meta_analysis': 'meta-analysis',
            'case-study': 'case_study',
            
            # Other common variations
            'ict': 'information_communication_technology',
            'hci': 'human_computer_interaction',
            'ux': 'user_experience',
            'ui': 'user_interface',
            'pd': 'professional_development',
            'cpd': 'continuing_professional_development',
        }
    
    def scan_vault_tags(self) -> Dict[str, List[Path]]:
        """Scan entire vault and collect all tags with their locations"""
        tag_locations = defaultdict(list)
        
        # Scan all markdown files
        for md_file in self.vault_path.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all hashtags
                hashtags = re.findall(r'#([\w_-]+)', content)
                
                # Also check YAML frontmatter
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end > 0:
                        frontmatter = content[3:yaml_end]
                        if 'tags:' in frontmatter:
                            # Extract YAML tags
                            yaml_tags = re.findall(r'^\s*-\s*(.+)$', frontmatter, re.MULTILINE)
                            hashtags.extend(yaml_tags)
                
                # Record tag locations
                for tag in hashtags:
                    tag = tag.strip().lower()
                    if tag and not tag.endswith('_'):  # Exclude author tags
                        tag_locations[tag].append(md_file)
                        
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        return dict(tag_locations)
    
    def analyze_tags(self) -> Dict:
        """Analyze all tags in vault"""
        tag_locations = self.scan_vault_tags()
        
        # Calculate tag statistics
        tag_counts = {tag: len(files) for tag, files in tag_locations.items()}
        
        # Sort by frequency
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        analysis = {
            'total_unique_tags': len(tag_locations),
            'total_tag_uses': sum(tag_counts.values()),
            'most_common': sorted_tags[:20],
            'least_common': sorted_tags[-20:],
            'tag_distribution': self._calculate_distribution(tag_counts),
            'potential_duplicates': self._find_similar_tags(list(tag_locations.keys())),
            'standardization_suggestions': self._suggest_standardizations(tag_locations)
        }
        
        return analysis
    
    def _calculate_distribution(self, tag_counts: Dict[str, int]) -> Dict:
        """Calculate tag distribution statistics"""
        counts = list(tag_counts.values())
        
        return {
            'single_use': len([c for c in counts if c == 1]),
            'rare_use': len([c for c in counts if 2 <= c <= 5]),
            'moderate_use': len([c for c in counts if 6 <= c <= 20]),
            'common_use': len([c for c in counts if c > 20])
        }
    
    def _find_similar_tags(self, tags: List[str]) -> List[Tuple[str, str, float]]:
        """Find potentially duplicate tags based on similarity"""
        similar_pairs = []
        
        for i, tag1 in enumerate(tags):
            for tag2 in tags[i+1:]:
                # Skip if one is clearly a subset
                if tag1 in tag2 or tag2 in tag1:
                    continue
                
                # Calculate similarity
                similarity = SequenceMatcher(None, tag1, tag2).ratio()
                
                if similarity > self.similarity_threshold:
                    similar_pairs.append((tag1, tag2, similarity))
        
        # Sort by similarity
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        return similar_pairs[:20]  # Return top 20
    
    def _suggest_standardizations(self, tag_locations: Dict[str, List[Path]]) -> List[Dict]:
        """Suggest tag standardizations based on mappings"""
        suggestions = []
        
        for tag in tag_locations:
            if tag.lower() in self.tag_mappings:
                standard_tag = self.tag_mappings[tag.lower()]
                if standard_tag in tag_locations:
                    # Both exist, suggest merge
                    suggestions.append({
                        'current': tag,
                        'suggested': standard_tag,
                        'reason': 'variant_exists',
                        'current_uses': len(tag_locations[tag]),
                        'standard_uses': len(tag_locations[standard_tag])
                    })
                else:
                    # Only variant exists, suggest rename
                    suggestions.append({
                        'current': tag,
                        'suggested': standard_tag,
                        'reason': 'standardization',
                        'current_uses': len(tag_locations[tag])
                    })
        
        return suggestions
    
    def merge_tags(self, old_tag: str, new_tag: str, dry_run: bool = True) -> Dict:
        """Merge one tag into another across all files"""
        tag_locations = self.scan_vault_tags()
        
        if old_tag not in tag_locations:
            return {'error': f"Tag '{old_tag}' not found in vault"}
        
        files_to_update = tag_locations[old_tag]
        updated_files = []
        errors = []
        
        for file_path in files_to_update:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace hashtag occurrences
                old_pattern = f'#{old_tag}\\b'
                new_hashtag = f'#{new_tag}'
                
                updated_content = re.sub(old_pattern, new_hashtag, content, flags=re.IGNORECASE)
                
                # Also check YAML frontmatter
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end > 0:
                        frontmatter = content[3:yaml_end]
                        if old_tag in frontmatter:
                            new_frontmatter = frontmatter.replace(f'- {old_tag}', f'- {new_tag}')
                            updated_content = content[:3] + new_frontmatter + content[yaml_end:]
                
                if not dry_run and updated_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                
                if updated_content != content:
                    updated_files.append(file_path)
                    
            except Exception as e:
                errors.append({'file': str(file_path), 'error': str(e)})
        
        return {
            'old_tag': old_tag,
            'new_tag': new_tag,
            'files_affected': len(updated_files),
            'files_list': [str(f.relative_to(self.vault_path)) for f in updated_files],
            'errors': errors,
            'dry_run': dry_run
        }
    
    def clean_tags(self, remove_single_use: bool = False, dry_run: bool = True) -> Dict:
        """Clean up tags based on various criteria"""
        tag_locations = self.scan_vault_tags()
        
        tags_to_remove = []
        
        # Find single-use tags
        if remove_single_use:
            single_use = [tag for tag, files in tag_locations.items() if len(files) == 1]
            tags_to_remove.extend(single_use)
        
        # Remove tags that are just numbers or very short
        invalid_tags = [tag for tag in tag_locations if len(tag) < 3 or tag.isdigit()]
        tags_to_remove.extend(invalid_tags)
        
        # Remove duplicates from list
        tags_to_remove = list(set(tags_to_remove))
        
        removed_count = 0
        errors = []
        
        for tag in tags_to_remove:
            for file_path in tag_locations[tag]:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Remove hashtag
                    pattern = f'#{tag}\\b'
                    updated_content = re.sub(pattern, '', content)
                    
                    if not dry_run and updated_content != content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                    
                    if updated_content != content:
                        removed_count += 1
                        
                except Exception as e:
                    errors.append({'file': str(file_path), 'tag': tag, 'error': str(e)})
        
        return {
            'tags_removed': len(tags_to_remove),
            'occurrences_removed': removed_count,
            'tags_list': tags_to_remove,
            'errors': errors,
            'dry_run': dry_run
        }
    
    def analyze_tag_relationships(self, tag_locations: Dict[str, List[Path]]) -> Dict:
        """Analyze relationships between tags with clustering"""
        import itertools
        
        # Build co-occurrence data
        file_tags = defaultdict(set)
        for tag, files in tag_locations.items():
            for file in files:
                file_tags[file].add(tag)
        
        # Calculate co-occurrences
        co_occurrences = defaultdict(lambda: defaultdict(int))
        for file, tags in file_tags.items():
            for tag1, tag2 in itertools.combinations(tags, 2):
                co_occurrences[tag1][tag2] += 1
                co_occurrences[tag2][tag1] += 1
        
        # Find strong associations
        strong_associations = []
        for tag, co_tags in co_occurrences.items():
            tag_count = len(tag_locations[tag])
            if tag_count > 5:  # Only analyze tags with sufficient data
                for co_tag, co_count in co_tags.items():
                    strength = co_count / tag_count
                    if strength > 0.3 and co_count > 3:
                        strong_associations.append({
                            'tag1': tag,
                            'tag2': co_tag,
                            'strength': strength,
                            'co_count': co_count
                        })
        
        # Remove duplicates and sort
        seen = set()
        unique_associations = []
        for assoc in sorted(strong_associations, key=lambda x: x['strength'], reverse=True):
            pair = tuple(sorted([assoc['tag1'], assoc['tag2']]))
            if pair not in seen:
                seen.add(pair)
                unique_associations.append(assoc)
        
        # Find tag clusters (groups of tags that frequently appear together)
        clusters = self._find_tag_clusters(co_occurrences, tag_locations)
        
        # Identify bridge tags (tags that connect different clusters)
        bridge_tags = self._find_bridge_tags(co_occurrences, tag_locations)
        
        # Find isolated tags (rarely co-occur with others)
        isolated_tags = []
        for tag, files in tag_locations.items():
            if len(files) > 3:  # Only consider tags with some usage
                co_tag_count = sum(1 for count in co_occurrences[tag].values() if count > 1)
                if co_tag_count < 2:
                    isolated_tags.append(tag)
        
        return {
            'strong_associations': unique_associations[:30],
            'co_occurrences': dict(co_occurrences),
            'file_tag_count': {f: len(tags) for f, tags in file_tags.items()},
            'clusters': clusters,
            'bridge_tags': bridge_tags,
            'isolated_tags': isolated_tags
        }
    
    def _find_tag_clusters(self, co_occurrences: Dict, tag_locations: Dict) -> List[Dict]:
        """Find clusters of related tags"""
        # Simple clustering based on co-occurrence strength
        clusters = []
        processed = set()
        
        # Find seed tags for clusters (highly connected tags)
        seed_candidates = []
        for tag in tag_locations:
            if tag not in processed and len(tag_locations[tag]) > 5:
                connections = sum(1 for co_tag, count in co_occurrences[tag].items() if count > 3)
                if connections > 5:
                    seed_candidates.append((tag, connections))
        
        # Sort by connectivity
        seed_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Build clusters around seeds
        for seed_tag, _ in seed_candidates[:10]:
            if seed_tag in processed:
                continue
                
            cluster = {seed_tag}
            processed.add(seed_tag)
            
            # Add strongly connected tags
            for co_tag, count in co_occurrences[seed_tag].items():
                if co_tag not in processed and count > 3:
                    strength = count / len(tag_locations[seed_tag])
                    if strength > 0.4:
                        cluster.add(co_tag)
                        processed.add(co_tag)
            
            if len(cluster) > 2:
                clusters.append({
                    'tags': list(cluster),
                    'size': len(cluster),
                    'total_uses': sum(len(tag_locations[t]) for t in cluster),
                    'seed': seed_tag
                })
        
        return sorted(clusters, key=lambda x: x['total_uses'], reverse=True)
    
    def _find_bridge_tags(self, co_occurrences: Dict, tag_locations: Dict) -> List[Dict]:
        """Novel algorithm identifying tags that connect research domains"""
        bridge_candidates = []
        
        # Enhanced domain definitions for better detection
        domain_patterns = {
            'education': {
                'keywords': ['learning', 'education', 'pedagogy', 'teaching', 'student', 
                            'classroom', 'curriculum', 'instruction', 'school', 'academic'],
                'patterns': ['_education', 'edu_', '_learning', 'teach_']
            },
            'ai': {
                'keywords': ['ai', 'artificial', 'machine', 'intelligence', 'algorithm',
                           'automated', 'computational', 'neural', 'deep', 'generative'],
                'patterns': ['ai_', '_ai', 'ml_', '_learning', 'intelligent_']
            },
            'research': {
                'keywords': ['research', 'method', 'study', 'analysis', 'theory', 
                           'framework', 'investigation', 'empirical', 'qualitative', 'quantitative'],
                'patterns': ['_research', 'research_', '_method', '_analysis', '_study']
            },
            'professional': {
                'keywords': ['teacher', 'professional', 'development', 'training', 
                           'practice', 'competency', 'faculty', 'educator', 'instructor'],
                'patterns': ['professional_', 'teacher_', '_development', '_training']
            },
            'social': {
                'keywords': ['social', 'online', 'community', 'collaborative', 'network',
                           'interaction', 'communication', 'virtual', 'digital', 'media'],
                'patterns': ['social_', 'online_', 'digital_', '_community', '_network']
            },
            'technology': {
                'keywords': ['technology', 'tech', 'digital', 'computer', 'software',
                           'platform', 'tool', 'system', 'application', 'interface'],
                'patterns': ['tech_', '_technology', 'digital_', 'computer_', '_system']
            },
            'assessment': {
                'keywords': ['assessment', 'evaluation', 'testing', 'measurement', 
                           'feedback', 'grading', 'performance', 'outcome', 'rubric'],
                'patterns': ['assess_', '_assessment', 'evaluat_', '_evaluation']
            },
            'cognitive': {
                'keywords': ['cognitive', 'thinking', 'metacognition', 'knowledge', 
                           'understanding', 'reasoning', 'problem', 'critical', 'creative'],
                'patterns': ['cognit_', '_thinking', 'meta_', '_knowledge']
            }
        }
        
        for tag, co_tags in co_occurrences.items():
            if len(tag_locations[tag]) < 5:  # Skip rarely used tags
                continue
                
            # Identify connected domains with enhanced detection
            connected_domains = set()
            domain_strengths = {}  # Track connection strength to each domain
            
            for co_tag in co_tags:
                co_tag_lower = co_tag.lower()
                co_tag_count = co_occurrences[tag][co_tag]
                
                for domain, criteria in domain_patterns.items():
                    # Check keywords
                    if any(keyword in co_tag_lower for keyword in criteria['keywords']):
                        connected_domains.add(domain)
                        domain_strengths[domain] = domain_strengths.get(domain, 0) + co_tag_count
                    
                    # Check patterns
                    for pattern in criteria['patterns']:
                        if pattern.startswith('_') and co_tag_lower.endswith(pattern[1:]):
                            connected_domains.add(domain)
                            domain_strengths[domain] = domain_strengths.get(domain, 0) + co_tag_count
                        elif pattern.endswith('_') and co_tag_lower.startswith(pattern[:-1]):
                            connected_domains.add(domain)
                            domain_strengths[domain] = domain_strengths.get(domain, 0) + co_tag_count
            
            # Bridge tags must connect 3+ domains
            if len(connected_domains) >= 3:
                # Calculate bridge strength score
                bridge_strength = sum(domain_strengths.values()) / len(connected_domains)
                
                bridge_candidates.append({
                    'tag': tag,
                    'domains_connected': list(connected_domains),
                    'domain_count': len(connected_domains),
                    'connection_count': len(co_tags),
                    'uses': len(tag_locations[tag]),
                    'bridge_strength': bridge_strength,
                    'domain_strengths': domain_strengths
                })
        
        # Sort by multiple criteria: domain count, bridge strength, total uses
        bridge_candidates.sort(
            key=lambda x: (x['domain_count'], x['bridge_strength'], x['uses']), 
            reverse=True
        )
        
        return bridge_candidates[:15]  # Return top 15 bridge tags
    
    def analyze_temporal_trends(self) -> Dict:
        """Classify tags as emerging or declining based on usage patterns"""
        tag_years = defaultdict(list)
        current_year = datetime.now().year
        
        # First pass: collect year data for all tags
        for md_file in self.vault_path.rglob('*.md'):
            try:
                # Extract year from filename (supports multiple formats)
                year_match = re.search(r'(\d{4})', md_file.name)
                if not year_match:
                    continue
                year = int(year_match.group(1))
                
                # Skip future years or very old years
                if year > current_year or year < 1990:
                    continue
                
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all hashtags and YAML tags
                hashtags = re.findall(r'#([\w_-]+)', content)
                
                # Also check YAML frontmatter
                if content.startswith('---'):
                    yaml_end = content.find('---', 3)
                    if yaml_end > 0:
                        frontmatter = content[3:yaml_end]
                        if 'tags:' in frontmatter:
                            yaml_tags = re.findall(r'^\s*-\s*(.+)$', frontmatter, re.MULTILINE)
                            hashtags.extend(yaml_tags)
                
                for tag in set(hashtags):
                    tag = tag.strip().lower()
                    if tag and not tag.endswith('_'):  # Exclude author tags
                        tag_years[tag].append(year)
                    
            except Exception:
                continue
        
        # Second pass: analyze trends with enhanced classification
        emerging_tags = []
        declining_tags = []
        stable_tags = []
        periodic_tags = []
        
        for tag, years in tag_years.items():
            if len(years) < 3:  # Need sufficient data
                continue
                
            years_counter = Counter(years)
            total_count = len(years)
            unique_years_set = set(years)
            unique_years = len(unique_years_set)
            
            # Calculate key metrics
            recent_count = sum(1 for y in years if y >= current_year - 2)
            recent_ratio = recent_count / total_count
            
            # Calculate year span and activity density
            year_span = max(years) - min(years) + 1
            activity_density = unique_years / year_span if year_span > 0 else 0
            
            # Find peak year and calculate trend
            peak_year, peak_count = max(years_counter.items(), key=lambda x: x[1])
            years_sorted = sorted(years)
            
            # Enhanced classification based on multiple criteria
            if total_count >= 5:  # Minimum threshold for meaningful analysis
                # Calculate emergence strength for emerging tags
                if recent_ratio > 0.7 and max(years) >= current_year - 2:
                    # Additional criteria for strong emergence
                    years_growth = []
                    for i in range(1, unique_years):
                        if i < len(years_sorted):
                            growth = years_sorted[i] - years_sorted[i-1]
                            years_growth.append(growth)
                    
                    avg_growth = sum(years_growth) / len(years_growth) if years_growth else 0
                    emergence_strength = recent_ratio * (1 + (1 / (avg_growth + 1)))
                    
                    emerging_tags.append({
                        'tag': tag,
                        'emergence_strength': emergence_strength,
                        'total_uses': total_count,
                        'recent_uses': recent_count,
                        'recent_ratio': recent_ratio,
                        'first_year': min(years),
                        'last_year': max(years),
                        'years_active': unique_years,
                        'activity_density': activity_density
                    })
                
                # Enhanced criteria for declining tags
                elif recent_ratio < 0.3 and peak_year < current_year - 3:
                    decline_rate = 1 - recent_ratio
                    years_since_peak = current_year - peak_year
                    
                    declining_tags.append({
                        'tag': tag,
                        'decline_rate': decline_rate,
                        'total_uses': total_count,
                        'recent_uses': recent_count,
                        'recent_ratio': recent_ratio,
                        'peak_year': peak_year,
                        'peak_count': peak_count,
                        'years_since_peak': years_since_peak,
                        'first_year': min(years),
                        'last_year': max(years)
                    })
                
                # Identify stable tags (consistent usage over time)
                elif 0.3 <= recent_ratio <= 0.7 and activity_density > 0.5:
                    variance = sum((years_counter[y] - (total_count/unique_years))**2 for y in years_counter) / unique_years
                    stability_score = 1 / (1 + variance)
                    
                    stable_tags.append({
                        'tag': tag,
                        'stability_score': stability_score,
                        'total_uses': total_count,
                        'years_active': unique_years,
                        'activity_density': activity_density,
                        'first_year': min(years),
                        'last_year': max(years)
                    })
                
                # Identify periodic/seasonal tags
                elif unique_years >= 3 and activity_density < 0.5:
                    # Tags that appear periodically but not consistently
                    gaps = []
                    sorted_unique_years = sorted(set(years))
                    for i in range(1, len(sorted_unique_years)):
                        gap = sorted_unique_years[i] - sorted_unique_years[i-1]
                        if gap > 1:
                            gaps.append(gap)
                    
                    if gaps:
                        avg_gap = sum(gaps) / len(gaps)
                        periodic_tags.append({
                            'tag': tag,
                            'total_uses': total_count,
                            'years_active': unique_years,
                            'average_gap': avg_gap,
                            'activity_pattern': 'periodic',
                            'first_year': min(years),
                            'last_year': max(years)
                        })
        
        # Sort by relevant metrics
        emerging_tags.sort(key=lambda x: (x['emergence_strength'], x['recent_uses']), reverse=True)
        declining_tags.sort(key=lambda x: (x['decline_rate'], x['years_since_peak']), reverse=True)
        stable_tags.sort(key=lambda x: x['stability_score'], reverse=True)
        periodic_tags.sort(key=lambda x: x['total_uses'], reverse=True)
        
        return {
            'emerging': emerging_tags[:15],
            'declining': declining_tags[:15],
            'stable': stable_tags[:10],
            'periodic': periodic_tags[:10],
            'yearly_distribution': dict(tag_years),
            'summary': {
                'total_temporal_tags': len(tag_years),
                'emerging_count': len(emerging_tags),
                'declining_count': len(declining_tags),
                'stable_count': len(stable_tags),
                'periodic_count': len(periodic_tags)
            }
        }
    
    def analyze_research_domains(self, tag_locations: Dict[str, List[Path]]) -> Dict:
        """Enhanced research domain analysis with auto-categorization"""
        # Expanded domain definitions with more keywords
        domains = {
            'AI & Technology': {
                'keywords': ['artificial_intelligence', 'ai', 'machine_learning', 'ml', 'chatgpt', 
                           'generative_ai', 'genai', 'ai_ethics', 'ai_literacy', 'large_language_models',
                           'llm', 'deep_learning', 'neural', 'algorithm', 'computational', 'automated',
                           'intelligent', 'robot', 'nlp', 'computer_vision'],
                'patterns': ['ai_', '_ai', 'tech_', '_technology', 'digital_', 'computer_']
            },
            'Education Levels': {
                'keywords': ['higher_education', 'k_12', 'k12', 'university', 'college', 'school',
                           'undergraduate', 'graduate', 'doctoral', 'phd', 'elementary', 'secondary',
                           'primary', 'tertiary', 'academic'],
                'patterns': ['_education', 'edu_', 'academic_', 'university_', 'school_']
            },
            'Research Methods': {
                'keywords': ['systematic_review', 'case_study', 'ethnography', 'qualitative',
                           'quantitative', 'meta_analysis', 'survey', 'interview', 'observation',
                           'experiment', 'methodology', 'analysis', 'data_collection', 'sampling'],
                'patterns': ['_method', '_analysis', '_study', 'research_', '_research']
            },
            'Learning & Pedagogy': {
                'keywords': ['collaborative_learning', 'online_learning', 'game_based_learning',
                           'personalized_learning', 'dialogic_learning', 'pedagogy', 'curriculum',
                           'instruction', 'teaching', 'assessment', 'evaluation', 'blended',
                           'flipped', 'active_learning', 'problem_based', 'project_based'],
                'patterns': ['_learning', 'teach_', '_pedagogy', 'instruct_', '_based']
            },
            'Professional Development': {
                'keywords': ['professional_development', 'teacher_education', 'teacher_training',
                           'faculty_development', 'staff_development', 'continuing_education',
                           'workshop', 'mentoring', 'coaching', 'competency', 'skill'],
                'patterns': ['professional_', 'teacher_', 'development_', 'training_']
            },
            'Social & Digital': {
                'keywords': ['social_media', 'twitter', 'facebook', 'online_communities', 
                           'digital_literacy', 'virtual', 'remote', 'network', 'collaboration',
                           'communication', 'interaction', 'engagement', 'participation'],
                'patterns': ['social_', 'online_', 'digital_', 'virtual_', 'cyber_']
            },
            'Theory & Philosophy': {
                'keywords': ['theory', 'framework', 'model', 'paradigm', 'epistemology',
                           'ontology', 'constructivism', 'behaviorism', 'cognitivism',
                           'sociocultural', 'critical', 'postmodern'],
                'patterns': ['_theory', 'theoretical_', '_model', '_framework']
            },
            'Assessment & Evaluation': {
                'keywords': ['assessment', 'evaluation', 'testing', 'grading', 'feedback',
                           'formative', 'summative', 'rubric', 'portfolio', 'exam',
                           'measurement', 'achievement', 'performance'],
                'patterns': ['assess_', '_assessment', 'evaluat_', '_evaluation', 'test_']
            }
        }
        
        # Auto-categorize all tags
        domain_assignments = defaultdict(list)
        uncategorized_tags = []
        
        for tag, files in tag_locations.items():
            assigned = False
            tag_lower = tag.lower()
            
            # Check each domain
            for domain, criteria in domains.items():
                # Check exact keyword matches
                if any(keyword in tag_lower for keyword in criteria['keywords']):
                    domain_assignments[domain].append((tag, len(files)))
                    assigned = True
                    continue
                
                # Check pattern matches
                if any(tag_lower.startswith(p) or tag_lower.endswith(p) 
                      for p in criteria['patterns'] if not p.startswith('_') and not p.endswith('_')):
                    domain_assignments[domain].append((tag, len(files)))
                    assigned = True
            
            # Track uncategorized tags
            if not assigned and len(files) > 2:  # Only track if used more than twice
                uncategorized_tags.append((tag, len(files)))
        
        # Calculate statistics
        domain_stats = {}
        for domain in domains:
            tags = domain_assignments.get(domain, [])
            domain_stats[domain] = {
                'total_uses': sum(count for _, count in tags),
                'unique_tags': len(tags),
                'top_tags': sorted(tags, key=lambda x: x[1], reverse=True)[:8],
                'percentage': 0  # Will calculate after
            }
        
        # Calculate percentages
        total_categorized_uses = sum(stats['total_uses'] for stats in domain_stats.values())
        for domain, stats in domain_stats.items():
            if total_categorized_uses > 0:
                stats['percentage'] = (stats['total_uses'] / total_categorized_uses) * 100
        
        # Add uncategorized section
        domain_stats['Uncategorized'] = {
            'total_uses': sum(count for _, count in uncategorized_tags),
            'unique_tags': len(uncategorized_tags),
            'top_tags': sorted(uncategorized_tags, key=lambda x: x[1], reverse=True)[:8],
            'percentage': 0
        }
        
        # Find cross-domain tags
        cross_domain_tags = []
        tag_domain_count = defaultdict(set)
        
        for domain, tags in domain_assignments.items():
            for tag, _ in tags:
                tag_domain_count[tag].add(domain)
        
        for tag, domains_set in tag_domain_count.items():
            if len(domains_set) > 1:
                cross_domain_tags.append({
                    'tag': tag,
                    'domains': list(domains_set),
                    'uses': len(tag_locations.get(tag, []))
                })
        
        return {
            'domain_stats': domain_stats,
            'cross_domain_tags': sorted(cross_domain_tags, key=lambda x: len(x['domains']), reverse=True)[:10],
            'total_tags_analyzed': len(tag_locations),
            'categorization_rate': (len(tag_locations) - len(uncategorized_tags)) / len(tag_locations) * 100 if tag_locations else 0
        }
    
    def _archive_old_reports(self, export_dir: Path):
        """Archive old tag reports to keep export directory clean"""
        archive_dir = export_dir / 'archive'
        
        # Find all existing tag reports
        tag_reports = list(export_dir.glob('tag_report_*.txt')) + list(export_dir.glob('tag_report_*.md'))
        
        if tag_reports:
            # Create archive directory if it doesn't exist
            archive_dir.mkdir(exist_ok=True)
            
            # Keep only the most recent report, archive the rest
            tag_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for report in tag_reports[1:]:  # Skip the most recent
                # Move to archive
                archive_path = archive_dir / report.name
                
                # If file already exists in archive, add timestamp
                if archive_path.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    archive_path = archive_dir / f"{report.stem}_archived_{timestamp}{report.suffix}"
                
                report.rename(archive_path)
                print(f"Archived: {report.name} → archive/{archive_path.name}")
    
    def _export_json_data(self, analysis: Dict, tag_locations: Dict[str, List[Path]]):
        """Export comprehensive tag data in JSON format for programmatic use"""
        # Prepare data for JSON export
        json_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'vault_path': str(self.vault_path),
                'total_tags': analysis['total_unique_tags'],
                'total_uses': analysis['total_tag_uses'],
                'total_files': len(set(file for files in tag_locations.values() for file in files))
            },
            'tag_usage': {
                tag: len(files) for tag, files in tag_locations.items()
            },
            'tag_files': {
                tag: [str(f.relative_to(self.vault_path)) for f in files]
                for tag, files in tag_locations.items()
            },
            'analysis': {
                'distribution': analysis['tag_distribution'],
                'most_common': analysis['most_common'],
                'potential_duplicates': analysis['potential_duplicates'],
                'standardization_suggestions': analysis['standardization_suggestions']
            },
            'advanced_analysis': {}
        }
        
        # Add advanced analysis if available
        try:
            # Temporal trends
            temporal = self.analyze_temporal_trends()
            json_data['advanced_analysis']['temporal_trends'] = {
                'emerging': temporal['emerging'],
                'declining': temporal['declining']
            }
            
            # Relationships
            relationships = self.analyze_tag_relationships(tag_locations)
            json_data['advanced_analysis']['relationships'] = {
                'strong_associations': relationships['strong_associations'][:50],
                'clusters': relationships['clusters'],
                'bridge_tags': relationships['bridge_tags'],
                'isolated_tags': relationships['isolated_tags']
            }
            
            # Domains
            domains = self.analyze_research_domains(tag_locations)
            json_data['advanced_analysis']['domains'] = domains
            
            # Semantic duplicates
            semantic = self.find_semantic_duplicates(tag_locations)
            json_data['advanced_analysis']['semantic_duplicates'] = semantic
            
            # Removal recommendations
            removal = self.analyze_tags_to_remove(tag_locations)
            json_data['advanced_analysis']['removal_recommendations'] = removal
            
            # Tag quality metrics
            quality_metrics = self.calculate_tag_quality_metrics(tag_locations)
            json_data['advanced_analysis']['quality_metrics'] = {
                'collection_metrics': quality_metrics['collection_metrics'],
                'top_quality_tags': quality_metrics['top_quality_tags'],
                'tags_to_promote': quality_metrics['tags_to_promote'],
                'tags_to_review': quality_metrics['tags_to_review'],
                'tag_quality_sample': dict(list(quality_metrics['tag_quality'].items())[:20])
            }
            
        except Exception as e:
            print(f"Warning: Could not complete advanced analysis for JSON: {e}")
        
        # Save JSON file
        json_path = self.vault_path / 'claude_workspace' / 'export' / f'tag_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"JSON data exported to: {json_path.name}")
    
    def find_semantic_duplicates(self, tag_locations: Dict[str, List[Path]]) -> List[Dict]:
        """Three-pronged approach to semantic similarity detection"""
        semantic_groups = []
        processed_tags = set()
        
        # Method 1: Enhanced stem matching with linguistic analysis
        from collections import defaultdict
        stem_groups = defaultdict(list)
        
        for tag in tag_locations:
            # Skip if already processed
            if tag in processed_tags:
                continue
                
            # Extract word stems more intelligently
            words = tag.split('_')
            if len(words) >= 1:
                # Try different stem extraction strategies
                # 1. Longest word as stem
                main_word = max(words, key=len) if words else tag
                
                # 2. First meaningful word (skip common prefixes)
                skip_prefixes = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for'}
                first_meaningful = next((w for w in words if w not in skip_prefixes and len(w) > 2), main_word)
                
                # 3. Root word detection (simple heuristic)
                root_candidates = []
                for word in words:
                    if len(word) > 4:
                        # Simple stemming: remove common suffixes
                        for suffix in ['ing', 'ed', 'er', 'est', 'ly', 'tion', 'ment', 'ness', 'ity']:
                            if word.endswith(suffix) and len(word) - len(suffix) > 3:
                                root_candidates.append(word[:-len(suffix)])
                                break
                        else:
                            root_candidates.append(word)
                
                # Group by most promising stem
                best_stem = root_candidates[0] if root_candidates else main_word
                stem_groups[best_stem].append(tag)
                
                # Also group by main word if different
                if main_word != best_stem and len(main_word) > 3:
                    stem_groups[main_word].append(tag)
        
        # Process stem groups
        for stem, tags in stem_groups.items():
            if len(tags) > 1 and len(stem) > 2:
                unique_tags = list(set(tags) - processed_tags)
                if len(unique_tags) > 1:
                    semantic_groups.append({
                        'type': 'stem_match',
                        'stem': stem,
                        'tags': unique_tags,
                        'total_uses': sum(len(tag_locations[t]) for t in unique_tags),
                        'confidence': 0.8
                    })
                    processed_tags.update(unique_tags)
        
        # Method 2: Enhanced synonym detection with academic vocabulary
        synonyms = {
            'education': ['teaching', 'learning', 'pedagogy', 'instruction', 'educational', 
                         'didactic', 'scholastic', 'academic', 'schooling'],
            'assessment': ['evaluation', 'testing', 'grading', 'examination', 'appraisal',
                          'measurement', 'scoring', 'judgment', 'review'],
            'technology': ['tech', 'digital', 'computer', 'it', 'technological', 
                          'computational', 'electronic', 'software', 'hardware'],
            'research': ['study', 'investigation', 'analysis', 'inquiry', 'examination',
                        'exploration', 'survey', 'review', 'experiment'],
            'professional': ['teacher', 'educator', 'faculty', 'instructor', 'practitioner',
                            'expert', 'specialist', 'mentor', 'coach'],
            'development': ['training', 'growth', 'improvement', 'advancement', 'progress',
                           'evolution', 'enhancement', 'cultivation', 'formation'],
            'online': ['virtual', 'remote', 'distance', 'digital', 'web', 'internet',
                      'cyber', 'electronic', 'networked'],
            'student': ['learner', 'pupil', 'scholar', 'trainee', 'apprentice',
                       'disciple', 'mentee', 'participant'],
            'artificial': ['ai', 'machine', 'automated', 'synthetic', 'computational',
                          'algorithmic', 'robotic', 'intelligent'],
            'collaborative': ['cooperative', 'joint', 'shared', 'collective', 'team',
                             'group', 'mutual', 'participatory'],
            'cognitive': ['thinking', 'mental', 'intellectual', 'reasoning', 'thought',
                         'mind', 'brain', 'psychological'],
            'knowledge': ['understanding', 'comprehension', 'awareness', 'expertise',
                         'wisdom', 'insight', 'information', 'learning']
        }
        
        synonym_groups = defaultdict(list)
        for tag in tag_locations:
            if tag in processed_tags:
                continue
                
            tag_words = set(tag.lower().split('_'))
            matched_concepts = []
            
            for concept, syns in synonyms.items():
                # Check if tag contains concept or any synonym
                all_terms = [concept] + syns
                if any(term in tag_words or any(term in word for word in tag_words) for term in all_terms):
                    matched_concepts.append(concept)
                    synonym_groups[concept].append(tag)
        
        # Process synonym groups
        for concept, tags in synonym_groups.items():
            unique_tags = list(set(tags) - processed_tags)
            if len(unique_tags) > 1:
                semantic_groups.append({
                    'type': 'synonym_group',
                    'concept': concept,
                    'tags': unique_tags[:10],  # Limit size
                    'total_uses': sum(len(tag_locations[t]) for t in unique_tags[:10]),
                    'confidence': 0.7
                })
        
        # Method 3: Enhanced pattern matching
        prefix_groups = defaultdict(list)
        suffix_groups = defaultdict(list)
        compound_groups = defaultdict(list)
        
        for tag in tag_locations:
            if tag in processed_tags:
                continue
                
            # Prefix matching (minimum 5 characters)
            if len(tag) > 8:
                for prefix_len in [5, 6, 7]:
                    if len(tag) > prefix_len:
                        prefix = tag[:prefix_len]
                        prefix_groups[prefix].append(tag)
            
            # Suffix matching (minimum 4 characters)
            if len(tag) > 7:
                for suffix_len in [4, 5, 6]:
                    if len(tag) > suffix_len:
                        suffix = tag[-suffix_len:]
                        suffix_groups[suffix].append(tag)
            
            # Compound word detection
            words = tag.split('_')
            if len(words) >= 2:
                # Group by first two words
                compound_key = '_'.join(words[:2])
                if len(compound_key) > 4:
                    compound_groups[compound_key].append(tag)
                
                # Group by last two words
                compound_key = '_'.join(words[-2:])
                if len(compound_key) > 4:
                    compound_groups[compound_key].append(tag)
        
        # Process pattern groups
        for prefix, tags in prefix_groups.items():
            unique_tags = list(set(tags) - processed_tags)
            if len(unique_tags) > 2 and len(prefix) >= 5:
                semantic_groups.append({
                    'type': 'common_prefix',
                    'pattern': f"{prefix}*",
                    'tags': unique_tags[:8],
                    'total_uses': sum(len(tag_locations[t]) for t in unique_tags[:8]),
                    'confidence': 0.6
                })
        
        for suffix, tags in suffix_groups.items():
            unique_tags = list(set(tags) - processed_tags)
            if len(unique_tags) > 2 and len(suffix) >= 4:
                semantic_groups.append({
                    'type': 'common_suffix',
                    'pattern': f"*{suffix}",
                    'tags': unique_tags[:8],
                    'total_uses': sum(len(tag_locations[t]) for t in unique_tags[:8]),
                    'confidence': 0.6
                })
        
        for compound, tags in compound_groups.items():
            unique_tags = list(set(tags) - processed_tags)
            if len(unique_tags) > 2:
                semantic_groups.append({
                    'type': 'compound_pattern',
                    'pattern': compound,
                    'tags': unique_tags[:8],
                    'total_uses': sum(len(tag_locations[t]) for t in unique_tags[:8]),
                    'confidence': 0.65
                })
        
        # Sort by confidence and total uses
        semantic_groups.sort(key=lambda x: (x['confidence'], x['total_uses']), reverse=True)
        
        # Deduplicate overlapping groups
        final_groups = []
        seen_tags = set()
        
        for group in semantic_groups:
            # Only include if at least half the tags are new
            new_tags = [t for t in group['tags'] if t not in seen_tags]
            if len(new_tags) >= len(group['tags']) / 2:
                group['tags'] = new_tags
                group['total_uses'] = sum(len(tag_locations[t]) for t in new_tags)
                final_groups.append(group)
                seen_tags.update(new_tags)
        
        return final_groups[:20]  # Top 20 groups
    
    def calculate_tag_metrics(self, tag_locations: Dict[str, List[Path]]) -> Dict:
        """Calculate advanced metrics for tag quality and usage patterns"""
        metrics = {
            'tag_quality_scores': {},
            'usage_patterns': {},
            'co_occurrence_strength': {},
            'tag_entropy': {},
            'collection_metrics': {},
            'recommendation_score': {}
        }
        
        # Get relationships for co-occurrence analysis
        relationships = self.analyze_tag_relationships(tag_locations)
        co_occurrences = relationships['co_occurrences']
        
        # Calculate collection-wide metrics
        total_files = len(set(file for files in tag_locations.values() for file in files))
        total_tags = len(tag_locations)
        total_tag_uses = sum(len(files) for files in tag_locations.values())
        
        metrics['collection_metrics'] = {
            'total_files': total_files,
            'total_unique_tags': total_tags,
            'total_tag_uses': total_tag_uses,
            'avg_tags_per_file': total_tag_uses / total_files if total_files > 0 else 0,
            'tag_density': total_tags / total_files if total_files > 0 else 0,
            'tag_reuse_ratio': total_tag_uses / total_tags if total_tags > 0 else 0
        }
        
        # Calculate per-tag metrics
        for tag, files in tag_locations.items():
            tag_count = len(files)
            
            # Quality score components
            # 1. Usage frequency (normalized)
            usage_score = min(tag_count / 50, 1.0)  # Cap at 50 uses
            
            # 2. Co-occurrence diversity
            co_tags = co_occurrences.get(tag, {})
            diversity_score = min(len(co_tags) / 20, 1.0)  # Cap at 20 co-tags
            
            # 3. Semantic clarity (based on tag structure)
            words = tag.split('_')
            clarity_score = 1.0
            if len(tag) < 3 or tag.isdigit():
                clarity_score = 0.1
            elif len(words) > 5:
                clarity_score = 0.5
            elif len(words) == 1 and len(tag) < 5:
                clarity_score = 0.3
            
            # 4. Temporal consistency (if year data available)
            temporal_score = 1.0  # Default if no temporal data
            
            # Overall quality score
            quality_score = (usage_score * 0.3 + diversity_score * 0.3 + 
                           clarity_score * 0.3 + temporal_score * 0.1)
            
            metrics['tag_quality_scores'][tag] = {
                'overall': quality_score,
                'usage': usage_score,
                'diversity': diversity_score,
                'clarity': clarity_score,
                'temporal': temporal_score,
                'raw_count': tag_count
            }
            
            # Usage pattern analysis
            if tag_count >= 3:  # Need minimum data
                # Calculate distribution entropy
                file_years = []
                for file in files:
                    year_match = re.search(r'(\d{4})', file.name)
                    if year_match:
                        file_years.append(int(year_match.group(1)))
                
                if file_years:
                    from collections import Counter
                    year_counts = Counter(file_years)
                    total = sum(year_counts.values())
                    entropy = -sum((count/total) * (count/total).bit_length() 
                                 for count in year_counts.values() if count > 0)
                    metrics['tag_entropy'][tag] = entropy
                
                # Co-occurrence strength
                if co_tags:
                    avg_strength = sum(co_tags.values()) / len(co_tags)
                    max_strength = max(co_tags.values())
                    metrics['co_occurrence_strength'][tag] = {
                        'average': avg_strength,
                        'maximum': max_strength,
                        'partners': len(co_tags)
                    }
        
        # Calculate recommendation scores
        for tag, quality in metrics['tag_quality_scores'].items():
            # High quality tags to promote
            if quality['overall'] > 0.7:
                metrics['recommendation_score'][tag] = {
                    'action': 'promote',
                    'score': quality['overall'],
                    'reason': 'High quality tag with good usage patterns'
                }
            # Low quality tags to review
            elif quality['overall'] < 0.3:
                reasons = []
                if quality['usage'] < 0.2:
                    reasons.append('low usage')
                if quality['clarity'] < 0.5:
                    reasons.append('poor clarity')
                if quality['diversity'] < 0.2:
                    reasons.append('isolated usage')
                
                metrics['recommendation_score'][tag] = {
                    'action': 'review',
                    'score': quality['overall'],
                    'reason': ', '.join(reasons)
                }
        
        # Sort recommendations by score
        metrics['top_quality_tags'] = sorted(
            [(tag, scores['overall']) for tag, scores in metrics['tag_quality_scores'].items()],
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        metrics['bottom_quality_tags'] = sorted(
            [(tag, scores['overall']) for tag, scores in metrics['tag_quality_scores'].items()],
            key=lambda x: x[1]
        )[:20]
        
        return metrics
    
    def analyze_tags_to_remove(self, tag_locations: Dict[str, List[Path]]) -> Dict:
        """Comprehensive analysis of tags that should be removed"""
        removal_candidates = {
            'too_generic': [],
            'too_specific': [],
            'redundant': [],
            'malformed': [],
            'obsolete': [],
            'low_value': []
        }
        
        # Generic tags that don't add value
        generic_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
                        'new', 'old', 'good', 'bad', 'big', 'small', 'more', 'less',
                        'yes', 'no', 'true', 'false', 'article', 'paper', 'study', 'research'}
        
        for tag, files in tag_locations.items():
            # Too generic
            if tag in generic_words or len(tag) < 3:
                removal_candidates['too_generic'].append({
                    'tag': tag,
                    'uses': len(files),
                    'reason': 'Common word or too short'
                })
            
            # Too specific (single use, very long)
            elif len(files) == 1 and len(tag) > 30:
                removal_candidates['too_specific'].append({
                    'tag': tag,
                    'uses': 1,
                    'reason': 'Single use and very long'
                })
            
            # Malformed (contains numbers only, special patterns)
            elif tag.isdigit() or re.match(r'^[0-9_]+$', tag):
                removal_candidates['malformed'].append({
                    'tag': tag,
                    'uses': len(files),
                    'reason': 'Contains only numbers or underscores'
                })
            
            # Low value (very rare use, not connected to other tags)
            elif len(files) <= 2:
                # Check if isolated (appears alone in files)
                isolated = True
                for file in files:
                    # Would need to check if other tags exist in same file
                    # For now, just mark very rare tags
                    pass
                
                if len(files) == 1:
                    removal_candidates['low_value'].append({
                        'tag': tag,
                        'uses': 1,
                        'reason': 'Single use tag'
                    })
        
        # Find redundant tags (covered by the semantic duplicate analysis)
        semantic_dupes = self.find_semantic_duplicates(tag_locations)
        for group in semantic_dupes:
            if group['type'] in ['stem_match', 'common_prefix']:
                # Recommend keeping the most used, remove others
                tags_by_use = sorted(
                    [(t, len(tag_locations[t])) for t in group['tags']], 
                    key=lambda x: x[1], 
                    reverse=True
                )
                for tag, uses in tags_by_use[1:]:  # All except most used
                    removal_candidates['redundant'].append({
                        'tag': tag,
                        'uses': uses,
                        'reason': f"Redundant with '{tags_by_use[0][0]}'"
                    })
        
        # Calculate statistics
        total_removals = sum(len(items) for items in removal_candidates.values())
        total_uses = sum(
            item['uses'] for items in removal_candidates.values() 
            for item in items
        )
        
        return {
            'candidates': removal_candidates,
            'statistics': {
                'total_tags_to_remove': total_removals,
                'total_uses_affected': total_uses,
                'by_category': {
                    cat: len(items) for cat, items in removal_candidates.items()
                }
            }
        }
    
    def calculate_tag_quality_metrics(self, tag_locations: Dict[str, List[Path]]) -> Dict:
        """Calculate comprehensive quality scores for each tag based on multiple criteria"""
        quality_metrics = {}
        
        # Get additional data for quality assessment
        co_occurrences = defaultdict(lambda: defaultdict(int))
        file_tags = defaultdict(set)
        
        # Build co-occurrence data
        for tag, files in tag_locations.items():
            for file in files:
                file_tags[file].add(tag)
        
        for file, tags in file_tags.items():
            for tag1 in tags:
                for tag2 in tags:
                    if tag1 != tag2:
                        co_occurrences[tag1][tag2] += 1
        
        # Calculate temporal data
        tag_years = defaultdict(list)
        current_year = datetime.now().year
        
        for md_file in self.vault_path.rglob('*.md'):
            try:
                year_match = re.search(r'(\d{4})', md_file.name)
                if year_match:
                    year = int(year_match.group(1))
                    if 1990 <= year <= current_year:
                        with open(md_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        hashtags = re.findall(r'#([\w_-]+)', content)
                        for tag in hashtags:
                            tag = tag.strip().lower()
                            if tag and not tag.endswith('_'):
                                tag_years[tag].append(year)
            except Exception:
                continue
        
        # Calculate quality metrics for each tag
        for tag, files in tag_locations.items():
            if tag.endswith('_'):  # Skip author tags
                continue
                
            # 1. Usage metrics
            usage_count = len(files)
            usage_score = min(usage_count / 10, 1.0)  # Normalize to 0-1, max at 10 uses
            
            # 2. Diversity metrics (appears across different contexts)
            co_tag_count = len([t for t, count in co_occurrences[tag].items() if count > 1])
            diversity_score = min(co_tag_count / 20, 1.0)  # Normalize to 0-1, max at 20 co-tags
            
            # 3. Clarity metrics (tag length and readability)
            tag_length = len(tag)
            word_count = len(tag.split('_'))
            clarity_score = 0.0
            
            if 5 <= tag_length <= 30:  # Optimal length range
                clarity_score += 0.5
            if 1 <= word_count <= 3:  # Optimal word count
                clarity_score += 0.5
            
            # 4. Temporal consistency
            temporal_score = 0.0
            if tag in tag_years and len(tag_years[tag]) >= 3:
                years = sorted(set(tag_years[tag]))
                year_span = max(years) - min(years) + 1
                activity_density = len(years) / year_span if year_span > 0 else 0
                temporal_score = activity_density
            
            # 5. Semantic value (not too generic, not too specific)
            semantic_score = 1.0
            generic_terms = ['research', 'study', 'paper', 'article', 'new', 'good', 'bad', 'thing']
            if tag in generic_terms:
                semantic_score = 0.3
            elif usage_count == 1:  # Too specific
                semantic_score = 0.5
            elif '_and_' in tag or '_or_' in tag:  # Compound concepts
                semantic_score = 0.7
            
            # 6. Calculate overall quality score
            weights = {
                'usage': 0.25,
                'diversity': 0.25,
                'clarity': 0.20,
                'temporal': 0.15,
                'semantic': 0.15
            }
            
            overall_score = (
                usage_score * weights['usage'] +
                diversity_score * weights['diversity'] +
                clarity_score * weights['clarity'] +
                temporal_score * weights['temporal'] +
                semantic_score * weights['semantic']
            )
            
            # Determine quality category and recommendations
            quality_category = 'low'
            recommendations = []
            
            if overall_score >= 0.7:
                quality_category = 'high'
                recommendations.append('Promote as standard tag')
            elif overall_score >= 0.5:
                quality_category = 'medium'
                if usage_score < 0.3:
                    recommendations.append('Increase usage across more articles')
                if diversity_score < 0.3:
                    recommendations.append('Use with more diverse tags')
            else:
                quality_category = 'low'
                if clarity_score < 0.5:
                    recommendations.append('Consider renaming for clarity')
                if semantic_score < 0.5:
                    recommendations.append('Too generic or too specific')
                if usage_count < 3:
                    recommendations.append('Consider removing due to low usage')
            
            quality_metrics[tag] = {
                'overall_score': round(overall_score, 3),
                'quality_category': quality_category,
                'scores': {
                    'usage': round(usage_score, 3),
                    'diversity': round(diversity_score, 3),
                    'clarity': round(clarity_score, 3),
                    'temporal': round(temporal_score, 3),
                    'semantic': round(semantic_score, 3)
                },
                'metrics': {
                    'usage_count': usage_count,
                    'co_tag_count': co_tag_count,
                    'tag_length': tag_length,
                    'word_count': word_count,
                    'years_active': len(set(tag_years.get(tag, [])))
                },
                'recommendations': recommendations
            }
        
        # Sort by overall score
        sorted_metrics = dict(sorted(
            quality_metrics.items(),
            key=lambda x: x[1]['overall_score'],
            reverse=True
        ))
        
        # Calculate collection-wide metrics
        total_tags = len(tag_locations)
        total_files = len(file_tags)
        total_tag_uses = sum(len(files) for files in tag_locations.values())
        
        collection_metrics = {
            'total_tags': total_tags,
            'total_files': total_files,
            'total_tag_uses': total_tag_uses,
            'avg_tags_per_file': round(total_tag_uses / total_files, 2) if total_files > 0 else 0,
            'tag_density': round(total_tag_uses / total_tags, 2) if total_tags > 0 else 0,
            'reuse_ratio': round(total_tag_uses / total_tags, 2) if total_tags > 0 else 0,
            'quality_distribution': {
                'high': len([t for t, m in quality_metrics.items() if m['quality_category'] == 'high']),
                'medium': len([t for t, m in quality_metrics.items() if m['quality_category'] == 'medium']),
                'low': len([t for t, m in quality_metrics.items() if m['quality_category'] == 'low'])
            }
        }
        
        return {
            'tag_quality': sorted_metrics,
            'collection_metrics': collection_metrics,
            'top_quality_tags': list(sorted_metrics.keys())[:20],
            'tags_to_promote': [t for t, m in sorted_metrics.items() if 'Promote as standard tag' in m['recommendations']][:10],
            'tags_to_review': [t for t, m in sorted_metrics.items() if m['quality_category'] == 'low'][:20]
        }
    
    def export_tag_report(self, output_path: str = None, format: str = 'txt', include_advanced: bool = True) -> str:
        """Export comprehensive tag report with optional advanced analysis"""
        analysis = self.analyze_tags()
        tag_locations = self.scan_vault_tags()
        
        # Also export JSON data for programmatic use
        if format == 'txt' and not output_path:  # Only for default reports
            self._export_json_data(analysis, tag_locations)
        
        # Use .txt extension by default to avoid Obsidian graph issues
        file_extension = '.txt' if format == 'txt' else '.md'
        
        if not output_path:
            export_dir = self.vault_path / 'claude_workspace' / 'system1_tagging' / 'export'
            
            # Archive old reports before creating new one
            self._archive_old_reports(export_dir)
            
            output_path = export_dir / f'tag_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}{file_extension}'
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate report with plain text formatting for .txt files
        if format == 'txt':
            report_lines = [
                f"OBSIDIAN VAULT TAG ANALYSIS REPORT",
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"",
                f"SUMMARY",
                f"- Total unique tags: {analysis['total_unique_tags']}",
                f"- Total tag uses: {analysis['total_tag_uses']}",
                f"- Average uses per tag: {analysis['total_tag_uses'] / analysis['total_unique_tags']:.1f}",
                f"",
                f"TAG DISTRIBUTION",
                f"- Single use tags: {analysis['tag_distribution']['single_use']}",
                f"- Rare use (2-5): {analysis['tag_distribution']['rare_use']}",
                f"- Moderate use (6-20): {analysis['tag_distribution']['moderate_use']}",
                f"- Common use (>20): {analysis['tag_distribution']['common_use']}",
                f"",
                f"MOST COMMON TAGS"
            ]
        else:
            # Markdown format
            report_lines = [
                f"# Obsidian Vault Tag Analysis Report",
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"",
                f"## Summary",
                f"- Total unique tags: {analysis['total_unique_tags']}",
                f"- Total tag uses: {analysis['total_tag_uses']}",
                f"- Average uses per tag: {analysis['total_tag_uses'] / analysis['total_unique_tags']:.1f}",
                f"",
                f"## Tag Distribution",
                f"- Single use tags: {analysis['tag_distribution']['single_use']}",
                f"- Rare use (2-5): {analysis['tag_distribution']['rare_use']}",
                f"- Moderate use (6-20): {analysis['tag_distribution']['moderate_use']}",
                f"- Common use (>20): {analysis['tag_distribution']['common_use']}",
                f"",
                f"## Most Common Tags"
            ]
        
        for tag, count in analysis['most_common']:
            report_lines.append(f"- #{tag}: {count} uses")
        
        if format == 'txt':
            report_lines.extend([
                f"",
                f"POTENTIAL DUPLICATES"
            ])
            
            for tag1, tag2, similarity in analysis['potential_duplicates']:
                report_lines.append(f"- '{tag1}' <-> '{tag2}' (similarity: {similarity:.2%})")
            
            report_lines.extend([
                f"",
                f"STANDARDIZATION SUGGESTIONS"
            ])
            
            for suggestion in analysis['standardization_suggestions']:
                report_lines.append(f"- Change '#{suggestion['current']}' -> '#{suggestion['suggested']}' ({suggestion['current_uses']} uses)")
            
            # Removed TOP 100 tag list - not useful for analysis
        else:
            # Markdown format
            report_lines.extend([
                f"",
                f"## Potential Duplicates"
            ])
            
            for tag1, tag2, similarity in analysis['potential_duplicates']:
                report_lines.append(f"- '{tag1}' ↔ '{tag2}' (similarity: {similarity:.2%})")
            
            report_lines.extend([
                f"",
                f"## Standardization Suggestions"
            ])
            
            for suggestion in analysis['standardization_suggestions']:
                report_lines.append(f"- Change '#{suggestion['current']}' → '#{suggestion['suggested']}' ({suggestion['current_uses']} uses)")
            
            # Removed complete tag list - not useful for analysis
        
        # Add advanced analysis sections if requested
        if include_advanced:
            if format == 'txt':
                report_lines.extend([
                    "",
                    "=" * 80,
                    "ADVANCED ANALYSIS",
                    "=" * 80,
                    ""
                ])
            else:
                report_lines.extend([
                    "",
                    "## Advanced Analysis",
                    ""
                ])
            
            # Add temporal trends
            temporal_trends = self.analyze_temporal_trends()
            
            if format == 'txt':
                report_lines.extend([
                    "TEMPORAL TRENDS",
                    "-" * 40,
                    "",
                    f"Analyzed {temporal_trends['summary']['total_temporal_tags']} tags with temporal data",
                    "",
                    "Emerging Tags (>70% recent usage):"
                ])
                for tag in temporal_trends['emerging'][:8]:
                    report_lines.append(
                        f"- #{tag['tag']}: {tag['recent_uses']}/{tag['total_uses']} recent uses "
                        f"(emergence strength: {tag['emergence_strength']:.2f}, first seen: {tag['first_year']})"
                    )
                
                report_lines.extend([
                    "",
                    "Declining Tags (<30% recent usage):"
                ])
                for tag in temporal_trends['declining'][:8]:
                    report_lines.append(
                        f"- #{tag['tag']}: only {tag['recent_uses']}/{tag['total_uses']} recent uses "
                        f"(decline rate: {tag['decline_rate']:.1%}, peak: {tag['peak_year']}, "
                        f"{tag['years_since_peak']} years since peak)"
                    )
                
                report_lines.extend([
                    "",
                    "Stable Tags (consistent usage):"
                ])
                for tag in temporal_trends['stable'][:5]:
                    report_lines.append(
                        f"- #{tag['tag']}: {tag['total_uses']} uses over {tag['years_active']} years "
                        f"(stability: {tag['stability_score']:.2f})"
                    )
                
                if temporal_trends['periodic']:
                    report_lines.extend([
                        "",
                        "Periodic Tags (intermittent usage):"
                    ])
                    for tag in temporal_trends['periodic'][:5]:
                        report_lines.append(
                            f"- #{tag['tag']}: {tag['total_uses']} uses, appears every ~{tag['average_gap']:.1f} years"
                        )
            
            # Add relationship analysis
            relationships = self.analyze_tag_relationships(tag_locations)
            
            if format == 'txt':
                report_lines.extend([
                    "",
                    "TAG RELATIONSHIPS",
                    "-" * 40,
                    "",
                    "Strong Associations (tags that frequently appear together):"
                ])
                for assoc in relationships['strong_associations'][:15]:
                    report_lines.append(
                        f"- {assoc['tag1']} <-> {assoc['tag2']} "
                        f"(strength: {assoc['strength']:.1%}, co-occurs: {assoc['co_count']} times)"
                    )
                
                # Add tag clusters
                report_lines.extend([
                    "",
                    "TAG CLUSTERS (groups of related tags):"
                ])
                for cluster in relationships['clusters'][:8]:
                    tags_str = ', '.join([f"#{t}" for t in cluster['tags'][:8]])
                    if len(cluster['tags']) > 8:
                        tags_str += f" +{len(cluster['tags'])-8} more"
                    report_lines.append(
                        f"- Cluster around '{cluster['seed']}': {tags_str} "
                        f"({cluster['size']} tags, {cluster['total_uses']} total uses)"
                    )
                
                # Add bridge tags
                report_lines.extend([
                    "",
                    "BRIDGE TAGS (connecting multiple research areas):"
                ])
                for bridge in relationships['bridge_tags'][:8]:
                    domains = ', '.join(bridge['domains_connected'])
                    report_lines.append(
                        f"- #{bridge['tag']} connects {bridge['domain_count']} domains: {domains} "
                        f"({bridge['connection_count']} connections, strength: {bridge['bridge_strength']:.1f})"
                    )
                
                # Add isolated tags
                if relationships['isolated_tags']:
                    report_lines.extend([
                        "",
                        "ISOLATED TAGS (rarely appear with other tags):",
                        f"- {', '.join(['#' + t for t in relationships['isolated_tags'][:10]])}"
                    ])
            
            # Add domain analysis
            domains = self.analyze_research_domains(tag_locations)
            
            if format == 'txt':
                report_lines.extend([
                    "",
                    "RESEARCH DOMAIN DISTRIBUTION",
                    "-" * 40,
                    "",
                    f"Categorization rate: {domains['categorization_rate']:.1f}% of tags categorized",
                    ""
                ])
                
                # Sort domains by usage
                sorted_domains = sorted(
                    domains['domain_stats'].items(), 
                    key=lambda x: x[1]['total_uses'], 
                    reverse=True
                )
                
                for domain, stats in sorted_domains:
                    if stats['total_uses'] > 0:  # Only show domains with content
                        report_lines.append(f"{domain}: ({stats['percentage']:.1f}% of categorized tags)")
                        report_lines.append(f"  Total uses: {stats['total_uses']}")
                        report_lines.append(f"  Unique tags: {stats['unique_tags']}")
                        if stats['top_tags']:
                            report_lines.append("  Top tags:")
                            for tag, count in stats['top_tags'][:5]:  # Limit to top 5
                                report_lines.append(f"    - #{tag}: {count} uses")
                        report_lines.append("")
                
                # Add cross-domain tags
                if domains['cross_domain_tags']:
                    report_lines.extend([
                        "CROSS-DOMAIN TAGS:",
                        ""
                    ])
                    for tag_info in domains['cross_domain_tags'][:8]:
                        domains_str = ' + '.join(tag_info['domains'][:3])
                        if len(tag_info['domains']) > 3:
                            domains_str += f" +{len(tag_info['domains'])-3} more"
                        report_lines.append(
                            f"- #{tag_info['tag']} spans: {domains_str} ({tag_info['uses']} uses)"
                        )
                    report_lines.append("")
            
            # Add semantic duplicate analysis
            semantic_dupes = self.find_semantic_duplicates(tag_locations)
            
            if format == 'txt':
                report_lines.extend([
                    "",
                    "SEMANTIC DUPLICATE ANALYSIS",
                    "-" * 40,
                    "",
                    "Groups of semantically similar tags:"
                ])
                
                for group in semantic_dupes[:12]:
                    tags_str = ', '.join([f"#{t}" for t in group['tags'][:5]])
                    if len(group['tags']) > 5:
                        tags_str += f" +{len(group['tags'])-5} more"
                    
                    confidence_str = f"confidence: {group['confidence']:.0%}" if 'confidence' in group else ""
                    
                    if group['type'] == 'stem_match':
                        report_lines.append(
                            f"- Stem '{group['stem']}': {tags_str} "
                            f"({group['total_uses']} total uses, {confidence_str})"
                        )
                    elif group['type'] == 'synonym_group':
                        report_lines.append(
                            f"- Concept '{group['concept']}': {tags_str} "
                            f"({group['total_uses']} total uses, {confidence_str})"
                        )
                    elif group['type'] == 'common_prefix':
                        report_lines.append(
                            f"- Pattern '{group['pattern']}': {tags_str} "
                            f"({group['total_uses']} total uses, {confidence_str})"
                        )
                    elif group['type'] == 'common_suffix':
                        report_lines.append(
                            f"- Pattern '{group['pattern']}': {tags_str} "
                            f"({group['total_uses']} total uses, {confidence_str})"
                        )
                    elif group['type'] == 'compound_pattern':
                        report_lines.append(
                            f"- Compound '{group['pattern']}': {tags_str} "
                            f"({group['total_uses']} total uses, {confidence_str})"
                        )
            
            # Add tag quality metrics
            quality_metrics = self.calculate_tag_quality_metrics(tag_locations)
            
            if format == 'txt':
                report_lines.extend([
                    "",
                    "TAG QUALITY METRICS",
                    "-" * 40,
                    "",
                    "Collection Overview:",
                    f"- Total files analyzed: {quality_metrics['collection_metrics']['total_files']}",
                    f"- Total unique tags: {quality_metrics['collection_metrics']['total_tags']}",
                    f"- Total tag uses: {quality_metrics['collection_metrics']['total_tag_uses']}",
                    f"- Average tags per file: {quality_metrics['collection_metrics']['avg_tags_per_file']}",
                    f"- Tag density: {quality_metrics['collection_metrics']['tag_density']}",
                    f"- Tag reuse ratio: {quality_metrics['collection_metrics']['reuse_ratio']}",
                    "",
                    "Quality Distribution:",
                    f"- High quality tags: {quality_metrics['collection_metrics']['quality_distribution']['high']}",
                    f"- Medium quality tags: {quality_metrics['collection_metrics']['quality_distribution']['medium']}",
                    f"- Low quality tags: {quality_metrics['collection_metrics']['quality_distribution']['low']}",
                    "",
                    "Top Quality Tags (promote these as standard tags):"
                ])
                
                for tag in quality_metrics['top_quality_tags'][:10]:
                    tag_data = quality_metrics['tag_quality'][tag]
                    report_lines.append(
                        f"- #{tag}: score {tag_data['overall_score']} "
                        f"(usage: {tag_data['metrics']['usage_count']}, "
                        f"diversity: {tag_data['metrics']['co_tag_count']} co-tags)"
                    )
                
                report_lines.extend([
                    "",
                    "Tags to Review (low quality):"
                ])
                
                for tag in quality_metrics['tags_to_review'][:10]:
                    if tag in quality_metrics['tag_quality']:
                        tag_data = quality_metrics['tag_quality'][tag]
                        recommendations = '; '.join(tag_data['recommendations'][:2])  # First 2 recommendations
                        report_lines.append(f"- #{tag}: score {tag_data['overall_score']} ({recommendations})")
                    else:
                        report_lines.append(f"- #{tag}: needs review")
            
            # Add tag removal recommendations
            removal_analysis = self.analyze_tags_to_remove(tag_locations)
            
            if format == 'txt':
                report_lines.extend([
                    "",
                    "TAG REMOVAL RECOMMENDATIONS",
                    "-" * 40,
                    "",
                    f"Total tags recommended for removal: {removal_analysis['statistics']['total_tags_to_remove']}",
                    f"Total tag uses affected: {removal_analysis['statistics']['total_uses_affected']}",
                    ""
                ])
                
                # Show breakdown by category
                for category, count in removal_analysis['statistics']['by_category'].items():
                    if count > 0:
                        report_lines.append(f"- {category.replace('_', ' ').title()}: {count} tags")
                
                # Show examples from each category
                report_lines.append("\nExamples:")
                
                for category, items in removal_analysis['candidates'].items():
                    if items:
                        report_lines.append(f"\n{category.replace('_', ' ').title()}:")
                        for item in items[:3]:  # Show top 3 examples
                            report_lines.append(
                                f"- #{item['tag']} ({item['uses']} uses) - {item['reason']}"
                            )
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        return str(output_path)
    
    def interactive_deduplication(self):
        """Interactive session for tag deduplication"""
        print(f"\n🏷️  Obsidian Tag Deduplication")
        print(f"{'='*60}")
        
        analysis = self.analyze_tags()
        
        print(f"Found {analysis['total_unique_tags']} unique tags")
        print(f"Found {len(analysis['potential_duplicates'])} potential duplicate pairs")
        print(f"Found {len(analysis['standardization_suggestions'])} standardization suggestions")
        
        # Process potential duplicates
        if analysis['potential_duplicates']:
            print(f"\n## Potential Duplicates")
            for tag1, tag2, similarity in analysis['potential_duplicates'][:10]:
                print(f"\n'{tag1}' ↔ '{tag2}' (similarity: {similarity:.2%})")
                # In real implementation, would ask user to merge or skip
        
        # Process standardization suggestions
        if analysis['standardization_suggestions']:
            print(f"\n## Standardization Suggestions")
            for suggestion in analysis['standardization_suggestions'][:10]:
                print(f"\nChange '#{suggestion['current']}' → '#{suggestion['suggested']}'")
                print(f"  Current uses: {suggestion['current_uses']}")
                if 'standard_uses' in suggestion:
                    print(f"  Standard tag uses: {suggestion['standard_uses']}")
                # In real implementation, would ask user to apply or skip

def main():
    parser = argparse.ArgumentParser(description='Manage tags in Obsidian vault')
    parser.add_argument('--vault-path', default='.',
                       help='Path to Obsidian vault (default: current directory)')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze all tags in vault')
    parser.add_argument('--report', action='store_true',
                       help='Generate comprehensive tag report')
    parser.add_argument('--advanced', action='store_true',
                       help='Include advanced analysis in report (relationships, trends, domains)')
    parser.add_argument('--deduplicate', action='store_true',
                       help='Interactive tag deduplication')
    parser.add_argument('--merge', nargs=2, metavar=('OLD_TAG', 'NEW_TAG'),
                       help='Merge old tag into new tag')
    parser.add_argument('--clean', action='store_true',
                       help='Clean invalid and single-use tags')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    try:
        manager = ObsidianTagManager(args.vault_path)
        
        if args.analyze:
            analysis = manager.analyze_tags()
            print(f"\n## Tag Analysis")
            print(f"Total unique tags: {analysis['total_unique_tags']}")
            print(f"Total tag uses: {analysis['total_tag_uses']}")
            print(f"\nMost common tags:")
            for tag, count in analysis['most_common'][:10]:
                print(f"  #{tag}: {count} uses")
                
        elif args.report:
            # Include advanced analysis if --advanced flag is set
            report_path = manager.export_tag_report(include_advanced=args.advanced)
            print(f"Tag report saved to: {report_path}")
            
        elif args.deduplicate:
            manager.interactive_deduplication()
            
        elif args.merge:
            result = manager.merge_tags(args.merge[0], args.merge[1], dry_run=args.dry_run)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"{'Would merge' if result['dry_run'] else 'Merged'} '#{result['old_tag']}' → '#{result['new_tag']}'")
                print(f"Files affected: {result['files_affected']}")
                
        elif args.clean:
            result = manager.clean_tags(remove_single_use=True, dry_run=args.dry_run)
            print(f"{'Would remove' if result['dry_run'] else 'Removed'} {result['tags_removed']} tags")
            print(f"Total occurrences: {result['occurrences_removed']}")
        
        else:
            parser.print_help()
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())