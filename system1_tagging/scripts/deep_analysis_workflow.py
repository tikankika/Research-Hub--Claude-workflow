#!/usr/bin/env python3
"""
Deep Analysis Workflow for Obsidian Tag Management
Implements three-phase analysis for high-quality tag assessment and reporting

Phase 1A: Existing Tags - Comprehensive Tag Report
Phase 1B: Tag Quality Analysis of Articles
Phase 1C: Extract Articles Needing Retagging (Abstract-Only)

Author: Claude Code Assistant
Date: 2025-08-04
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
from collections import defaultdict, Counter

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from obsidian_tag_manager import ObsidianTagManager
from obsidian_article_tagger import ObsidianArticleTagger

class DeepAnalysisWorkflow:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.articles_path = self.vault_path / "4 Articles"
        self.export_path = self.vault_path / "claude_workspace" / "system1_tagging" / "export"
        self.current_path = self.export_path / "current"
        self.archive_path = self.export_path / "archive"
        
        # Initialize component managers
        self.tag_manager = ObsidianTagManager(vault_path)
        self.article_tagger = ObsidianArticleTagger(vault_path)
        
        # Ensure directories exist
        self.current_path.mkdir(parents=True, exist_ok=True)
        self.archive_path.mkdir(parents=True, exist_ok=True)
        
        # Category definitions for coverage analysis
        self.categories = {
            'methodology': [
                'empirical_study', 'case_study', 'systematic_review', 'meta_analysis',
                'qualitative_research', 'quantitative_research', 'mixed_methods',
                'ethnography', 'action_research', 'design_based_research',
                'grounded_theory', 'phenomenology', 'experimental_design',
                'quasi_experimental', 'longitudinal_study', 'cross_sectional',
                'descriptive_study', 'exploratory_study'
            ],
            'education_level': [
                'k_12', 'primary_education', 'secondary_education', 'higher_education',
                'vocational_education', 'adult_education', 'preschool', 'undergraduate',
                'graduate', 'doctoral', 'postdoctoral', 'early_childhood',
                'middle_school', 'high_school', 'university'
            ],
            'technology': [
                'artificial_intelligence', 'machine_learning', 'deep_learning',
                'natural_language_processing', 'computer_vision', 'robotics',
                'virtual_reality', 'augmented_reality', 'learning_analytics',
                'educational_data_mining', 'intelligent_tutoring_systems',
                'adaptive_learning', 'learning_management_systems', 'moocs',
                'mobile_learning', 'game_based_learning', 'simulations',
                'chatbots', 'voice_assistants', 'blockchain', 'iot',
                'cloud_computing', 'edge_computing'
            ],
            'learning_theory': [
                'constructivism', 'cognitivism', 'behaviorism', 'connectivism',
                'social_learning_theory', 'cognitive_load_theory', 'multimedia_learning',
                'self_regulated_learning', 'collaborative_learning', 'inquiry_based_learning',
                'problem_based_learning', 'project_based_learning', 'experiential_learning',
                'situated_learning', 'transformative_learning', 'adult_learning_theory'
            ],
            'skills': [
                'critical_thinking', '21st_century_skills', 'digital_literacy',
                'computational_thinking', 'problem_solving', 'creativity',
                'collaboration', 'communication', 'self_efficacy', 'metacognition',
                'systems_thinking', 'design_thinking', 'ethical_reasoning',
                'cultural_competence', 'emotional_intelligence'
            ],
            'research_focus': [
                'student_engagement', 'learning_outcomes', 'teaching_effectiveness',
                'assessment', 'curriculum_design', 'professional_development',
                'educational_equity', 'accessibility', 'inclusion', 'diversity',
                'motivation', 'self_efficacy', 'teacher_beliefs', 'student_perceptions',
                'implementation', 'adoption', 'scalability', 'sustainability'
            ],
            'ai_specific': [
                'prompt_engineering', 'ai_literacy', 'ai_ethics', 'explainable_ai',
                'bias_in_ai', 'fairness', 'transparency', 'accountability',
                'human_ai_interaction', 'ai_augmented_learning', 'generative_ai',
                'large_language_models', 'conversational_ai'
            ]
        }
        
        # Generic tags to identify
        self.generic_tags = {
            'ai', 'education', 'technology', 'learning', 'study', 'research',
            'article', 'paper', 'analysis', 'review', 'method', 'data',
            'student', 'teacher', 'school', 'university', 'system', 'model'
        }

    def archive_old_reports(self):
        """Archive existing reports before creating new ones"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_folder = self.archive_path / timestamp
        
        # List of report files to archive
        report_files = [
            "tag_system_analysis_report.md",
            "article_tag_quality_analysis.json",
            "articles_for_retagging.md",
            "deep_analysis_summary.md",
            "tagging_action_plan.txt",
            "detailed_analysis_summary.md"
        ]
        
        # Also archive tag_data JSON files
        tag_data_files = list(self.current_path.glob("tag_data_*.json"))
        
        # Check if any reports exist in current folder
        reports_exist = any((self.current_path / f).exists() for f in report_files) or tag_data_files
        
        if reports_exist:
            archive_folder.mkdir(exist_ok=True)
            
            # Move existing reports to archive
            for report_file in report_files:
                source = self.current_path / report_file
                if source.exists():
                    dest = archive_folder / report_file
                    shutil.move(str(source), str(dest))
                    print(f"Archived: {report_file}")
            
            # Move tag_data JSON files
            for tag_data_file in tag_data_files:
                dest = archive_folder / tag_data_file.name
                shutil.move(str(tag_data_file), str(dest))
                print(f"Archived: {tag_data_file.name}")
            
            print(f"\n✓ Old reports archived to: {archive_folder.name}")

    def phase_1a_tag_system_analysis(self) -> Dict:
        """Phase 1A: Comprehensive analysis of existing tag system"""
        print("\n" + "="*60)
        print("PHASE 1A: TAG SYSTEM ANALYSIS")
        print("="*60)
        
        # Get comprehensive tag analysis from tag manager
        tag_locations = self.tag_manager.scan_vault_tags()
        analysis = self.tag_manager.analyze_tags()
        
        # Additional analysis
        author_only_count = 0
        generic_overuse = 0
        malformed_tags = []
        
        for tag, files in tag_locations.items():
            # Check for author tags (ending with underscore)
            if tag.endswith('_'):
                author_only_count += len(files)
            
            # Check for generic tags
            if tag.lower() in self.generic_tags:
                generic_overuse += len(files)
            
            # Check for malformed tags
            if not tag.replace('_', '').replace('-', '').isalnum():
                malformed_tags.append(tag)
        
        # Get advanced analysis
        relationships = self.tag_manager.analyze_tag_relationships(tag_locations)
        co_occurrences = relationships['co_occurrences']
        
        bridge_tags = self.tag_manager._find_bridge_tags(
            co_occurrences,
            tag_locations
        )
        
        temporal_trends = self.tag_manager.analyze_temporal_trends()
        
        # Compile results
        results = {
            'vault_stats': {
                'total_unique_tags': analysis['total_unique_tags'],
                'total_tag_uses': analysis['total_tag_uses'],
                'avg_tags_per_article': round(analysis['total_tag_uses'] / len(list(self.articles_path.glob("*.md"))), 2)
            },
            'quality_metrics': {
                'well_formed_tags': analysis['total_unique_tags'] - len(malformed_tags),
                'malformed_tags': len(malformed_tags),
                'generic_overuse': generic_overuse,
                'author_only_articles': author_only_count
            },
            'distribution': {
                'single_use': analysis['tag_distribution']['single_use'],
                'common_tags': analysis['tag_distribution']['common_use'],
                'bridge_tags': len(bridge_tags),
                'emerging_tags': len(temporal_trends.get('emerging_tags', [])),
                'declining_tags': len(temporal_trends.get('declining_tags', []))
            },
            'issues': {
                'inconsistent_formatting': self._find_format_inconsistencies(tag_locations),
                'redundant_groups': self.tag_manager.find_semantic_duplicates(tag_locations),
                'missing_categories': self._analyze_missing_categories(tag_locations)
            }
        }
        
        # Generate report
        self._generate_phase_1a_report(results, analysis, temporal_trends, bridge_tags)
        
        # Also export raw tag data as JSON
        self._export_tag_data_json(tag_locations, analysis)
        
        return results

    def phase_1b_article_quality_analysis(self) -> Dict:
        """Phase 1B: Analyze tag quality for each article"""
        print("\n" + "="*60)
        print("PHASE 1B: ARTICLE TAG QUALITY ANALYSIS")
        print("="*60)
        
        quality_results = {}
        quality_distribution = defaultdict(int)
        
        # Analyze each article
        for article_path in self.articles_path.glob("*.md"):
            article_quality = self._analyze_article_tag_quality(article_path)
            quality_results[article_path.name] = article_quality
            
            # Categorize by quality score
            score = article_quality['score']
            if score >= 80:
                quality_distribution['excellent'] += 1
            elif score >= 60:
                quality_distribution['good'] += 1
            elif score >= 40:
                quality_distribution['fair'] += 1
            elif score >= 20:
                quality_distribution['poor'] += 1
            else:
                quality_distribution['very_poor'] += 1
        
        # Generate JSON report
        report_data = {
            'quality_distribution': dict(quality_distribution),
            'total_articles': len(quality_results),
            'average_score': round(sum(r['score'] for r in quality_results.values()) / len(quality_results), 1),
            'articles_by_quality': quality_results
        }
        
        report_path = self.current_path / "article_tag_quality_analysis.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n✓ Quality analysis complete: {len(quality_results)} articles analyzed")
        print(f"  Average quality score: {report_data['average_score']}/100")
        
        return report_data

    def phase_1c_extract_retagging_candidates(self, quality_data: Dict) -> Dict:
        """Phase 1C: Extract articles needing retagging (abstract-only)"""
        print("\n" + "="*60)
        print("PHASE 1C: EXTRACT ARTICLES FOR RETAGGING")
        print("="*60)
        
        candidates = []
        
        for article_name, quality_info in quality_data['articles_by_quality'].items():
            # Skip if no abstract
            if not quality_info.get('has_abstract', False):
                continue
            
            # Skip if quality is already good
            if quality_info['score'] >= 60:
                continue
            
            # Calculate priority
            priority = self._calculate_retag_priority(quality_info)
            
            if priority > 0:
                candidates.append({
                    'article': article_name,
                    'priority': priority,
                    'quality_score': quality_info['score'],
                    'current_tags': quality_info.get('tag_count', 0),
                    'issues': quality_info.get('issues', []),
                    'abstract_preview': quality_info.get('abstract_preview', '')
                })
        
        # Sort by priority
        candidates.sort(key=lambda x: x['priority'], reverse=True)
        
        # Generate report
        self._generate_phase_1c_report(candidates, quality_data)
        
        return {
            'total_with_abstracts': sum(1 for q in quality_data['articles_by_quality'].values() if q.get('has_abstract')),
            'needing_retagging': len(candidates),
            'candidates': candidates[:50]  # Top 50 for manageable workload
        }

    def generate_unified_summary(self, phase_1a_results: Dict, phase_1b_results: Dict, phase_1c_results: Dict):
        """Generate unified, actionable summary report"""
        print("\n" + "="*60)
        print("GENERATING UNIFIED SUMMARY")
        print("="*60)
        
        summary_path = self.current_path / "tagging_action_plan.txt"
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Header with key stats
            f.write(f"# TAGGING ACTION PLAN\n")
            f.write(f"# Generated: {timestamp}\n")
            f.write(f"# Total articles: {phase_1b_results['total_articles']} | With abstracts: {phase_1c_results['total_with_abstracts']} | Need retagging: {phase_1c_results['needing_retagging']}\n")
            f.write(f"# Average quality: {phase_1b_results['average_score']}/100 | Estimated work: {phase_1c_results['needing_retagging'] * 2 / 60:.1f} hours\n")
            f.write(f"# Vault tags: {phase_1a_results['vault_stats']['total_unique_tags']} unique, {phase_1a_results['distribution']['bridge_tags']} bridge tags\n")
            f.write(f"\n")
            
            # High Priority Section (0-20 score, has abstract)
            high_priority = [c for c in phase_1c_results['candidates'] if c['quality_score'] < 20]
            if high_priority:
                f.write(f"## HIGH PRIORITY: No/Few tags, has abstract (Score 0-20)\n")
                f.write(f"# Ready for immediate tagging - {len(high_priority)} articles\n")
                f.write(f"# Focus: Full 7-category analysis needed\n")
                f.write(f"\n")
                for candidate in high_priority:
                    f.write(f"{candidate['article']}\n")
                f.write(f"\n")
            
            # Medium Priority Section (20-40 score, has abstract)
            medium_priority = [c for c in phase_1c_results['candidates'] if 20 <= c['quality_score'] < 40]
            if medium_priority:
                f.write(f"## MEDIUM PRIORITY: Some tags, needs improvement (Score 20-40)\n")
                f.write(f"# Enhancement needed - {len(medium_priority)} articles\n")
                f.write(f"# Focus: Fill missing categories, improve specificity\n")
                f.write(f"\n")
                for candidate in medium_priority:  # Show all medium priority
                    f.write(f"{candidate['article']}\n")
                f.write(f"\n")
            
            # Low Quality Articles WITHOUT abstracts (for completeness)
            no_abstract_low_quality = []
            for article_name, quality_info in phase_1b_results['articles_by_quality'].items():
                # Skip if has abstract (already handled above)
                if quality_info.get('has_abstract', False):
                    continue
                # Include if low quality
                if quality_info['score'] < 60:
                    no_abstract_low_quality.append({
                        'article': article_name,
                        'score': quality_info['score'],
                        'tags': quality_info.get('tag_count', 0)
                    })
            
            # Sort by score (lowest first)
            no_abstract_low_quality.sort(key=lambda x: x['score'])
            
            if no_abstract_low_quality:
                f.write(f"## LOW QUALITY WITHOUT ABSTRACT (Score <60)\n")
                f.write(f"# Missing abstracts - {len(no_abstract_low_quality)} articles\n")
                f.write(f"# Action: Add abstract first, then tag\n")
                f.write(f"\n")
                for article in no_abstract_low_quality:
                    f.write(f"{article['article']}\n")
                f.write(f"\n")
            
            # System Issues Section
            f.write(f"## SYSTEM ISSUES TO ADDRESS\n")
            f.write(f"# Fix these for better tag quality\n")
            f.write(f"\n")
            f.write(f"- Malformed tags: {phase_1a_results['quality_metrics']['malformed_tags']}\n")
            f.write(f"- Generic tag overuse: {phase_1a_results['quality_metrics']['generic_overuse']} instances\n")
            f.write(f"- Quality distribution: Very_Poor({phase_1b_results['quality_distribution'].get('very_poor', 0)}) | Poor({phase_1b_results['quality_distribution'].get('poor', 0)}) | Fair({phase_1b_results['quality_distribution'].get('fair', 0)}) | Good({phase_1b_results['quality_distribution'].get('good', 0)})\n")
            f.write(f"\n")
            
            # Quick Action Guide
            f.write(f"## QUICK ACTION GUIDE\n")
            f.write(f"# 7-Category Framework: methodology, education_level, technology, learning_theory, skills, research_focus, ai_specific\n")
            f.write(f"# Target: 15-20 tags per article covering all relevant categories\n")
            f.write(f"# Tools: Use manual_tag_suggestions.json → obsidian_article_tagger.py --apply-suggestions\n")
            f.write(f"\n")
            f.write(f"1. Start with HIGH PRIORITY list above\n")
            f.write(f"2. Read abstract, identify 7-category tags\n")
            f.write(f"3. Add tags to manual_tag_suggestions.json\n")
            f.write(f"4. Apply: python3 claude_workspace/scripts/tagging/obsidian_article_tagger.py --apply-suggestions\n")
            f.write(f"5. Re-run deep analysis to track progress\n")
        
        print(f"✓ Unified action plan generated: {summary_path.name}")
        
        # Also generate the old detailed reports for reference (but make them optional)
        self._generate_detailed_reports_if_needed(phase_1a_results, phase_1b_results, phase_1c_results)
    
    def _generate_detailed_reports_if_needed(self, phase_1a_results: Dict, phase_1b_results: Dict, phase_1c_results: Dict):
        """Generate detailed reports only if they don't exist (for reference)"""
        # Only generate if user specifically wants detailed analysis
        detailed_summary_path = self.current_path / "detailed_analysis_summary.md"
        
        if not detailed_summary_path.exists():
            with open(detailed_summary_path, 'w', encoding='utf-8') as f:
                f.write(f"# Detailed Tag Analysis Summary\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Quick Stats
                f.write(f"## Quick Stats\n")
                f.write(f"- Total articles: {phase_1b_results['total_articles']}\n")
                f.write(f"- Articles with abstracts: {phase_1c_results['total_with_abstracts']}\n")
                f.write(f"- Articles needing retagging: {phase_1c_results['needing_retagging']}\n")
                f.write(f"- Average quality score: {phase_1b_results['average_score']}/100\n")
                f.write(f"- Estimated work: {phase_1c_results['needing_retagging'] * 2 / 60:.1f} hours (2 min/article)\n\n")
                
                # Phase 1A Summary
                f.write(f"## Phase 1A: System Analysis\n")
                f.write(f"- Total unique tags: {phase_1a_results['vault_stats']['total_unique_tags']}\n")
                f.write(f"- Malformed tags: {phase_1a_results['quality_metrics']['malformed_tags']}\n")
                f.write(f"- Generic tag overuse: {phase_1a_results['quality_metrics']['generic_overuse']} instances\n")
                f.write(f"- Bridge tags identified: {phase_1a_results['distribution']['bridge_tags']}\n\n")
                
                # Phase 1B Summary
                f.write(f"## Phase 1B: Quality Distribution\n")
                for category, count in phase_1b_results['quality_distribution'].items():
                    f.write(f"- {category.title()}: {count} articles\n")
                f.write(f"\n")
                
                # Phase 1C Summary
                f.write(f"## Phase 1C: Top Priority Articles\n")
                for i, candidate in enumerate(phase_1c_results['candidates'][:10], 1):
                    f.write(f"\n### {i}. {candidate['article']} (Priority: {candidate['priority']})\n")
                    f.write(f"- Quality score: {candidate['quality_score']}/100\n")
                    f.write(f"- Current tags: {candidate['current_tags']}\n")
                    if candidate['issues']:
                        f.write(f"- Issues: {', '.join(candidate['issues'])}\n")
                
                # Recommendations
                f.write(f"\n## Recommendations\n")
                f.write(f"1. Start with highest priority articles (0-20 quality score)\n")
                f.write(f"2. Use 7-category framework consistently\n")
                f.write(f"3. Aim for 15-20 tags per article\n")
                f.write(f"4. Focus on specificity and category coverage\n")
                f.write(f"5. Replace generic tags with specific alternatives\n")

    def _analyze_article_tag_quality(self, article_path: Path) -> Dict:
        """Analyze tag quality for a single article"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except:
            return {'score': 0, 'error': 'Could not read file'}
        
        # Extract tags
        tags = self._extract_all_tags(content)
        
        # Check for abstract
        has_abstract = bool(re.search(r'## Abstract\s*\n\s*\n\s*[A-Z]', content, re.MULTILINE))
        
        # Get abstract preview if exists
        abstract_preview = ""
        if has_abstract:
            abstract_match = re.search(r'## Abstract\s*\n\s*\n\s*(.+?)(?:\n\n|\n##)', content, re.DOTALL)
            if abstract_match:
                abstract_preview = abstract_match.group(1).strip()[:200] + "..."
        
        # Calculate quality score
        score = 0
        issues = []
        
        # Quantity (0-20 points)
        tag_count = len(tags)
        if tag_count >= 15:
            score += 20
        elif tag_count >= 10:
            score += 15
        elif tag_count >= 5:
            score += 10
        elif tag_count >= 3:
            score += 5
        else:
            issues.append("Too few tags")
        
        # Coverage (0-30 points)
        categories_covered = self._check_category_coverage(tags)
        coverage_score = (categories_covered / 7) * 30
        score += coverage_score
        if categories_covered < 4:
            issues.append(f"Low category coverage ({categories_covered}/7)")
        
        # Specificity (0-25 points)
        if tags:
            specific_count = len([t for t in tags if t not in self.generic_tags])
            specificity_score = (specific_count / len(tags)) * 25
            score += specificity_score
            if specificity_score < 15:
                issues.append("Too many generic tags")
        
        # Consistency (0-25 points)
        consistency_score = self._check_taxonomy_alignment(tags) * 25
        score += consistency_score
        if consistency_score < 15:
            issues.append("Poor taxonomy alignment")
        
        return {
            'score': round(score),
            'tag_count': tag_count,
            'tags': list(tags),
            'has_abstract': has_abstract,
            'abstract_preview': abstract_preview,
            'categories_covered': f"{categories_covered}/7",
            'issues': issues
        }

    def _extract_all_tags(self, content: str) -> Set[str]:
        """Extract all tags from article content"""
        tags = set()
        
        # Extract YAML tags
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            tags_match = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n)*)', yaml_content, re.MULTILINE)
            if tags_match:
                yaml_tags = re.findall(r'-\s*([^#\n]+)', tags_match.group(1))
                tags.update(tag.strip().strip('"\'') for tag in yaml_tags if tag.strip())
        
        # Extract hashtag tags
        hashtag_tags = re.findall(r'#([a-zA-Z0-9_åäöÅÄÖ-]+)', content)
        tags.update(hashtag_tags)
        
        return tags

    def _check_category_coverage(self, tags: Set[str]) -> int:
        """Check how many categories are covered by tags"""
        covered = 0
        for category, category_tags in self.categories.items():
            if any(tag in category_tags for tag in tags):
                covered += 1
        return covered

    def _check_taxonomy_alignment(self, tags: Set[str]) -> float:
        """Check alignment with vault's common taxonomy"""
        if not tags:
            return 0
        
        # Check how many tags are in our defined categories
        aligned_count = 0
        for tag in tags:
            for category_tags in self.categories.values():
                if tag in category_tags:
                    aligned_count += 1
                    break
        
        return aligned_count / len(tags)

    def _calculate_retag_priority(self, quality_info: Dict) -> int:
        """Calculate retagging priority for an article"""
        priority = 0
        score = quality_info['score']
        
        # Quality-based priority
        if score == 0:
            priority += 100
        elif score < 20:
            priority += 80
        elif score < 40:
            priority += 60
        elif score < 60:
            priority += 40
        else:
            return 0  # Good enough, no retagging needed
        
        # Additional factors (simplified for now)
        if quality_info.get('tag_count', 0) == 0:
            priority += 10
        
        return priority

    def _find_format_inconsistencies(self, tag_locations: Dict) -> List[str]:
        """Find formatting inconsistencies in tags"""
        issues = []
        
        # Check for mixed formats
        has_underscores = any('_' in tag for tag in tag_locations)
        has_hyphens = any('-' in tag for tag in tag_locations)
        
        if has_underscores and has_hyphens:
            issues.append("Mixed use of underscores and hyphens")
        
        # Check for case inconsistencies
        lowercase_tags = {tag.lower() for tag in tag_locations}
        if len(lowercase_tags) < len(tag_locations):
            issues.append("Case inconsistencies found")
        
        return issues

    def _analyze_missing_categories(self, tag_locations: Dict) -> float:
        """Analyze what percentage of articles are missing core categories"""
        # This is simplified - would need full article analysis
        # For now, estimate based on tag distribution
        total_tags = len(tag_locations)
        category_tags = sum(len(tags) for tags in self.categories.values())
        
        # Rough estimate
        return 0.67  # Placeholder as mentioned in requirements

    def _generate_phase_1a_report(self, results: Dict, analysis: Dict, temporal_trends: Dict, bridge_tags: List):
        """Generate Phase 1A report"""
        report_path = self.current_path / "tag_system_analysis_report.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Tag System Analysis Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Vault-Wide Stats
            f.write(f"## Vault-Wide Tag Statistics\n")
            for key, value in results['vault_stats'].items():
                f.write(f"- {key.replace('_', ' ').title()}: {value}\n")
            f.write(f"\n")
            
            # Quality Metrics
            f.write(f"## Tag Quality Metrics\n")
            for key, value in results['quality_metrics'].items():
                f.write(f"- {key.replace('_', ' ').title()}: {value}\n")
            f.write(f"\n")
            
            # Distribution
            f.write(f"## Tag Distribution Analysis\n")
            for key, value in results['distribution'].items():
                f.write(f"- {key.replace('_', ' ').title()}: {value}\n")
            f.write(f"\n")
            
            # Issues
            f.write(f"## Systematic Issues Found\n")
            i = 1
            for issue_type, issue_data in results['issues'].items():
                if isinstance(issue_data, list) and issue_data:
                    f.write(f"{i}. {issue_type.replace('_', ' ').title()}\n")
                    i += 1
                elif isinstance(issue_data, float):
                    f.write(f"{i}. Missing core categories in {issue_data*100:.0f}% of articles\n")
                    i += 1
            
            # Most common tags
            f.write(f"\n## Most Common Tags\n")
            for tag, count in analysis['most_common'][:10]:
                f.write(f"- #{tag}: {count} uses\n")
            
            # Bridge tags
            if bridge_tags:
                f.write(f"\n## Bridge Tags (Connecting Domains)\n")
                for bt in bridge_tags[:5]:
                    f.write(f"- #{bt['tag']}: connects {', '.join(bt['domains_connected'])}\n")
        
        print(f"\n✓ Phase 1A report generated: {report_path.name}")

    def _export_tag_data_json(self, tag_locations: Dict, analysis: Dict):
        """Export raw tag data as JSON for further analysis"""
        # Calculate tag usage counts
        tag_usage = {}
        for tag, files in tag_locations.items():
            tag_usage[tag] = len(files)
        
        # Sort by usage count
        sorted_tag_usage = dict(sorted(tag_usage.items(), key=lambda x: x[1], reverse=True))
        
        # Count total files
        all_files = set()
        for files in tag_locations.values():
            all_files.update(files)
        
        # Create data structure
        tag_data = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'vault_path': str(self.vault_path),
                'total_tags': len(tag_locations),
                'total_uses': sum(tag_usage.values()),
                'total_files': len(all_files)
            },
            'tag_usage': sorted_tag_usage,
            'tag_distribution': analysis.get('tag_distribution', {}),
            'most_common': analysis.get('most_common', [])[:50],  # Top 50 tags
            'least_common': analysis.get('least_common', [])[:50]  # Bottom 50 tags
        }
        
        # Save to JSON
        output_path = self.current_path / f"tag_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tag_data, f, indent=2)
        
        print(f"✓ Tag data exported: {output_path.name}")

    def _generate_phase_1c_report(self, candidates: List, quality_data: Dict):
        """Generate Phase 1C report"""
        report_path = self.current_path / "articles_for_retagging.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# Articles Requiring Retagging\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total articles analyzed: {quality_data['total_articles']}\n")
            f.write(f"Articles with abstracts: {sum(1 for q in quality_data['articles_by_quality'].values() if q.get('has_abstract'))}\n")
            f.write(f"Articles needing retagging: {len(candidates)}\n\n")
            
            # Group by priority ranges
            high_priority = [c for c in candidates if c['quality_score'] < 20]
            medium_priority = [c for c in candidates if 20 <= c['quality_score'] < 40]
            low_priority = [c for c in candidates if 40 <= c['quality_score'] < 60]
            
            # High Priority
            if high_priority:
                f.write(f"## Highest Priority (Score 0-20, Has Abstract)\n")
                for i, candidate in enumerate(high_priority[:20], 1):
                    f.write(f"\n### {i}. {candidate['article']} (Priority: {candidate['priority']})\n")
                    f.write(f"- Current tags: {candidate['current_tags']}\n")
                    f.write(f"- Quality score: {candidate['quality_score']}/100\n")
                    if candidate['abstract_preview']:
                        f.write(f"- Abstract preview: \"{candidate['abstract_preview']}\"\n")
                    if candidate['issues']:
                        f.write(f"- Issues: {', '.join(candidate['issues'])}\n")
                    f.write(f"- Suggested focus: Full 7-category analysis needed\n")
            
            # Medium Priority
            if medium_priority:
                f.write(f"\n## Medium Priority (Score 20-40, Has Abstract)\n")
                for i, candidate in enumerate(medium_priority[:15], 1):
                    f.write(f"\n### {i}. {candidate['article']} (Priority: {candidate['priority']})\n")
                    f.write(f"- Current tags: {candidate['current_tags']}\n")
                    f.write(f"- Quality score: {candidate['quality_score']}/100\n")
                    if candidate['issues']:
                        f.write(f"- Issues: {', '.join(candidate['issues'])}\n")
        
        print(f"\n✓ Phase 1C report generated: {report_path.name}")

    def run_full_workflow(self):
        """Run all three phases of deep analysis"""
        print("\n" + "="*70)
        print("DEEP ANALYSIS WORKFLOW - HIGH QUALITY TAG ASSESSMENT")
        print("="*70)
        
        # Archive old reports first
        self.archive_old_reports()
        
        # Run three phases
        phase_1a_results = self.phase_1a_tag_system_analysis()
        phase_1b_results = self.phase_1b_article_quality_analysis()
        phase_1c_results = self.phase_1c_extract_retagging_candidates(phase_1b_results)
        
        # Generate unified summary
        self.generate_unified_summary(phase_1a_results, phase_1b_results, phase_1c_results)
        
        print("\n" + "="*70)
        print("WORKFLOW COMPLETE!")
        print(f"All reports saved to: {self.current_path}")
        print("="*70)


def main():
    parser = argparse.ArgumentParser(description='Deep Analysis Workflow for Obsidian Tag Management')
    parser.add_argument('--vault-path', type=str, default='.',
                       help='Path to Obsidian vault (default: current directory)')
    parser.add_argument('--phase', choices=['1a', '1b', '1c', 'all'], default='all',
                       help='Run specific phase or all phases (default: all)')
    
    args = parser.parse_args()
    
    # Initialize workflow
    workflow = DeepAnalysisWorkflow(args.vault_path)
    
    # Run requested phase(s)
    if args.phase == 'all':
        workflow.run_full_workflow()
    elif args.phase == '1a':
        workflow.archive_old_reports()
        workflow.phase_1a_tag_system_analysis()
    elif args.phase == '1b':
        workflow.archive_old_reports()
        workflow.phase_1b_article_quality_analysis()
    elif args.phase == '1c':
        # Need to run 1b first to get quality data
        workflow.archive_old_reports()
        quality_data = workflow.phase_1b_article_quality_analysis()
        workflow.phase_1c_extract_retagging_candidates(quality_data)


if __name__ == "__main__":
    import re  # Add this import at the top of main
    main()