#!/usr/bin/env python3
"""
Obsidian Batch Tagger with Claude Code Integration
Analyzes untagged articles and applies intelligent tags.
"""

import re
import json
from pathlib import Path
from datetime import datetime
import argparse
from typing import List, Dict, Set, Tuple

class ObsidianBatchTagger:
    def __init__(self, vault_path: str):
        """Initialize with Obsidian vault path"""
        self.vault_path = Path(vault_path)
        self.articles_dir = self.vault_path / "4 Articles"
        
        if not self.articles_dir.exists():
            raise FileNotFoundError(f"Articles directory not found at {self.articles_dir}")
        
        # Academic tag vocabulary based on your vault
        self.tag_vocabulary = {
            # AI/Technology
            'artificial intelligence': ['artificial intelligence', ' ai ', 'aied'],
            'machine_learning': ['machine learning', 'deep learning', 'neural network'],
            'chatgpt': ['chatgpt', 'gpt', 'language model', 'llm', 'generative ai'],
            'intelligent_tutoring_systems': ['intelligent tutor', 'its ', 'tutoring system'],
            'learning_analytics': ['learning analytic', 'educational data mining'],
            
            # Educational levels
            'higher_education': ['higher education', 'university', 'college', 'undergraduate', 'graduate'],
            'k_12': ['k-12', 'k12', 'primary', 'secondary', 'school', 'elementary'],
            'teacher_education': ['teacher education', 'teacher training', 'pre-service teacher', 'preservice teacher'],
            
            # Methods
            'case_study': ['case study', 'case studies'],
            'systematic_review': ['systematic review', 'meta-analysis', 'literature review'],
            'ethnography': ['ethnograph'],
            'qualitative_research': ['qualitative', 'interview', 'thematic analysis'],
            'quantitative_research': ['quantitative', 'statistical', 'experiment'],
            
            # Learning approaches
            'collaborative_learning': ['collaborative learning', 'cooperation', 'group work'],
            'online_learning': ['online learning', 'e-learning', 'distance education', 'remote learning'],
            'game_based_learning': ['game-based', 'gamification', 'serious games'],
            'dialogic_learning': ['dialogic', 'dialogue', 'discussion'],
            
            # Other key topics
            'assessment': ['assessment', 'evaluation', 'grading'],
            'professional_development': ['professional development', 'teacher development', 'pd '],
            'social_media': ['social media', 'twitter', 'facebook', 'instagram'],
            'ai_ethics': ['ai ethics', 'ethical', 'responsible ai'],
            'covid_19': ['covid', 'pandemic', 'lockdown'],
        }
    
    def find_untagged_articles(self, limit: int = None) -> List[Path]:
        """Find articles without tags"""
        untagged = []
        
        for md_file in self.articles_dir.rglob('*.md'):
            if self._needs_tags(md_file):
                untagged.append(md_file)
                if limit and len(untagged) >= limit:
                    break
        
        return untagged
    
    def _needs_tags(self, file_path: Path) -> bool:
        """Check if article needs tags"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for existing tags
            hashtags = re.findall(r'#[\w_]+', content)
            yaml_tags = re.search(r'^tags:\s*\[([^\]]+)\]', content, re.MULTILINE)
            
            # Consider it needs tags if it has fewer than 3 tags
            tag_count = len(hashtags)
            if yaml_tags:
                tag_count += len([t.strip() for t in yaml_tags.group(1).split(',')])
            
            return tag_count < 3
            
        except Exception:
            return True
    
    def extract_article_info(self, file_path: Path) -> Dict:
        """Extract article information for analysis"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else file_path.stem
            
            # Extract year from filename or content
            year_match = re.search(r'\((\d{4})\)', file_path.name)
            year = year_match.group(1) if year_match else ''
            
            # Extract authors from filename
            authors_match = re.match(r'^([^(]+)\s*\(', file_path.name)
            authors = authors_match.group(1).strip() if authors_match else ''
            
            # Extract abstract
            abstract_match = re.search(r'## Abstract\s*\n\s*\n(.+?)(?=\n\n##|\Z)', content, re.DOTALL)
            abstract = abstract_match.group(1).strip() if abstract_match else ''
            
            # Extract journal/conference
            journal_match = re.search(r'\*\*Journal:\*\*\s*\[\[([^\]]+)\]\]', content)
            journal = journal_match.group(1) if journal_match else ''
            
            return {
                'file_path': str(file_path),
                'filename': file_path.name,
                'title': title,
                'authors': authors,
                'year': year,
                'abstract': abstract[:500] + '...' if len(abstract) > 500 else abstract,
                'journal': journal,
                'full_text': content[:1000]  # First 1000 chars for analysis
            }
        except Exception as e:
            return {
                'file_path': str(file_path),
                'filename': file_path.name,
                'error': str(e)
            }
    
    def suggest_tags_keyword(self, article_info: Dict) -> List[str]:
        """Suggest tags based on keyword matching"""
        tags = set()
        
        # Combine all text for analysis
        text = ' '.join([
            article_info.get('title', ''),
            article_info.get('abstract', ''),
            article_info.get('journal', '')
        ]).lower()
        
        # Check each tag category
        for tag, keywords in self.tag_vocabulary.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    tags.add(tag)
                    break
        
        # Limit to most relevant tags
        return list(tags)[:6]
    
    def export_for_claude(self, articles: List[Dict], output_path: Path = None):
        """Export articles for Claude Code analysis"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if not output_path:
            export_dir = self.Path(__file__).parent.parent / "export"'
            export_dir.mkdir(parents=True, exist_ok=True)
            output_path = export_dir / f'untagged_articles_{timestamp}.json'
        
        export_data = {
            'timestamp': timestamp,
            'total_articles': len(articles),
            'articles': articles
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    def print_for_claude(self, articles: List[Dict]):
        """Print articles for Claude Code analysis"""
        print("\n" + "="*80)
        print("ARTICLES FOR CLAUDE CODE ANALYSIS")
        print("="*80)
        print("\nPlease analyze these articles and suggest 3-6 specific academic tags for each.")
        print("Focus on: main topic, methodology, educational level, technology used, research type.")
        print("Use snake_case for multi-word tags (e.g., machine_learning, higher_education)\n")
        
        for i, article in enumerate(articles, 1):
            print(f"\n--- ARTICLE {i} ---")
            print(f"File: {article['filename']}")
            print(f"Title: {article.get('title', 'N/A')}")
            print(f"Authors: {article.get('authors', 'N/A')}")
            print(f"Year: {article.get('year', 'N/A')}")
            if article.get('journal'):
                print(f"Journal: {article['journal']}")
            if article.get('abstract'):
                print(f"\nAbstract: {article['abstract']}")
            print("-" * 40)
        
        print("\n\nPlease provide tag suggestions in this JSON format:")
        print('[')
        print('  {"file": "filename1.md", "tags": ["tag1", "tag2", "tag3"]},')
        print('  {"file": "filename2.md", "tags": ["tag1", "tag2", "tag3"]}')
        print(']')
    
    def apply_tags(self, file_path: str, tags: List[str]) -> bool:
        """Apply tags to a markdown file"""
        try:
            path = Path(file_path)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if there's already a tags section
            if re.search(r'^## Tags', content, re.MULTILINE):
                # Add to existing tags section
                tags_section = re.search(r'^## Tags\s*\n(.+?)(?=\n##|\n---|\Z)', content, re.MULTILINE | re.DOTALL)
                if tags_section:
                    existing_tags = tags_section.group(1)
                    new_tags = ' '.join([f'#{tag}' for tag in tags])
                    updated_tags = f"{existing_tags.rstrip()} {new_tags}"
                    content = content.replace(tags_section.group(0), f"## Tags\n{updated_tags}")
            else:
                # Add new tags section before the footer
                tag_string = ' '.join([f'#{tag}' for tag in tags])
                tags_section = f"\n## Tags\n{tag_string}\n"
                
                # Try to insert before the "---" separator
                if '\n---\n' in content:
                    content = content.replace('\n---\n', f'{tags_section}\n---\n', 1)
                else:
                    content += tags_section
            
            # Write back
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error applying tags to {file_path}: {e}")
            return False
    
    def apply_claude_suggestions(self, suggestions_file: Path) -> int:
        """Apply tags from Claude's suggestions"""
        with open(suggestions_file, 'r') as f:
            suggestions = json.load(f)
        
        success_count = 0
        for item in suggestions:
            file_path = self.articles_dir / item['file']
            if file_path.exists():
                if self.apply_tags(str(file_path), item['tags']):
                    print(f"✓ Tagged {item['file']}: {', '.join(item['tags'])}")
                    success_count += 1
                else:
                    print(f"✗ Failed to tag {item['file']}")
            else:
                print(f"✗ File not found: {item['file']}")
        
        return success_count

