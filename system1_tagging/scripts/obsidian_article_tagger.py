#!/usr/bin/env python3
"""
Obsidian Article Tagger with Claude Code Deep Analysis
Analyzes markdown articles and suggests intelligent tags using Claude's deep understanding
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
import argparse
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict

class ObsidianArticleTagger:
    def __init__(self, vault_path: str, target_dir: str = "4 Articles"):
        """Initialize with Obsidian vault path"""
        self.vault_path = Path(vault_path)
        self.target_dir = target_dir  # Target directory to analyze
        
        # Enhanced academic domains for deep analysis
        self.academic_domains = {
            'methodology': ['empirical_study', 'case_study', 'systematic_review', 'meta_analysis', 
                          'qualitative_research', 'quantitative_research', 'mixed_methods',
                          'ethnography', 'action_research', 'design_based_research', 'grounded_theory',
                          'phenomenology', 'experimental_design', 'quasi_experimental', 'longitudinal_study',
                          'cross_sectional', 'descriptive_study', 'exploratory_study', 'correlational_study'],
            'education_level': ['k_12', 'primary_education', 'secondary_education', 
                              'higher_education', 'vocational_education', 'adult_education',
                              'preschool', 'undergraduate', 'graduate', 'doctoral', 'postdoctoral',
                              'early_childhood', 'middle_school', 'high_school', 'university'],
            'technology': ['ai', 'artificial_intelligence', 'machine_learning', 'deep_learning',
                         'educational_technology', 'e_learning', 'online_learning', 'moocs',
                         'virtual_reality', 'augmented_reality', 'chatbots', 'llms', 'generative_ai',
                         'learning_analytics', 'data_mining', 'natural_language_processing',
                         'computer_vision', 'robotics', 'iot', 'blockchain', 'cloud_computing'],
            'learning_theory': ['constructivism', 'behaviorism', 'cognitivism', 'connectivism',
                              'social_learning_theory', 'experiential_learning', 'collaborative_learning',
                              'problem_based_learning', 'inquiry_based_learning', 'situated_learning',
                              'transformative_learning', 'activity_theory', 'sociocultural_theory',
                              'cognitive_load_theory', 'self_regulated_learning', 'metacognition'],
            'skills': ['critical_thinking', 'creativity', 'collaboration', 'communication',
                      'computational_thinking', 'digital_literacy', 'information_literacy',
                      'media_literacy', '21st_century_skills', 'problem_solving', 'systems_thinking',
                      'data_literacy', 'ai_literacy', 'ethical_reasoning', 'cultural_competence'],
            'research_focus': ['student_engagement', 'learning_outcomes', 'assessment', 'curriculum_design',
                             'teacher_education', 'professional_development', 'educational_equity',
                             'inclusive_education', 'special_education', 'stem_education', 'language_learning',
                             'literacy', 'numeracy', 'steam_education', 'educational_policy'],
            'ai_specific': ['prompt_engineering', 'ai_ethics', 'ai_bias', 'explainable_ai', 'human_ai_interaction',
                           'ai_literacy', 'responsible_ai', 'ai_governance', 'ai_safety', 'ai_alignment',
                           'machine_psychology', 'computational_creativity', 'ai_in_assessment'],
            'pedagogical_approach': ['flipped_classroom', 'blended_learning', 'gamification', 'game_based_learning',
                                   'project_based_learning', 'service_learning', 'peer_learning', 'self_directed_learning',
                                   'differentiated_instruction', 'universal_design_for_learning', 'culturally_responsive_teaching']
        }
        
        # Statistics tracking
        self.stats = {
            'total_analyzed': 0,
            'successfully_tagged': 0,
            'analysis_failed': 0,
            'already_tagged': 0,
            'tags_suggested': defaultdict(int)
        }
        
        # Batch processing progress tracking
        self.batch_progress_file = self.vault_path / Path(__file__).parent.parent / "export" / "batch_progress.json"
        self.batch_progress = self._load_batch_progress()
        
    def find_articles_without_tags(self, limit: int = None, main_dir_only: bool = True, require_abstract: bool = True) -> List[Path]:
        """Find markdown articles that don't have tags in the target directory"""
        untagged_articles = []
        
        # Search in the target directory (e.g., "4 Articles")
        target_path = self.vault_path / self.target_dir
        if not target_path.exists():
            print(f"Target directory not found: {target_path}")
            return []
        
        # Search markdown files based on main_dir_only setting
        if main_dir_only:
            # Only files directly in the target directory, not subdirectories
            md_files = [f for f in target_path.iterdir() if f.is_file() and f.suffix == '.md']
        else:
            # All files including subdirectories
            md_files = list(target_path.rglob('*.md'))
        
        # Sort files alphabetically to process in order
        md_files.sort(key=lambda f: f.name)
        
        for md_file in md_files:
            # Skip system files and indices
            if any(pattern in md_file.name.lower() for pattern in ['readme', 'index', '.obsidian']):
                continue
            
            # Check if article needs tags
            if not self._is_untagged(md_file):
                continue
            
            # If require_abstract is True, check if article has an abstract
            if require_abstract:
                if not self._has_abstract(md_file):
                    continue
            
            untagged_articles.append(md_file)
            if limit and len(untagged_articles) >= limit:
                break
        
        return untagged_articles
    
    def _has_abstract(self, file_path: Path) -> bool:
        """Check if article has an abstract section"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for abstract section with various patterns
            abstract_patterns = [
                r'^#+\s*Abstract',
                r'^Abstract:',
                r'^\*\*Abstract\*\*',
                r'^_Abstract_'
            ]
            
            for pattern in abstract_patterns:
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    # Check if there's actual content after the abstract heading
                    match = re.search(pattern + r'.*?\n(.+)', content, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                    if match and len(match.group(1).strip()) > 50:  # At least 50 chars of content
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking abstract in {file_path}: {e}")
            return False
    
    def _is_untagged(self, file_path: Path) -> bool:
        """Check if article has sufficient tags"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for hashtag patterns (Obsidian tags)
            hashtags = re.findall(r'#[\w_]+', content)
            
            # Check YAML frontmatter
            yaml_tags = []
            if content.startswith('---'):
                yaml_end = content.find('---', 3)
                if yaml_end > 0:
                    frontmatter = content[3:yaml_end]
                    tags_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter, re.DOTALL)
                    if tags_match:
                        tags_str = tags_match.group(1)
                        yaml_tags = [tag.strip().strip('"\'') for tag in tags_str.split(',')]
            
            all_tags = hashtags + [f"#{tag}" for tag in yaml_tags]
            
            # Filter out author tags, year tags, and navigation tags
            meaningful_tags = []
            for tag in all_tags:
                tag_clean = tag.lstrip('#').lower()
                # Skip author tags (multiple underscores suggest names)
                if tag_clean.count('_') >= 2 and any(part[0].isupper() for part in tag.split('_')):
                    continue
                # Skip year tags
                if re.match(r'^\d{4}$', tag_clean):
                    continue
                # Skip navigation/system tags
                if tag_clean in ['toc', 'index', 'navigation', 'meta']:
                    continue
                meaningful_tags.append(tag_clean)
            
            # Consider untagged if less than 3 meaningful tags
            return len(set(meaningful_tags)) < 3
            
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
    
    def extract_article_metadata(self, file_path: Path) -> Dict:
        """Extract comprehensive metadata from article for deep analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                'filename': file_path.name,
                'path': str(file_path),
                'relative_path': str(file_path.relative_to(self.vault_path)),
                'title': '',
                'authors': '',
                'year': '',
                'journal': '',
                'abstract': '',
                'keywords': [],
                'existing_tags': [],
                'full_text': content[:5000],  # First 5000 chars for context
                'methodology': '',
                'key_findings': '',
                'research_questions': '',
                'theoretical_framework': '',
                'implications': ''
            }
            
            # Extract title
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            else:
                # Try to extract from filename
                filename = file_path.stem
                # Handle various citation formats
                if '(' in filename and ')' in filename:
                    # Format: Authors (Year). Title
                    parts = filename.split(')', 1)
                    if len(parts) > 1:
                        metadata['title'] = parts[1].strip('. ')
                        author_year = parts[0] + ')'
                        if '(' in author_year:
                            metadata['authors'] = author_year.split('(')[0].strip()
                            metadata['year'] = author_year.split('(')[1].strip(')')
                else:
                    metadata['title'] = filename
            
            # Extract journal/conference from wikilinks
            journal_matches = re.findall(r'\[\[([^\]]+)\]\]', content[:2000])  # Check first part
            for match in journal_matches:
                if any(keyword in match.lower() for keyword in ['journal', 'conference', 'proceedings', 'transactions']):
                    metadata['journal'] = match
                    break
            
            # Extract abstract with multiple patterns
            abstract = self._extract_section(content, ['abstract', 'summary', 'overview'])
            metadata['abstract'] = abstract[:1500] if abstract else ''
            
            # Extract methodology
            methodology = self._extract_section(content, ['method', 'methodology', 'approach', 'design'])
            metadata['methodology'] = methodology[:500] if methodology else ''
            
            # Extract findings
            findings = self._extract_section(content, ['findings', 'results', 'conclusions'])
            metadata['key_findings'] = findings[:500] if findings else ''
            
            # Extract research questions
            rq = self._extract_section(content, ['research question', 'research questions', 'rq', 'objectives'])
            metadata['research_questions'] = rq[:300] if rq else ''
            
            # Extract theoretical framework
            theory = self._extract_section(content, ['theoretical', 'framework', 'theory', 'conceptual'])
            metadata['theoretical_framework'] = theory[:300] if theory else ''
            
            # Extract implications
            implications = self._extract_section(content, ['implications', 'discussion', 'practical applications'])
            metadata['implications'] = implications[:300] if implications else ''
            
            # Extract existing tags
            hashtags = re.findall(r'#[\w_]+', content)
            yaml_tags = self._extract_yaml_tags(content)
            metadata['existing_tags'] = list(set(hashtags + yaml_tags))
            
            # Extract keywords from various sections
            keywords = []
            for section in ['Key Concepts:', 'Keywords:', 'Key Terms:', 'Tags:']:
                keywords.extend(self._extract_keywords_from_section(content, section))
            metadata['keywords'] = list(set(keywords))
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return None
    
    def _extract_section(self, content: str, section_names: List[str]) -> str:
        """Extract content from a section with various heading patterns"""
        for section_name in section_names:
            # Try different heading patterns
            patterns = [
                rf'^#+\s*{section_name}.*?$',  # Markdown heading
                rf'^{section_name}:.*?$',       # Colon format
                rf'^\*\*{section_name}\*\*.*?$', # Bold format
                rf'^_{section_name}_.*?$'       # Italic format
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    start_pos = match.end()
                    # Find next section or end
                    next_section = re.search(r'^#+\s+', content[start_pos:], re.MULTILINE)
                    if next_section:
                        end_pos = start_pos + next_section.start()
                    else:
                        end_pos = min(start_pos + 2000, len(content))
                    
                    section_content = content[start_pos:end_pos].strip()
                    if len(section_content) > 50:  # Meaningful content
                        return section_content
        
        return ""
    
    def _extract_yaml_tags(self, content: str) -> List[str]:
        """Extract tags from YAML frontmatter"""
        tags = []
        if content.startswith('---'):
            yaml_end = content.find('---', 3)
            if yaml_end > 0:
                frontmatter = content[3:yaml_end]
                # Multiple formats for tags in YAML
                patterns = [
                    r'tags:\s*\[(.*?)\]',  # Array format
                    r'tags:\s*"([^"]+)"',  # Quoted string
                    r'tags:\s*\'([^\']+)\'',  # Single quoted
                    r'tags:\s*([^\n]+)'    # Plain string
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, frontmatter, re.DOTALL)
                    if match:
                        tags_str = match.group(1)
                        # Parse different formats
                        if ',' in tags_str:
                            tags = [tag.strip().strip('"\'') for tag in tags_str.split(',')]
                        else:
                            tags = [tags_str.strip().strip('"\'')]
                        break
        
        return [f"#{tag}" if not tag.startswith('#') else tag for tag in tags]
    
    def _extract_keywords_from_section(self, content: str, section_marker: str) -> List[str]:
        """Extract keywords from a specific section"""
        keywords = []
        section_start = content.find(section_marker)
        if section_start != -1:
            section_end = content.find('\n\n', section_start)
            if section_end == -1:
                section_end = section_start + 500
            
            section_text = content[section_start:section_end]
            # Extract hashtags
            keywords.extend(re.findall(r'#[\w_]+', section_text))
            # Extract comma-separated keywords
            if ':' in section_text:
                after_colon = section_text.split(':', 1)[1]
                if ',' in after_colon:
                    keywords.extend([k.strip() for k in after_colon.split(',') if len(k.strip()) > 2])
        
        return keywords
    
    def load_existing_tags(self) -> Dict[str, int]:
        """Load existing tags from the latest tag data export"""
        export_dir = self.vault_path / Path(__file__).parent.parent / "export"
        if not export_dir.exists():
            return {}
        
        # Find the most recent tag data file
        tag_files = list(export_dir.glob("tag_data_*.json"))
        if not tag_files:
            return {}
        
        latest_file = max(tag_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('tag_usage', {})
        except Exception as e:
            print(f"Warning: Could not load existing tags from {latest_file}: {e}")
            return {}
    
    def analyze_with_claude(self, metadata: Dict, save_suggestion: bool = True) -> List[str]:
        """Deep analysis with Claude to suggest contextually appropriate tags"""
        # Load existing tags for context
        existing_vault_tags = self.load_existing_tags()
        
        # Prepare comprehensive analysis prompt
        prompt = self._create_deep_analysis_prompt(metadata, existing_vault_tags)
        
        print(f"\n{'='*60}")
        print(f"DEEP ANALYSIS: {metadata['filename']}")
        print(f"Title: {metadata['title'][:80]}...")
        print(f"Path: {metadata['relative_path']}")
        
        if metadata['abstract']:
            print(f"\nAbstract Preview:")
            print(f"{metadata['abstract'][:200]}...")
        
        if metadata['methodology']:
            print(f"\nMethodology detected: {metadata['methodology'][:100]}...")
        
        print(f"\nExisting tags in article: {', '.join(metadata['existing_tags'][:10])}")
        print(f"\nPreparing deep analysis with Claude...")
        print(f"{'='*60}\n")
        
        # This is where Claude performs deep analysis
        # The prompt includes full context for intelligent tagging
        
        # Claude will analyze the article and suggest tags
        suggested_tags = []
        
        # First check if we have manual suggestions for this article
        manual_suggestions = self._load_manual_suggestions()
        if metadata['filename'] in manual_suggestions:
            suggested_tags = manual_suggestions[metadata['filename']]
            print(f"✅ Found manual tag suggestions: {', '.join(suggested_tags)}")
        else:
            # Use Claude to analyze and suggest tags
            print("🤖 Asking Claude to analyze the article and suggest tags...")
            
            # Based on the metadata, Claude should suggest appropriate tags
            # The actual tags will be determined by Claude based on:
            # - Abstract content
            # - Title and keywords
            # - Methodology and findings
            # - Existing vault tags for consistency
            
            # For now, return empty list if no manual suggestions
            # Claude will provide tags based on the deep analysis prompt
            pass
        
        # Save the suggestion for later review/application
        if save_suggestion and suggested_tags:
            self._save_tag_suggestion(metadata, suggested_tags, prompt)
        
        return suggested_tags
    
    def _load_manual_suggestions(self) -> Dict[str, List[str]]:
        """Load manual tag suggestions from a JSON file"""
        suggestions_file = self.vault_path / "claude_workspace" / "system1_tagging" / "manual_tag_suggestions.json"
        if suggestions_file.exists():
            try:
                with open(suggestions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load manual suggestions: {e}")
        return {}
    
    def _save_tag_suggestion(self, metadata: Dict, suggested_tags: List[str], prompt: str):
        """Save tag suggestion to export folder for later review/application"""
        # Create suggestions directory
        suggestions_dir = self.vault_path / Path(__file__).parent.parent / "export" / "tag_suggestions"
        suggestions_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamp-based filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"suggestion_{timestamp}_{Path(metadata['filename']).stem[:50]}.json"
        
        # Prepare suggestion data
        suggestion_data = {
            "timestamp": datetime.now().isoformat(),
            "file_path": metadata['path'],
            "filename": metadata['filename'],
            "title": metadata['title'],
            "existing_tags": metadata['existing_tags'],
            "suggested_tags": suggested_tags,
            "metadata": {
                "abstract": metadata['abstract'][:500] if metadata['abstract'] else "",
                "authors": metadata['authors'],
                "year": metadata['year'],
                "journal": metadata['journal']
            },
            "analysis_prompt": prompt[:1000]  # Save first 1000 chars of prompt
        }
        
        # Save to JSON file
        suggestion_path = suggestions_dir / filename
        with open(suggestion_path, 'w', encoding='utf-8') as f:
            json.dump(suggestion_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Suggestion saved to: {suggestion_path.relative_to(self.vault_path)}")
    
    def _create_deep_analysis_prompt(self, metadata: Dict, existing_vault_tags: Dict[str, int]) -> str:
        """Create comprehensive prompt for Claude's deep analysis"""
        # Get top existing tags for reference
        top_tags = sorted(existing_vault_tags.items(), key=lambda x: x[1], reverse=True)[:50]
        common_tags = [tag for tag, count in top_tags if count >= 5]
        
        prompt = f"""Perform a DEEP ANALYSIS of this academic article and suggest 5-8 highly specific, contextually appropriate tags.

ARTICLE METADATA:
Title: {metadata['title']}
Authors: {metadata['authors']}
Year: {metadata['year']}
Journal/Conference: {metadata['journal']}
File Path: {metadata['relative_path']}

ABSTRACT:
{metadata['abstract']}

METHODOLOGY (if detected):
{metadata['methodology']}

KEY FINDINGS (if detected):
{metadata['key_findings']}

RESEARCH QUESTIONS (if detected):
{metadata['research_questions']}

THEORETICAL FRAMEWORK (if detected):
{metadata['theoretical_framework']}

IMPLICATIONS (if detected):
{metadata['implications']}

EXISTING KEYWORDS IN ARTICLE:
{', '.join(metadata['keywords'])}

EXISTING TAGS IN ARTICLE:
{', '.join([tag.lstrip('#') for tag in metadata['existing_tags']])}

COMMONLY USED TAGS IN THIS VAULT (for consistency):
{', '.join(common_tags[:30])}

FULL TEXT EXCERPT (first 2000 chars for context):
{metadata['full_text'][:2000]}

ANALYSIS INSTRUCTIONS:
1. Identify the PRIMARY RESEARCH DOMAIN and theoretical perspective
2. Determine the SPECIFIC METHODOLOGY (not just "empirical study" but e.g., "quasi_experimental", "grounded_theory", "design_based_research")
3. Extract KEY CONCEPTS that are central to the paper (not peripheral mentions)
4. Identify the TARGET POPULATION or educational level (e.g., "k_12", "higher_education", "teacher_education")
5. Note any SPECIFIC TECHNOLOGIES or AI approaches discussed (e.g., "chatgpt", "learning_analytics", "intelligent_tutoring_systems")
6. Consider PEDAGOGICAL APPROACHES if mentioned (e.g., "collaborative_learning", "problem_based_learning")
7. Look for CROSS-CUTTING THEMES (e.g., "ai_ethics", "educational_equity", "assessment")

IMPORTANT GUIDELINES:
- Use existing vault tags when appropriate for consistency
- All tags must be lowercase with underscores (e.g., "machine_learning" not "Machine Learning")
- Be SPECIFIC - prefer "systematic_review" over "review", "k_12" over "education"
- Avoid overly generic tags like "research", "study", "paper", "analysis"
- Consider the paper's contribution to the field when selecting tags
- If the paper is about AI in education, include relevant AI-specific tags

Return ONLY a Python list of 5-8 tag strings. Example:
["learning_analytics", "higher_education", "predictive_modeling", "student_retention", "machine_learning", "systematic_review"]"""
        
        return prompt
    
    def apply_tags_to_article(self, file_path: Path, tags: List[str], replace_mode: bool = True) -> bool:
        """Apply tags to article - either replacing existing tags or appending"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert tags to hashtags
            hashtags = [f"#{tag}" for tag in tags]
            tag_line = ', '.join(hashtags)
            
            if replace_mode:
                # Remove existing hashtags from the content (except in code blocks)
                # This preserves author tags and other structured content
                lines = content.split('\n')
                cleaned_lines = []
                in_code_block = False
                
                for line in lines:
                    # Track code blocks
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                    
                    if not in_code_block and not line.strip().startswith('##'):  # Not a heading
                        # Remove standalone hashtags but preserve author tags (e.g., #Smith_J)
                        # Only remove tags that are likely subject tags
                        cleaned_line = re.sub(r'#(?![\w]+_[\w]+)[\w_]+(?:\s*,\s*)?', '', line)
                        # Clean up any leftover commas and spaces
                        cleaned_line = re.sub(r',\s*,', ',', cleaned_line)
                        cleaned_line = re.sub(r'^\s*,\s*|\s*,\s*$', '', cleaned_line)
                        cleaned_lines.append(cleaned_line)
                    else:
                        cleaned_lines.append(line)
                
                lines = cleaned_lines
            else:
                lines = content.split('\n')
            
            # Find or create tags section
            tag_section_index = None
            
            # Look for existing tags section
            for i, line in enumerate(lines):
                if re.match(r'^#+\s*Tags', line, re.IGNORECASE):
                    tag_section_index = i
                    break
            
            if tag_section_index is not None:
                if replace_mode:
                    # Replace content in tags section
                    # Find the extent of the tags section
                    section_end = tag_section_index + 1
                    while section_end < len(lines) and lines[section_end].strip() and not lines[section_end].startswith('#'):
                        section_end += 1
                    
                    # Remove old tags content (but keep the heading)
                    del lines[tag_section_index + 1:section_end]
                    
                    # Insert new tags
                    lines.insert(tag_section_index + 1, '')
                    lines.insert(tag_section_index + 2, tag_line)
                else:
                    # Append mode - add to existing tags
                    insert_index = tag_section_index + 1
                    while insert_index < len(lines) and lines[insert_index].strip() and not lines[insert_index].startswith('#'):
                        insert_index += 1
                    
                    if insert_index < len(lines) and lines[insert_index - 1].strip():
                        lines.insert(insert_index, '')
                    lines.insert(insert_index + 1, tag_line)
            else:
                # Create new tags section at end of file
                if lines[-1].strip():
                    lines.append('')
                lines.append('## Tags')
                lines.append('')
                lines.append(tag_line)
            
            # Add metadata about tagging
            lines.append('')
            if replace_mode:
                lines.append(f'*Tags updated by Claude on {datetime.now().strftime("%Y-%m-%d")} (replaced existing tags)*')
            else:
                lines.append(f'*Tags added by Claude on {datetime.now().strftime("%Y-%m-%d")}*')
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            return True
            
        except Exception as e:
            print(f"Error applying tags to {file_path}: {e}")
            return False
    
    def deep_analysis_session(self, limit: int = 1, auto_apply: bool = False, replace_mode: bool = True):
        """Run deep analysis tagging session - one article at a time"""
        print(f"\n🔍 DEEP ANALYSIS MODE - Obsidian Article Tagger")
        print(f"{'='*60}")
        print(f"Analyzing articles in '{self.target_dir}' directory (main directory only)")
        print(f"Filtering: Articles must have abstracts")
        print(f"Processing {limit} article(s) at a time for thorough analysis\n")
        
        # Load existing tags
        existing_tags = self.load_existing_tags()
        print(f"Loaded {len(existing_tags)} existing tags from vault")
        
        # Find untagged articles with abstracts in main directory only
        print(f"\nSearching for articles with abstracts that need tags...")
        untagged = self.find_articles_without_tags(limit=limit, main_dir_only=True, require_abstract=True)
        
        if not untagged:
            print("All articles are already sufficiently tagged!")
            return
        
        print(f"Found {len(untagged)} article(s) to analyze")
        
        # Process one at a time for deep analysis
        for i, article_path in enumerate(untagged, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(untagged)}] ANALYZING: {article_path.name}")
            print(f"{'='*60}")
            
            # Extract comprehensive metadata
            print("Extracting metadata...")
            metadata = self.extract_article_metadata(article_path)
            if not metadata:
                print("❌ Failed to extract metadata, skipping...")
                self.stats['analysis_failed'] += 1
                continue
            
            self.stats['total_analyzed'] += 1
            
            # Check if already has some tags
            existing_article_tags = len([t for t in metadata['existing_tags'] 
                                       if not t.lstrip('#').count('_') >= 2])  # Filter author tags
            if existing_article_tags > 0:
                print(f"ℹ️  Article already has {existing_article_tags} tags")
                self.stats['already_tagged'] += 1
            
            # Perform deep analysis with Claude
            print("\n🤖 Sending to Claude for deep analysis...")
            suggested_tags = self.analyze_with_claude(metadata)
            
            if suggested_tags:
                print(f"\n✅ Claude suggests these tags:")
                for tag in suggested_tags:
                    count = existing_tags.get(tag, 0)
                    print(f"   - {tag} (used {count} times in vault)")
                
                # Update stats
                for tag in suggested_tags:
                    self.stats['tags_suggested'][tag] += 1
                
                if auto_apply:
                    if replace_mode:
                        print(f"\n📝 Replacing existing tags in article...")
                    else:
                        print(f"\n📝 Appending tags to article...")
                    success = self.apply_tags_to_article(article_path, suggested_tags, replace_mode=replace_mode)
                    if success:
                        self.stats['successfully_tagged'] += 1
                        print("✅ Tags applied successfully!")
                    else:
                        print("❌ Failed to apply tags")
                else:
                    print("\n💡 Tags suggested but not applied (use --auto-apply to apply automatically)")
            else:
                print("❌ No tags suggested by Claude")
            
            # Pause between articles for rate limiting
            if i < len(untagged):
                print(f"\n⏳ Pausing before next article...")
                import time
                time.sleep(2)
        
        # Generate report
        self._generate_session_report()
    
    def _generate_session_report(self):
        """Generate a report of the tagging session"""
        print(f"\n{'='*60}")
        print(f"📊 DEEP ANALYSIS SESSION REPORT")
        print(f"{'='*60}")
        print(f"Total articles analyzed: {self.stats['total_analyzed']}")
        print(f"Successfully tagged: {self.stats['successfully_tagged']}")
        print(f"Already had tags: {self.stats['already_tagged']}")
        print(f"Analysis failed: {self.stats['analysis_failed']}")
        
        if self.stats['tags_suggested']:
            print(f"\n🏷️  Most suggested tags:")
            top_tags = sorted(self.stats['tags_suggested'].items(), 
                            key=lambda x: x[1], reverse=True)[:10]
            for tag, count in top_tags:
                print(f"   - {tag}: {count} times")
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.vault_path / Path(__file__).parent.parent / "export" / f"deep_analysis_report_{timestamp}.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Deep Analysis Tagging Report\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Statistics:\n")
            for key, value in self.stats.items():
                if key != 'tags_suggested':
                    f.write(f"  {key}: {value}\n")
            
            if self.stats['tags_suggested']:
                f.write(f"\nTags Suggested:\n")
                for tag, count in sorted(self.stats['tags_suggested'].items()):
                    f.write(f"  {tag}: {count}\n")
        
        print(f"\n📄 Report saved to: {report_path.relative_to(self.vault_path)}")
    
    def _load_batch_progress(self) -> Dict:
        """Load batch processing progress from file"""
        if self.batch_progress_file.exists():
            try:
                with open(self.batch_progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            'processed_files': [],
            'last_run': None,
            'total_processed': 0
        }
    
    def _save_batch_progress(self):
        """Save batch processing progress to file"""
        self.batch_progress_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.batch_progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.batch_progress, f, indent=2)
    
    def reset_batch_progress(self):
        """Reset batch processing progress"""
        self.batch_progress = {
            'processed_files': [],
            'last_run': None,
            'total_processed': 0
        }
        self._save_batch_progress()
        print("✅ Batch progress reset successfully")
    
    def apply_saved_suggestions(self, suggestions_file: str = None):
        """Apply saved tag suggestions from JSON files"""
        suggestions_dir = self.vault_path / Path(__file__).parent.parent / "export" / "tag_suggestions"
        manual_suggestions_file = self.vault_path / "claude_workspace" / "system1_tagging" / "manual_tag_suggestions.json"
        
        if suggestions_file:
            # Apply specific suggestion file
            suggestion_path = suggestions_dir / suggestions_file
            if not suggestion_path.exists():
                print(f"❌ Suggestion file not found: {suggestion_path}")
                return
            
            with open(suggestion_path, 'r', encoding='utf-8') as f:
                suggestion = json.load(f)
            
            self._apply_single_suggestion(suggestion)
        else:
            # First check and apply manual_tag_suggestions.json
            if manual_suggestions_file.exists():
                print(f"📋 Applying tags from manual_tag_suggestions.json...")
                self._apply_manual_suggestions_from_file()
                return
            
            # Otherwise apply all pending individual suggestions
            pending_files = list(suggestions_dir.glob("suggestion_*.json"))
            if not pending_files:
                print("No pending suggestions found.")
                return
            
            print(f"\nFound {len(pending_files)} pending suggestions:")
            for i, file in enumerate(pending_files, 1):
                print(f"\n[{i}/{len(pending_files)}] Processing {file.name}")
                with open(file, 'r', encoding='utf-8') as f:
                    suggestion = json.load(f)
                self._apply_single_suggestion(suggestion)
    
    def _apply_single_suggestion(self, suggestion: Dict):
        """Apply a single tag suggestion"""
        file_path = Path(suggestion['file_path'])
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        print(f"\n📄 Article: {suggestion['title'][:80]}...")
        print(f"📁 Path: {suggestion['filename']}")
        print(f"🏷️  Suggested tags: {', '.join(suggestion['suggested_tags'])}")
        
        # Apply the tags
        success = self.apply_tags_to_article(file_path, suggestion['suggested_tags'], replace_mode=True)
        if success:
            print("✅ Tags applied successfully!")
            # Archive the processed suggestion
            self._archive_suggestion(suggestion)
        else:
            print("❌ Failed to apply tags")
    
    def _archive_suggestion(self, suggestion: Dict):
        """Move processed suggestion to archive"""
        suggestions_dir = self.vault_path / Path(__file__).parent.parent / "export" / "tag_suggestions"
        archive_dir = suggestions_dir / "applied"
        archive_dir.mkdir(exist_ok=True)
        
        # Find the original file
        for file in suggestions_dir.glob("suggestion_*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data['file_path'] == suggestion['file_path']:
                # Move to archive
                archive_path = archive_dir / file.name
                file.rename(archive_path)
                print(f"📁 Suggestion archived to: {archive_path.relative_to(self.vault_path)}")
                break
    
    def _apply_manual_suggestions_from_file(self):
        """Apply all suggestions from manual_tag_suggestions.json"""
        manual_suggestions = self._load_manual_suggestions()
        if not manual_suggestions:
            print("No manual suggestions found.")
            return
        
        print(f"\n📋 Found {len(manual_suggestions)} articles with tag suggestions\n")
        
        success_count = 0
        failed_count = 0
        
        for filename, tags in manual_suggestions.items():
            print(f"\n[{success_count + failed_count + 1}/{len(manual_suggestions)}] Processing: {filename[:80]}...")
            
            # Find the article file
            article_path = None
            
            # Try exact match first
            exact_path = self.vault_path / "4 Articles" / filename
            if exact_path.exists():
                article_path = exact_path
            else:
                # Try without newlines in filename
                clean_filename = filename.replace('\n', ' ')
                clean_path = self.vault_path / "4 Articles" / clean_filename
                if clean_path.exists():
                    article_path = clean_path
                else:
                    # Search for partial match
                    for file_path in (self.vault_path / "4 Articles").glob("*.md"):
                        if clean_filename in str(file_path) or filename.replace('\n', '') in str(file_path):
                            article_path = file_path
                            break
            
            if not article_path:
                print(f"❌ File not found: {filename}")
                failed_count += 1
                continue
            
            print(f"📄 Found: {article_path.name}")
            print(f"🏷️  Tags to apply: {', '.join(tags)}")
            
            # Apply tags
            if self.apply_tags_to_article(article_path, tags, replace_mode=True):
                print("✅ Tags applied successfully!")
                success_count += 1
            else:
                print("❌ Failed to apply tags")
                failed_count += 1
        
        print(f"\n{'='*60}")
        print(f"📊 SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successfully tagged: {success_count} articles")
        print(f"❌ Failed: {failed_count} articles")
        print(f"{'='*60}\n")
    
    def batch_analysis_session(self, limit: int = 20):
        """Run batch analysis - process multiple articles without stopping for confirmation"""
        print(f"\n🚀 BATCH ANALYSIS MODE - Processing {limit} articles automatically")
        print(f"{'='*60}")
        print(f"This mode will:")
        print(f"  1. Process {limit} articles without stopping")
        print(f"  2. Save all suggestions to tag_suggestions/")
        print(f"  3. Skip already processed files")
        print(f"  4. Allow you to review and apply tags later")
        print(f"{'='*60}\n")
        
        # Load existing tags for consistency
        existing_tags = self.load_existing_tags()
        print(f"Loaded {len(existing_tags)} existing tags from vault")
        
        # Find untagged articles
        untagged = self.find_articles_without_tags(main_dir_only=True, require_abstract=True)
        
        # Filter out already processed files
        remaining = [f for f in untagged if str(f) not in self.batch_progress['processed_files']]
        
        if not remaining:
            print("\n✅ All articles have been processed in batch mode!")
            print(f"Total processed: {self.batch_progress['total_processed']} articles")
            print("\n💡 Use --review to review and apply the suggestions")
            print("💡 Use --reset-progress to start batch processing from beginning")
            return
        
        print(f"\nFound {len(remaining)} unprocessed articles (out of {len(untagged)} total)")
        articles_to_process = remaining[:limit]
        
        print(f"\n🔄 Processing {len(articles_to_process)} articles in batch mode...\n")
        
        # Update progress
        self.batch_progress['last_run'] = datetime.now().isoformat()
        
        for i, article in enumerate(articles_to_process, 1):
            print(f"\n[{i}/{len(articles_to_process)}] Analyzing: {article.name[:60]}...")
            
            try:
                # Extract metadata
                metadata = self.extract_article_metadata(article)
                
                # Generate tags using keyword matching (no Claude in batch mode for speed)
                suggested_tags = self.suggest_tags_by_keywords(metadata)
                
                if suggested_tags:
                    # Save suggestion
                    suggestion = {
                        'file_path': str(article),
                        'filename': article.name,
                        'title': metadata['title'],
                        'suggested_tags': suggested_tags,
                        'metadata': metadata,
                        'timestamp': datetime.now().isoformat(),
                        'batch_mode': True
                    }
                    
                    # Save to individual file
                    suggestions_dir = self.vault_path / Path(__file__).parent.parent / "export" / "tag_suggestions"
                    suggestions_dir.mkdir(parents=True, exist_ok=True)
                    
                    safe_title = re.sub(r'[^\w\s-]', '', metadata['title'])[:50]
                    suggestion_file = suggestions_dir / f"suggestion_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_title}.json"
                    
                    with open(suggestion_file, 'w', encoding='utf-8') as f:
                        json.dump(suggestion, f, indent=2, ensure_ascii=False)
                    
                    print(f"✅ Suggested {len(suggested_tags)} tags: {', '.join(suggested_tags[:5])}...")
                    
                    # Update stats
                    self.stats['total_analyzed'] += 1
                    for tag in suggested_tags:
                        self.stats['tags_suggested'][tag] += 1
                else:
                    print(f"⚠️  No tags suggested for this article")
                
                # Mark as processed
                self.batch_progress['processed_files'].append(str(article))
                self.batch_progress['total_processed'] += 1
                
            except Exception as e:
                print(f"❌ Error processing article: {e}")
                self.stats['analysis_failed'] += 1
            
            # Save progress after each article
            self._save_batch_progress()
        
        # Generate final report
        print(f"\n{'='*60}")
        print(f"📊 BATCH PROCESSING COMPLETE")
        print(f"{'='*60}")
        print(f"Processed in this session: {len(articles_to_process)} articles")
        print(f"Total processed overall: {self.batch_progress['total_processed']} articles")
        print(f"Suggestions saved to: system1_tagging/export/tag_suggestions/")
        print(f"\n💡 Next steps:")
        print(f"   1. Use --review to interactively review suggestions")
        print(f"   2. Use --apply-suggestions to apply all at once")
        print(f"   3. Continue batch processing with --batch")
    
    def review_suggestions(self):
        """Interactive review of saved suggestions"""
        suggestions_dir = self.vault_path / Path(__file__).parent.parent / "export" / "tag_suggestions"
        pending_files = list(suggestions_dir.glob("suggestion_*.json"))
        
        if not pending_files:
            print("No pending suggestions to review.")
            return
        
        print(f"\n📋 REVIEW MODE - {len(pending_files)} suggestions to review")
        print(f"{'='*60}")
        print("Commands: [a]pply, [s]kip, [d]elete suggestion, [e]dit tags, [q]uit\n")
        
        applied_count = 0
        skipped_count = 0
        deleted_count = 0
        
        for i, file in enumerate(sorted(pending_files), 1):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    suggestion = json.load(f)
                
                print(f"\n[{i}/{len(pending_files)}] Article: {suggestion['title'][:80]}...")
                print(f"File: {suggestion['filename']}")
                print(f"Suggested tags: {', '.join(suggestion['suggested_tags'])}")
                
                if 'batch_mode' in suggestion and suggestion['batch_mode']:
                    print("📝 Note: Generated in batch mode (keyword matching)")
                
                while True:
                    choice = input("\nAction ([a]pply/[s]kip/[d]elete/[e]dit/[q]uit): ").lower().strip()
                    
                    if choice == 'a':
                        # Apply tags
                        file_path = Path(suggestion['file_path'])
                        if self.apply_tags_to_article(file_path, suggestion['suggested_tags'], replace_mode=True):
                            print("✅ Tags applied!")
                            applied_count += 1
                            self._archive_suggestion(suggestion)
                        else:
                            print("❌ Failed to apply tags")
                        break
                    
                    elif choice == 's':
                        print("⏭️  Skipped")
                        skipped_count += 1
                        break
                    
                    elif choice == 'd':
                        file.unlink()
                        print("🗑️  Suggestion deleted")
                        deleted_count += 1
                        break
                    
                    elif choice == 'e':
                        print("\nCurrent tags:", ', '.join(suggestion['suggested_tags']))
                        new_tags_str = input("Enter new tags (comma-separated): ").strip()
                        if new_tags_str:
                            new_tags = [t.strip() for t in new_tags_str.split(',') if t.strip()]
                            suggestion['suggested_tags'] = new_tags
                            # Save updated suggestion
                            with open(file, 'w', encoding='utf-8') as f:
                                json.dump(suggestion, f, indent=2, ensure_ascii=False)
                            print("✏️  Tags updated")
                            continue
                    
                    elif choice == 'q':
                        print("\n👋 Exiting review mode")
                        break
                    
                    else:
                        print("Invalid choice. Please enter a, s, d, e, or q.")
                
                if choice == 'q':
                    break
                    
            except Exception as e:
                print(f"❌ Error processing suggestion: {e}")
                continue
        
        print(f"\n{'='*60}")
        print(f"📊 REVIEW SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Applied: {applied_count}")
        print(f"⏭️  Skipped: {skipped_count}")
        print(f"🗑️  Deleted: {deleted_count}")
        print(f"📋 Remaining: {len(pending_files) - applied_count - deleted_count}")
        print(f"{'='*60}\n")

def main():
    parser = argparse.ArgumentParser(
        description='Deep Analysis Article Tagger - Uses Claude to analyze and tag articles',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze one article at a time (default)
  python obsidian_article_tagger.py
  
  # Analyze 5 articles
  python obsidian_article_tagger.py --limit 5
  
  # Auto-apply suggested tags
  python obsidian_article_tagger.py --auto-apply
  
  # BATCH MODE (NEW): Process 50 articles automatically
  python obsidian_article_tagger.py --batch --limit 50
  
  # Review batch suggestions interactively
  python obsidian_article_tagger.py --review
  
  # Apply all suggestions at once
  python obsidian_article_tagger.py --apply-suggestions
  
  # Reset batch progress and start over
  python obsidian_article_tagger.py --reset-progress
  
  # Analyze articles in a different directory
  python obsidian_article_tagger.py --target-dir "5 Methods"
  
  # Just find untagged articles
  python obsidian_article_tagger.py --find-untagged
        """
    )
    parser.add_argument('--vault-path', default='.',
                       help='Path to Obsidian vault (default: current directory)')
    parser.add_argument('--target-dir', default='4 Articles',
                       help='Target directory to analyze (default: 4 Articles)')
    parser.add_argument('--limit', type=int, default=1,
                       help='Number of articles to process (default: 1 for deep analysis)')
    parser.add_argument('--auto-apply', action='store_true',
                       help='Automatically apply suggested tags without confirmation')
    parser.add_argument('--append-tags', action='store_true',
                       help='Append new tags instead of replacing existing ones')
    parser.add_argument('--find-untagged', action='store_true',
                       help='Just find and list untagged articles')
    parser.add_argument('--apply-suggestions', action='store_true',
                       help='Apply saved tag suggestions from export folder')
    parser.add_argument('--suggestion-file', type=str,
                       help='Specific suggestion file to apply')
    parser.add_argument('--batch', action='store_true',
                       help='Run in batch mode - process multiple articles automatically')
    parser.add_argument('--review', action='store_true',
                       help='Review and apply saved tag suggestions interactively')
    parser.add_argument('--reset-progress', action='store_true',
                       help='Reset batch processing progress')
    
    args = parser.parse_args()
    
    try:
        # Initialize tagger with target directory
        tagger = ObsidianArticleTagger(args.vault_path, target_dir=args.target_dir)
        
        if args.reset_progress:
            # Reset batch progress
            tagger.reset_batch_progress()
        elif args.batch:
            # Run batch analysis
            tagger.batch_analysis_session(limit=args.limit)
        elif args.review:
            # Review suggestions interactively
            tagger.review_suggestions()
        elif args.apply_suggestions:
            # Apply saved suggestions
            print(f"\n📋 Applying saved tag suggestions...")
            tagger.apply_saved_suggestions(args.suggestion_file)
        elif args.find_untagged:
            # Just find and list untagged articles
            print(f"\n🔍 Searching for untagged articles...")
            print(f"Target directory: {args.target_dir} (main directory only)")
            print(f"Filter: Articles must have abstracts")
            
            untagged = tagger.find_articles_without_tags(main_dir_only=True, require_abstract=True)
            print(f"\nFound {len(untagged)} articles with abstracts that need tags:\n")
            
            # Group by directory
            by_dir = defaultdict(list)
            for article in untagged:
                dir_name = article.parent.relative_to(tagger.vault_path)
                by_dir[str(dir_name)].append(article)
            
            # Show grouped results
            for dir_name, articles in sorted(by_dir.items()):
                print(f"\n📁 {dir_name}/ ({len(articles)} articles)")
                for article in articles[:5]:  # Show first 5 per directory
                    print(f"   - {article.name}")
                if len(articles) > 5:
                    print(f"   ... and {len(articles) - 5} more")
            
            print(f"\n💡 Use --limit N to analyze N articles at a time")
            print(f"💡 Use --auto-apply to automatically apply suggested tags")
        else:
            # Run deep analysis session
            replace_mode = not args.append_tags  # Default is replace unless --append-tags is used
            tagger.deep_analysis_session(limit=args.limit, auto_apply=args.auto_apply, replace_mode=replace_mode)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())