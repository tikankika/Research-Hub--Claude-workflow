#!/usr/bin/env python3
"""
Paperpile BibTeX to Markdown Exporter
Converts entries from paperpile.bib to markdown files in Obsidian vault format
"""

import os
import re
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
from datetime import datetime
import argparse
from pathlib import Path

class PaperpileExporter:
    def __init__(self, bib_path, output_dir):
        """Initialize with paths to bib file and output directory"""
        self.bib_path = Path(bib_path)
        self.output_dir = Path(output_dir)
        
        if not self.bib_path.exists():
            raise FileNotFoundError(f"BibTeX file not found at {bib_path}")
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def parse_bibtex(self):
        """Parse the BibTeX file and return entries"""
        parser = BibTexParser()
        parser.customization = convert_to_unicode
        
        with open(self.bib_path, 'r', encoding='utf-8') as bibfile:
            bib_database = bibtexparser.load(bibfile, parser=parser)
        
        return bib_database.entries
    
    def format_authors(self, author_string):
        """Format authors from BibTeX format to list of names"""
        if not author_string:
            return []
        
        # Split by 'and'
        authors = author_string.split(' and ')
        formatted_authors = []
        
        for author in authors:
            author = author.strip()
            # Handle "Last, First" format
            if ',' in author:
                parts = author.split(',')
                last_name = parts[0].strip()
                first_name = parts[1].strip() if len(parts) > 1 else ''
                formatted_authors.append({
                    'firstName': first_name,
                    'lastName': last_name,
                    'fullName': f"{first_name} {last_name}".strip()
                })
            else:
                # Handle "First Last" format
                parts = author.split()
                if len(parts) >= 2:
                    first_name = ' '.join(parts[:-1])
                    last_name = parts[-1]
                else:
                    first_name = ''
                    last_name = parts[0] if parts else author
                
                formatted_authors.append({
                    'firstName': first_name,
                    'lastName': last_name,
                    'fullName': author
                })
        
        return formatted_authors
    
    def generate_filename(self, entry):
        """Generate filename based on entry metadata"""
        # Get authors
        authors = self.format_authors(entry.get('author', ''))
        
        # Format author string
        if not authors:
            author_string = "Unknown"
        elif len(authors) == 1:
            author_string = authors[0]['lastName']
        elif len(authors) == 2:
            author_string = f"{authors[0]['lastName']} & {authors[1]['lastName']}"
        else:
            # For 3+ authors
            author_names = [a['lastName'] for a in authors]
            author_string = ", ".join(author_names[:-1]) + " & " + author_names[-1]
        
        # Get year
        year = entry.get('year', 'n.d.')
        
        # Get title
        title = entry.get('title', 'Untitled')
        # Remove curly braces from title
        title = re.sub(r'[{}]', '', title)
        
        # Create filename
        filename = f"{author_string} ({year}). {title}.md"
        
        # Sanitize filename
        filename = filename.replace('/', '-')
        filename = filename.replace('\\', '-')
        filename = filename.replace(':', '-')
        filename = filename.replace('*', '-')
        filename = filename.replace('?', '')
        filename = filename.replace('"', "'")
        filename = filename.replace('<', '-')
        filename = filename.replace('>', '-')
        filename = filename.replace('|', '-')
        
        # Limit length
        if len(filename) > 255:
            prefix = f"{author_string} ({year}). "
            max_title_length = 250 - len(prefix)
            title = title[:max_title_length]
            filename = f"{prefix}{title}.md"
        
        return filename
    
    def format_as_markdown(self, entry):
        """Convert BibTeX entry to markdown format"""
        md_lines = []
        
        # Title
        title = entry.get('title', 'Untitled')
        title = re.sub(r'[{}]', '', title)  # Remove curly braces
        md_lines.append(f"# {title}\n")
        
        # Metadata section
        md_lines.append("## Metadata\n")
        
        # Type
        entry_type = entry.get('ENTRYTYPE', 'article').title()
        md_lines.append(f"**Type:** {entry_type}")
        
        # Authors
        authors = self.format_authors(entry.get('author', ''))
        if authors:
            # Convert to wikilinks with first and last name
            author_links = []
            for author in authors:
                # Use full name for wikilink
                full_name = f"{author['firstName']} {author['lastName']}".strip()
                if full_name:
                    author_links.append(f"[[{full_name}]]")
            if author_links:
                md_lines.append(f"**Author(s):** {', '.join(author_links)}")
        
        # Date/Year
        if 'year' in entry:
            md_lines.append(f"**Date:** {entry['year']}")
        
        # Journal/Publisher - with wikilinks just like Zotero script
        if 'journal' in entry:
            md_lines.append(f"**Journal:** [[{entry['journal']}]]")
        elif 'publisher' in entry:
            md_lines.append(f"**Publisher:** [[{entry['publisher']}]]")
        
        # Abstract
        if 'abstract' in entry:
            abstract = entry['abstract']
            # Clean up abstract formatting
            abstract = re.sub(r'\s+', ' ', abstract)  # Replace multiple spaces/newlines with single space
            abstract = abstract.strip()
            md_lines.append(f"\n## Abstract\n\n{abstract}")
        
        # Additional fields
        other_fields = []
        
        if 'volume' in entry:
            other_fields.append(f"**Volume:** {entry['volume']}")
        
        if 'number' in entry:
            other_fields.append(f"**Issue:** {entry['number']}")
        
        if 'pages' in entry:
            other_fields.append(f"**Pages:** {entry['pages']}")
        
        if 'doi' in entry:
            other_fields.append(f"**DOI:** {entry['doi']}")
        
        if 'isbn' in entry:
            other_fields.append(f"**ISBN:** {entry['isbn']}")
        
        if 'url' in entry:
            other_fields.append(f"**URL:** {entry['url']}")
        
        if other_fields:
            md_lines.append("\n## Additional Information\n")
            md_lines.extend(other_fields)
        
        # Keywords/Tags
        if 'keywords' in entry:
            keywords = entry['keywords'].split(',')
            # Convert to hashtags
            hashtags = [f"#{keyword.strip().replace(' ', '_')}" for keyword in keywords]
            md_lines.append(f"\n## Tags\n\n{', '.join(hashtags)}")
        
        # Paperpile Information (similar to Zotero Information section)
        md_lines.append("\n## Paperpile Information\n")
        md_lines.append(f"**Key:** {entry.get('ID', 'unknown')}")
        md_lines.append(f"**Entry Type:** @{entry.get('ENTRYTYPE', 'article')}")
        md_lines.append(f"**Date Added:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Add note about source - keep this for tracking
        md_lines.append(f"\n---\n*Imported from Paperpile on {datetime.now().strftime('%Y-%m-%d')}*")
        
        return '\n'.join(md_lines)
    
    def check_file_exists_in_tree(self, filename):
        """Check if file exists in output directory or any subdirectory"""
        # Check in main directory
        if (self.output_dir / filename).exists():
            return True
        
        # Check in all subdirectories
        for subdir in self.output_dir.rglob('*/'):
            if (subdir / filename).exists():
                return True
        
        return False
    
    def find_paperpile_files(self):
        """Find all files that were imported from Paperpile"""
        paperpile_files = []
        
        # Search in output directory and all subdirectories
        for md_file in self.output_dir.rglob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check if file contains Paperpile import marker
                    if '*Imported from Paperpile on' in content:
                        paperpile_files.append(md_file)
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
        
        return paperpile_files
    
    def get_expected_filenames(self, entries):
        """Get list of expected filenames from BibTeX entries"""
        expected_files = set()
        
        for entry in entries:
            try:
                filename = self.generate_filename(entry)
                expected_files.add(filename)
            except Exception as e:
                print(f"Error generating filename for entry {entry.get('ID', 'unknown')}: {e}")
        
        return expected_files
    
    def find_duplicates_in_main_folder(self):
        """Find files in main folder that exist in subfolders"""
        duplicates = []
        
        # Get all files in main directory (not in subdirectories)
        main_folder_files = [f for f in self.output_dir.glob('*.md') if f.is_file()]
        
        # Check each file to see if it exists in any subdirectory
        for main_file in main_folder_files:
            filename = main_file.name
            
            # Check subdirectories
            for subdir in self.output_dir.iterdir():
                if subdir.is_dir() and not subdir.name.startswith('.'):
                    subfile = subdir / filename
                    if subfile.exists():
                        # Verify both are paperpile imports
                        try:
                            with open(main_file, 'r', encoding='utf-8') as f:
                                if '*Imported from Paperpile on' in f.read():
                                    duplicates.append((main_file, subfile))
                                    break
                        except Exception as e:
                            print(f"Error reading {main_file}: {e}")
        
        return duplicates
    
    def sync_with_paperpile(self, abstract_only=True, dry_run=False, remove_duplicates=False):
        """Sync markdown files with paperpile.bib - remove orphaned files and optionally duplicates"""
        print(f"Syncing with BibTeX file: {self.bib_path}")
        
        # Get all entries from BibTeX
        entries = self.parse_bibtex()
        if abstract_only:
            entries = [e for e in entries if 'abstract' in e and e['abstract'].strip()]
        
        # Get expected filenames
        expected_files = self.get_expected_filenames(entries)
        print(f"Expected {len(expected_files)} files from paperpile.bib")
        
        # Find existing paperpile files
        paperpile_files = self.find_paperpile_files()
        print(f"Found {len(paperpile_files)} existing files imported from Paperpile")
        
        # Find orphaned files
        orphaned_files = []
        for md_file in paperpile_files:
            filename = md_file.name
            if filename not in expected_files:
                orphaned_files.append(md_file)
        
        print(f"\nFound {len(orphaned_files)} orphaned files to remove:")
        for file in orphaned_files:
            print(f"  - {file.relative_to(self.output_dir.parent)}")
        
        # Find duplicates if requested
        duplicates_to_remove = []
        if remove_duplicates:
            duplicates = self.find_duplicates_in_main_folder()
            print(f"\nFound {len(duplicates)} duplicate files in main folder that exist in subfolders:")
            for main_file, sub_file in duplicates:
                print(f"  - {main_file.name}")
                print(f"    → Also in: {sub_file.parent.name}/")
                duplicates_to_remove.append(main_file)
        
        # Combine files to remove
        all_files_to_remove = list(set(orphaned_files + duplicates_to_remove))
        
        if all_files_to_remove and not dry_run:
            print(f"\nTotal files to remove: {len(all_files_to_remove)}")
            response = input("\nDo you want to remove these files? (yes/no): ")
            if response.lower() == 'yes':
                for file in all_files_to_remove:
                    try:
                        file.unlink()
                        print(f"Removed: {file.name}")
                    except Exception as e:
                        print(f"Error removing {file}: {e}")
            else:
                print("Skipping file removal.")
        
        return len(orphaned_files), len(duplicates_to_remove)
    
    def export_all(self, abstract_only=True, dry_run=False, sync_mode=False, remove_duplicates=False):
        """Export all entries to markdown files"""
        # Run sync first if requested
        if sync_mode:
            orphaned_count, duplicate_count = self.sync_with_paperpile(
                abstract_only=abstract_only, 
                dry_run=dry_run,
                remove_duplicates=remove_duplicates
            )
            print(f"\n{'='*50}\n")
        
        print(f"Reading BibTeX file: {self.bib_path}")
        entries = self.parse_bibtex()
        print(f"Found {len(entries)} entries in BibTeX file")
        
        # Filter entries with abstracts if requested
        if abstract_only:
            entries_with_abstract = [e for e in entries if 'abstract' in e and e['abstract'].strip()]
            print(f"Found {len(entries_with_abstract)} entries with abstracts")
            entries = entries_with_abstract
        
        exported_count = 0
        skipped_count = 0
        errors = []
        
        for entry in entries:
            try:
                # Generate markdown content
                md_content = self.format_as_markdown(entry)
                
                # Generate filename
                filename = self.generate_filename(entry)
                filepath = self.output_dir / filename
                
                # Check if file already exists anywhere in the tree
                if self.check_file_exists_in_tree(filename):
                    print(f"Skipping (already exists): {filename}")
                    skipped_count += 1
                    continue
                
                if dry_run:
                    print(f"Would create: {filename}")
                else:
                    # Write file
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f"Created: {filename}")
                
                exported_count += 1
                
            except Exception as e:
                error_msg = f"Error processing entry {entry.get('ID', 'unknown')}: {e}"
                print(error_msg)
                errors.append(error_msg)
        
        # Summary
        print(f"\n{'DRY RUN ' if dry_run else ''}Summary:")
        print(f"- Total entries processed: {len(entries)}")
        print(f"- Files {'would be created' if dry_run else 'created'}: {exported_count}")
        print(f"- Files skipped (already exist): {skipped_count}")
        print(f"- Errors: {len(errors)}")
        
        if errors:
            print("\nErrors encountered:")
            for error in errors:
                print(f"  - {error}")
        
        return exported_count

def main():
    parser = argparse.ArgumentParser(description='Export Paperpile BibTeX entries to Obsidian markdown files')
    parser.add_argument('--bib-path', default='paperpile/paperpile.bib',
                       help='Path to paperpile.bib file (default: paperpile/paperpile.bib)')
    parser.add_argument('--output-dir', default='4 Articles',
                       help='Output directory for markdown files (default: 4 Articles)')
    parser.add_argument('--all-entries', action='store_true',
                       help='Export all entries, not just those with abstracts')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without creating files')
    parser.add_argument('--sync', action='store_true',
                       help='Sync mode: remove orphaned files that are no longer in paperpile.bib')
    parser.add_argument('--remove-duplicates', action='store_true',
                       help='Remove files from main folder if they exist in subfolders')
    
    args = parser.parse_args()
    
    try:
        exporter = PaperpileExporter(args.bib_path, args.output_dir)
        abstract_only = not args.all_entries
        exporter.export_all(
            abstract_only=abstract_only, 
            dry_run=args.dry_run, 
            sync_mode=args.sync,
            remove_duplicates=args.remove_duplicates
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())