def main():
    parser = argparse.ArgumentParser(description='Batch tag Obsidian articles')
    parser.add_argument('--vault', type=str, 
                       default="/Users/niklaskarlsson/Obsidian Sandbox/Book project, Sandbox",
                       help='Path to Obsidian vault')
    parser.add_argument('--limit', type=int, default=10,
                       help='Number of articles to process')
    parser.add_argument('--mode', choices=['keyword', 'claude', 'export'], default='claude',
                       help='Tagging mode')
    parser.add_argument('--apply', type=str,
                       help='Apply tags from Claude suggestions JSON file')
    
    args = parser.parse_args()
    
    tagger = ObsidianBatchTagger(args.vault)
    
    # Apply mode
    if args.apply:
        suggestions_path = Path(args.apply)
        if not suggestions_path.exists():
            print(f"Error: Suggestions file not found: {args.apply}")
            return
        
        count = tagger.apply_claude_suggestions(suggestions_path)
        print(f"\nApplied tags to {count} articles")
        return
    
    # Find untagged articles
    print(f"Finding untagged articles (limit: {args.limit})...")
    untagged_files = tagger.find_untagged_articles(limit=args.limit)
    
    if not untagged_files:
        print("No untagged articles found!")
        return
    
    print(f"Found {len(untagged_files)} articles needing tags")
    
    # Extract article information
    articles = []
    for file_path in untagged_files:
        info = tagger.extract_article_info(file_path)
        articles.append(info)
    
    if args.mode == 'keyword':
        # Keyword matching mode
        success_count = 0
        for article in articles:
            if 'error' in article:
                continue
            
            tags = tagger.suggest_tags_keyword(article)
            if tags:
                if tagger.apply_tags(article['file_path'], tags):
                    print(f"✓ {article['filename']}: {', '.join(tags)}")
                    success_count += 1
        
        print(f"\nTagged {success_count} articles")
        
    elif args.mode == 'export':
        # Export mode
        export_path = tagger.export_for_claude(articles)
        print(f"\nExported {len(articles)} articles to: {export_path}")
        
    else:
        # Claude mode - print for analysis
        tagger.print_for_claude(articles)
        
        # Also save to file
        export_path = tagger.export_for_claude(articles)
        print(f"\n\n(Articles also saved to: {export_path})")
        print("\nTO COMPLETE TAGGING:")
        print("1. Copy the JSON output from Claude Code")
        print("2. Save it to a file (e.g., suggestions.json)")
        print(f"3. Run: python3 {__file__} --apply suggestions.json")

if __name__ == "__main__":
    main()