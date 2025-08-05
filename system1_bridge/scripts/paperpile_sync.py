#!/usr/bin/env python3
"""
Paperpile to Obsidian synchronization with content provenance tracking.
Updates only Paperpile metadata while preserving user content.
"""

import re
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import bibtexparser
from colorama import init, Fore, Style

init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paperpile_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PaperpileSync:
    def __init__(self, vault_path: str, bibtex_path: str):
        self.vault_path = Path(vault_path)
        self.bibtex_path = Path(bibtex_path)
        self.articles_dir = self.vault_path / "4 Articles"
        self.pdf_base = self.vault_path / "9 Paperpile"
        
        # Content markers for provenance tracking
        self.PAPERPILE_START = "<!-- PAPERPILE METADATA START -->"
        self.PAPERPILE_END = "<!-- PAPERPILE METADATA END -->"
        self.USER_START = "<!-- USER CONTENT START -->"
        self.USER_END = "<!-- USER CONTENT END -->"
        self.SCRIPT_START = "<!-- SCRIPT GENERATED START -->"
        self.SCRIPT_END = "<!-- SCRIPT GENERATED END -->"
        
        # Sync tracking
        self.bibtex_entries = {}
        self.sync_stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'orphaned': []
        }
    
    def run_sync(self, test_limit: int = None):
        """Run the synchronization process"""
        print(f"\n{Fore.CYAN}=== PAPERPILE TO OBSIDIAN SYNC ==={Style.RESET_ALL}\n")
        
        # Step 1: Parse BibTeX
        print("1. Loading BibTeX database...")
        self.parse_bibtex()
        
        # Step 2: Process entries
        print("\n2. Processing articles...")
        entries_to_process = list(self.bibtex_entries.values())
        if test_limit:
            entries_to_process = entries_to_process[:test_limit]
            print(f"   (Limited to {test_limit} articles for testing)")
        
        for i, entry in enumerate(entries_to_process, 1):
            print(f"\n[{i}/{len(entries_to_process)}] Processing {entry['ID']}...")
            self.sync_article(entry)
        
        # Step 3: Find orphaned files
        print("\n3. Checking for orphaned files...")
        self.find_orphaned_files()
        
        # Step 4: Generate report
        print("\n4. Generating sync report...")
        self.generate_report()
    
    def parse_bibtex(self):
        """Parse BibTeX file and extract all entries"""
        with open(self.bibtex_path, 'r', encoding='utf-8') as f:
            bib_database = bibtexparser.load(f)
        
        for entry in bib_database.entries:
            key = entry.get('ID', '')
            if key:
                # Extract year from date field if not present
                if 'year' not in entry and 'date' in entry:
                    date = entry['date']
                    # Extract year from date like "2024-09-05"
                    year_match = re.search(r'(\d{4})', date)
                    if year_match:
                        entry['year'] = year_match.group(1)
                
                self.bibtex_entries[key] = entry
        
        print(f"  ✓ Loaded {len(self.bibtex_entries)} BibTeX entries")
    
    def sync_article(self, entry: Dict):
        """Sync a single article"""
        try:
            # Determine file path
            bibtex_key = entry['ID']
            file_path = self.articles_dir / f"{bibtex_key}.md"
            
            logger.info(f"Processing {bibtex_key}: {file_path}")
            
            if file_path.exists():
                # Update existing file
                self.update_article(file_path, entry)
            else:
                # Create new file
                self.create_article(file_path, entry)
                
        except Exception as e:
            print(f"  {Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
            self.sync_stats['errors'] += 1
    
    def create_article(self, file_path: Path, entry: Dict):
        """Create a new article file"""
        content = self.generate_article_content(entry)
        
        file_path.write_text(content, encoding='utf-8')
        self.sync_stats['created'] += 1
        print(f"  {Fore.GREEN}✓ Created new article{Style.RESET_ALL}")
    
    def update_article(self, file_path: Path, entry: Dict):
        """Update existing article, preserving user content"""
        existing_content = file_path.read_text(encoding='utf-8')
        
        # Check if file has new format markers
        has_new_format = self.PAPERPILE_START in existing_content
        
        if not has_new_format:
            logger.info(f"  Converting legacy format for {file_path.name}")
            # For legacy files, we need to extract existing content and convert
            self.convert_legacy_file(file_path, entry, existing_content)
            return
        
        # Parse content sections
        sections = self.parse_content_sections(existing_content)
        
        # Generate new Paperpile section
        new_paperpile_content = self.generate_paperpile_section(entry)
        
        # Check if update needed
        if sections.get('paperpile') == new_paperpile_content:
            print(f"  → No changes needed")
            logger.info(f"  No changes needed for {file_path.name}")
            self.sync_stats['skipped'] += 1
            return
        
        # Rebuild content preserving user sections
        new_content = self.rebuild_content(entry, sections, new_paperpile_content)
        
        file_path.write_text(new_content, encoding='utf-8')
        self.sync_stats['updated'] += 1
        print(f"  {Fore.GREEN}✓ Updated metadata{Style.RESET_ALL}")
        logger.info(f"  Updated metadata for {file_path.name}")
    
    def parse_content_sections(self, content: str) -> Dict[str, str]:
        """Parse content into sections based on markers"""
        sections = {}
        
        # Extract Paperpile section
        paperpile_match = re.search(
            f"{re.escape(self.PAPERPILE_START)}(.*?){re.escape(self.PAPERPILE_END)}",
            content, re.DOTALL
        )
        if paperpile_match:
            sections['paperpile'] = paperpile_match.group(1).strip()
        
        # Extract user content section
        user_match = re.search(
            f"{re.escape(self.USER_START)}(.*?){re.escape(self.USER_END)}",
            content, re.DOTALL
        )
        if user_match:
            sections['user'] = user_match.group(1).strip()
        
        # Extract script generated section
        script_match = re.search(
            f"{re.escape(self.SCRIPT_START)}(.*?){re.escape(self.SCRIPT_END)}",
            content, re.DOTALL
        )
        if script_match:
            sections['script'] = script_match.group(1).strip()
        
        # Extract frontmatter
        if content.startswith('---'):
            fm_end = content.find('---', 3)
            if fm_end > 0:
                sections['frontmatter'] = content[3:fm_end].strip()
        
        # Any content outside marked sections is considered user content
        unmarked = self.extract_unmarked_content(content)
        if unmarked:
            existing_user = sections.get('user', '')
            sections['user'] = f"{existing_user}\n\n{unmarked}".strip() if existing_user else unmarked
        
        return sections
    
    def extract_unmarked_content(self, content: str) -> str:
        """Extract content that's outside any marked sections"""
        # Remove all marked sections
        cleaned = content
        
        # Remove frontmatter
        if cleaned.startswith('---'):
            fm_end = cleaned.find('---', 3)
            if fm_end > 0:
                cleaned = cleaned[fm_end + 3:].lstrip()
        
        # Remove marked sections
        for start, end in [
            (self.PAPERPILE_START, self.PAPERPILE_END),
            (self.USER_START, self.USER_END),
            (self.SCRIPT_START, self.SCRIPT_END)
        ]:
            pattern = f"{re.escape(start)}.*?{re.escape(end)}"
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL)
        
        # Remove title (first line starting with #)
        lines = cleaned.strip().split('\n')
        if lines and lines[0].startswith('#'):
            lines = lines[1:]
        
        unmarked = '\n'.join(lines).strip()
        
        # Don't include if it's just whitespace or very short
        if len(unmarked) < 10:
            return ""
        
        return unmarked
    
    def generate_article_content(self, entry: Dict) -> str:
        """Generate complete article content for new file"""
        # Generate components
        frontmatter = self.generate_frontmatter(entry)
        title = self.format_title(entry)
        paperpile_section = self.generate_paperpile_section(entry)
        
        # Build complete content
        content = f"{frontmatter}\n\n"
        content += f"# {title}\n\n"
        content += f"{self.PAPERPILE_START}\n{paperpile_section}\n{self.PAPERPILE_END}\n\n"
        content += f"{self.SCRIPT_START}\n## Tags\n\n*Tags will be added by tagging script*\n{self.SCRIPT_END}\n\n"
        content += f"{self.USER_START}\n## My Notes\n\n\n{self.USER_END}"
        
        return content
    
    def generate_frontmatter(self, entry: Dict) -> str:
        """Generate YAML frontmatter with minimal aliases"""
        # Extract key metadata
        authors = self.format_short_authors(entry.get('author', ''))
        year = entry.get('year', '')
        
        # Generate minimal aliases - only short citation if year is valid
        aliases = []
        if authors and year and re.match(r'^\d{4}$', str(year)):
            aliases.append(f"{authors} {year}")
        
        # Build frontmatter
        yaml = "---\n"
        if aliases:
            yaml += "aliases:\n"
            for alias in aliases:
                yaml += f'  - "{alias}"\n'
        yaml += "---"
        
        return yaml
    
    def generate_paperpile_section(self, entry: Dict) -> str:
        """Generate Paperpile metadata section"""
        sections = []
        
        # Metadata section
        metadata = ["## Metadata"]
        metadata.append(f"**Type:** {entry.get('ENTRYTYPE', 'article').title()}")
        
        # Authors with wiki links
        if entry.get('author'):
            authors = self.format_authors_with_links(entry['author'])
            metadata.append(f"**Author(s):** {authors}")
        
        metadata.append(f"**Year:** {entry.get('year', 'n.d.')}")
        
        # Journal with wiki link (handle both 'journal' and 'journaltitle')
        journal = entry.get('journal') or entry.get('journaltitle')
        if journal:
            metadata.append(f"**Journal:** [[{journal}]]")
        
        # Publisher
        if entry.get('publisher'):
            metadata.append(f"**Publisher:** {entry['publisher']}")
        
        # DOI with clickable link
        if entry.get('doi'):
            doi = entry['doi']
            metadata.append(f"**DOI:** [{doi}](https://doi.org/{doi})")
        
        sections.append('\n'.join(metadata))
        
        # Abstract section
        if entry.get('abstract'):
            abstract = self.clean_field(entry['abstract'])
            sections.append(f"## Abstract\n\n{abstract}")
        
        # Additional Information section
        additional = ["## Additional Information"]
        
        if entry.get('volume'):
            additional.append(f"**Volume:** {entry['volume']}")
        
        if entry.get('number') or entry.get('issue'):
            issue = entry.get('number') or entry.get('issue')
            additional.append(f"**Issue:** {issue}")
        
        if entry.get('pages'):
            additional.append(f"**Pages:** {entry['pages']}")
        
        if entry.get('url'):
            url = entry['url']
            additional.append(f"**URL:** [View Online]({url})")
        
        # PDF link
        pdf_path = self.extract_pdf_path(entry.get('file', ''))
        if pdf_path:
            additional.append(f"**PDF:** [[{pdf_path}]]")
        
        if entry.get('language'):
            additional.append(f"**Language:** {entry['language']}")
        
        if len(additional) > 1:  # More than just the header
            sections.append('\n'.join(additional))
        
        # Paperpile Notes section (user's notes from Paperpile)
        if entry.get('note'):
            note = self.clean_field(entry['note'])
            sections.append(f"## Paperpile Notes\n\n{note}")
        
        # Reference Information section
        ref_info = ["## Reference Information"]
        ref_info.append(f"**BibTeX Key:** {entry['ID']}")
        ref_info.append(f"**Entry Type:** @{entry.get('ENTRYTYPE', 'article')}")
        
        if entry.get('keywords'):
            keywords = entry['keywords']
            ref_info.append(f"**Keywords:** {keywords}")
        
        ref_info.append(f"**Last Paperpile Sync:** {datetime.now():%Y-%m-%d %H:%M:%S}")
        sections.append('\n'.join(ref_info))
        
        return '\n\n'.join(sections)
    
    def format_title(self, entry: Dict) -> str:
        """Format article title for display"""
        title = self.clean_field(entry.get('title', 'Untitled'))
        authors = self.format_short_authors(entry.get('author', ''))
        year = entry.get('year', 'n.d.')
        
        if authors:
            return f"{authors} ({year}). {title}"
        else:
            return f"({year}). {title}"
    
    def format_authors_with_links(self, author_string: str) -> str:
        """Format authors with wiki links"""
        authors = author_string.split(' and ')
        formatted = []
        
        for author in authors:
            author = author.strip()
            # Format as [[Last, First]]
            if ',' in author:
                formatted.append(f"[[{author}]]")
            else:
                # Convert "First Last" to "Last, First"
                parts = author.split()
                if len(parts) >= 2:
                    last = parts[-1]
                    first = ' '.join(parts[:-1])
                    formatted.append(f"[[{last}, {first}]]")
                else:
                    formatted.append(f"[[{author}]]")
        
        return ', '.join(formatted)
    
    def extract_pdf_path(self, file_field: str) -> str:
        """Extract PDF path from BibTeX file field"""
        if not file_field:
            return ""
        
        # Look for "All Papers/..." pattern
        match = re.search(r'(All Papers/[^:;]+\.pdf)', file_field)
        if match:
            paperpile_path = match.group(1)
            # Create Obsidian path (using lowercase as per user example)
            obsidian_path = f"9 paperpile/{paperpile_path}"
            
            # Verify the PDF actually exists
            full_path = self.vault_path / "9 Paperpile" / "Paperpile" / paperpile_path
            
            if full_path.exists():
                return obsidian_path
            else:
                print(f"  {Fore.YELLOW}⚠ PDF not found: {paperpile_path}{Style.RESET_ALL}")
        
        return ""
    
    def convert_legacy_file(self, file_path: Path, entry: Dict, existing_content: str):
        """Convert legacy format file to new format"""
        logger.info(f"  Converting legacy file: {file_path.name}")
        
        # Extract any user content from the legacy file
        # Look for common sections like Abstract, Tags, Notes, etc.
        user_content = []
        
        # Skip frontmatter and title
        lines = existing_content.split('\n')
        in_frontmatter = False
        skip_next = False
        
        for i, line in enumerate(lines):
            if i == 0 and line == '---':
                in_frontmatter = True
                continue
            if in_frontmatter and line == '---':
                in_frontmatter = False
                continue
            if in_frontmatter:
                continue
            
            # Skip title line
            if line.startswith('# '):
                skip_next = True
                continue
            
            # Skip metadata sections that will be regenerated
            if line.startswith('## Metadata') or \
               line.startswith('## Abstract') or \
               line.startswith('## Additional Information') or \
               line.startswith('## Zotero Information') or \
               line.startswith('## Collections'):
                skip_next = True
                continue
            
            # Skip known metadata lines
            if line.startswith('**Type:**') or \
               line.startswith('**Author(s):**') or \
               line.startswith('**Date:**') or \
               line.startswith('**Publisher:**') or \
               line.startswith('**Pages:**') or \
               line.startswith('**ISBN:**') or \
               line.startswith('**Key:**') or \
               line.startswith('**Item ID:**') or \
               line.startswith('**Date Added:**') or \
               line.startswith('**Date Modified:**'):
                continue
            
            # Check if we should skip this line
            if skip_next and not line.strip():
                skip_next = False
                continue
            
            # Keep user-added content
            if not skip_next and line.strip() and not line.startswith('Importerat '):
                # Check if this is a tags line
                if line.startswith('## Tags') or line.startswith('#'):
                    # This will go in script section
                    continue
                user_content.append(line)
        
        # Build new content with proper sections
        new_content = self.generate_frontmatter(entry) + "\n\n"
        new_content += f"# {self.format_title(entry)}\n\n"
        new_content += f"{self.PAPERPILE_START}\n{self.generate_paperpile_section(entry)}\n{self.PAPERPILE_END}\n\n"
        
        # Add script section for tags
        # Extract existing tags from legacy content
        existing_tags = []
        tag_match = re.findall(r'#(\S+)', existing_content)
        if tag_match:
            existing_tags = list(set(tag_match))
        
        if existing_tags:
            tags_content = "## Tags\n\n"
            for tag in existing_tags:
                tags_content += f"#{tag}\n"
        else:
            tags_content = "## Tags\n\n*Tags will be added by tagging script*"
        
        new_content += f"{self.SCRIPT_START}\n{tags_content}\n{self.SCRIPT_END}\n\n"
        
        # Add user content section
        if user_content:
            user_section = "## My Notes\n\n" + '\n'.join(user_content)
        else:
            user_section = "## My Notes\n\n"
        
        new_content += f"{self.USER_START}\n{user_section}\n{self.USER_END}"
        
        # Write the converted file
        file_path.write_text(new_content, encoding='utf-8')
        self.sync_stats['updated'] += 1
        print(f"  {Fore.GREEN}✓ Converted legacy format{Style.RESET_ALL}")
        logger.info(f"  Successfully converted {file_path.name} to new format")
    
    def rebuild_content(self, entry: Dict, sections: Dict, new_paperpile: str) -> str:
        """Rebuild file content with updated Paperpile section"""
        # Generate fresh frontmatter with correct aliases
        content = self.generate_frontmatter(entry) + "\n\n"
        
        # Add title
        content += f"# {self.format_title(entry)}\n\n"
        
        # Add Paperpile section
        content += f"{self.PAPERPILE_START}\n{new_paperpile}\n{self.PAPERPILE_END}\n\n"
        
        # Add script generated section if exists
        if sections.get('script'):
            content += f"{self.SCRIPT_START}\n{sections['script']}\n{self.SCRIPT_END}\n\n"
        else:
            content += f"{self.SCRIPT_START}\n## Tags\n\n*Tags will be added by tagging script*\n{self.SCRIPT_END}\n\n"
        
        # Add user content if exists
        if sections.get('user'):
            content += f"{self.USER_START}\n{sections['user']}\n{self.USER_END}"
        else:
            content += f"{self.USER_START}\n## My Notes\n\n\n{self.USER_END}"
        
        return content
    
    def clean_field(self, text: str) -> str:
        """Clean BibTeX field formatting"""
        if not text:
            return ""
        
        # Remove BibTeX braces
        text = re.sub(r'[{}]', '', text)
        
        # Fix LaTeX quotes
        text = text.replace("``", '"').replace("''", '"')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def format_short_authors(self, author_string: str) -> str:
        """Format authors for aliases"""
        if not author_string:
            return ""
        
        authors = author_string.split(' and ')
        if not authors:
            return ""
        
        first_author = self.extract_lastname(authors[0])
        
        if len(authors) == 1:
            return first_author
        elif len(authors) == 2:
            second_author = self.extract_lastname(authors[1])
            return f"{first_author} & {second_author}"
        else:
            return f"{first_author} et al."
    
    def extract_lastname(self, author: str) -> str:
        """Extract last name from author string"""
        author = author.strip()
        if ',' in author:
            return author.split(',')[0].strip()
        else:
            parts = author.split()
            return parts[-1] if parts else ""
    
    def extract_title_keywords(self, title: str) -> str:
        """Extract keywords from title for aliases - NO LONGER USED"""
        return ""
    
    def find_orphaned_files(self):
        """Find markdown files not in current BibTeX"""
        bibtex_keys = set(self.bibtex_entries.keys())
        
        for md_file in self.articles_dir.glob("*.md"):
            # Extract BibTeX key from filename or content
            file_key = md_file.stem  # Assuming migration completed
            
            if file_key not in bibtex_keys:
                # Double check by looking in file content
                content = md_file.read_text(encoding='utf-8')
                key_match = re.search(r'bibtex_key:\s*(\S+)', content) or \
                           re.search(r'BibTeX Key:\s*(\S+)', content)
                
                if key_match:
                    file_key = key_match.group(1)
                
                if file_key not in bibtex_keys:
                    self.sync_stats['orphaned'].append({
                        'file': md_file.name,
                        'key': file_key,
                        'path': str(md_file)
                    })
        
        if self.sync_stats['orphaned']:
            print(f"  {Fore.YELLOW}⚠ Found {len(self.sync_stats['orphaned'])} orphaned files{Style.RESET_ALL}")
    
    def generate_report(self):
        """Generate sync report"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}SYNC COMPLETE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        print(f"📊 Summary:")
        print(f"  Created: {self.sync_stats['created']} new articles")
        print(f"  Updated: {self.sync_stats['updated']} existing articles")
        print(f"  Skipped: {self.sync_stats['skipped']} unchanged articles")
        print(f"  Errors: {self.sync_stats['errors']}")
        
        if self.sync_stats['orphaned']:
            print(f"\n⚠️  Orphaned files (not in current BibTeX):")
            for orphan in self.sync_stats['orphaned'][:5]:
                print(f"  - {orphan['file']}")
            if len(self.sync_stats['orphaned']) > 5:
                print(f"  ... and {len(self.sync_stats['orphaned']) - 5} more")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.sync_stats,
            'bibtex_entries': len(self.bibtex_entries)
        }
        
        report_path = self.vault_path / Path(__file__).parent.parent / "export" / f"sync_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed report saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Sync Paperpile BibTeX to Obsidian vault'
    )
    parser.add_argument(
        '--vault',
        type=str,
        default='.',
        help='Path to Obsidian vault root'
    )
    parser.add_argument(
        '--bibtex',
        type=str,
        default='~/Desktop/paperpile.bib',
        help='Path to Paperpile BibTeX export'
    )
    parser.add_argument(
        '--test',
        type=int,
        metavar='N',
        help='Test with only N articles'
    )
    parser.add_argument(
        '--sync',
        action='store_true',
        default=True,
        help='Run synchronization (default action)'
    )
    
    args = parser.parse_args()
    
    # Expand paths
    vault_path = Path(args.vault).expanduser().resolve()
    bibtex_path = Path(args.bibtex).expanduser().resolve()
    
    # Validate
    if not vault_path.exists():
        print(f"{Fore.RED}Error: Vault path does not exist: {vault_path}{Style.RESET_ALL}")
        return
    
    if not bibtex_path.exists():
        print(f"{Fore.RED}Error: BibTeX file not found: {bibtex_path}{Style.RESET_ALL}")
        return
    
    # Run sync
    syncer = PaperpileSync(vault_path, bibtex_path)
    try:
        syncer.run_sync(test_limit=args.test)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Sync interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Sync failed: {e}{Style.RESET_ALL}")
        raise


if __name__ == "__main__":
    main()