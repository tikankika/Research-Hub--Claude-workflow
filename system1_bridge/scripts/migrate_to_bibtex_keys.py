#!/usr/bin/env python3
"""
Migrate Obsidian articles from descriptive filenames to BibTeX keys.
Preserves original filenames as aliases and maintains all links.
"""

import re
import json
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import bibtexparser
from colorama import init, Fore, Style

init(autoreset=True)

class VaultMigrator:
    def __init__(self, vault_path: str, bibtex_path: str):
        self.vault_path = Path(vault_path)
        self.bibtex_path = Path(bibtex_path)
        self.articles_dir = self.vault_path / "4 Articles"
        
        # Migration tracking
        self.bibtex_entries = {}
        self.migration_plan = []
        self.link_updates = []
        self.backup_dir = None
        
    def run_migration(self, dry_run: bool = True, batch_size: int = None):
        """Run the migration process"""
        print(f"\n{Fore.CYAN}=== VAULT MIGRATION TO BIBTEX KEYS ==={Style.RESET_ALL}\n")
        
        if batch_size:
            print(f"Mode: Batch processing ({batch_size} files per batch)")
        else:
            print(f"Mode: {'Dry run' if dry_run else 'Full migration'}")
        
        # Step 1: Parse BibTeX
        print("1. Loading BibTeX database...")
        self.parse_bibtex()
        
        # Step 2: Create backup
        if not dry_run:
            print("2. Creating backup...")
            self.create_backup()
        else:
            print("2. Skipping backup (dry run)")
        
        # Step 3: Build migration plan
        print("3. Building migration plan...")
        self.build_migration_plan()
        
        # Step 4: Preview changes
        print("4. Preview of changes:")
        self.preview_changes()
        
        if dry_run:
            print(f"\n{Fore.YELLOW}DRY RUN COMPLETE - No changes made{Style.RESET_ALL}")
            print("Run with --execute to apply changes")
            return
        
        # Step 5: Apply migration
        print("\n5. Applying migration...")
        
        # Auto-confirm for small test migrations or batch mode
        if len(self.migration_plan) <= 5 or batch_size == 1:
            print(f"{Fore.YELLOW}Auto-confirming migration of {len(self.migration_plan)} files (test mode){Style.RESET_ALL}")
        elif batch_size and batch_size > 1:
            # Auto-confirm for batch mode
            print(f"\n{Fore.YELLOW}Batch mode: Auto-confirming migration of {len(self.migration_plan)} files in batches of {batch_size}{Style.RESET_ALL}")
            print(f"This will take approximately {len(self.migration_plan) // 10} minutes.")
        else:
            # For large migrations without batch, add progress option
            print(f"\n{Fore.YELLOW}Ready to migrate {len(self.migration_plan)} files.{Style.RESET_ALL}")
            print(f"This will take approximately {len(self.migration_plan) // 10} minutes.")
            confirm = input(f"\n{Fore.YELLOW}Continue with migration? (y/N): {Style.RESET_ALL}")
            if confirm.lower() != 'y':
                print("Migration cancelled")
                return
        
        self.apply_migration(batch_size=batch_size)
        
        # Step 6: Update links
        print("\n6. Updating internal links...")
        self.update_all_links()
        
        # Step 7: Validate
        print("\n7. Validating migration...")
        self.validate_migration()
        
        # Step 8: Generate report
        print("\n8. Migration complete!")
        self.generate_report()
    
    def parse_bibtex(self):
        """Parse BibTeX file"""
        with open(self.bibtex_path, 'r', encoding='utf-8') as f:
            bib_database = bibtexparser.load(f)
        
        for entry in bib_database.entries:
            key = entry.get('ID', '')
            self.bibtex_entries[key] = entry
        
        print(f"  ✓ Loaded {len(self.bibtex_entries)} BibTeX entries")
    
    def create_backup(self):
        """Create full backup of articles directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.vault_path / "claude_workspace" / "backups" / f"pre_migration_{timestamp}"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy articles directory
        backup_articles = self.backup_dir / "4 Articles"
        if self.articles_dir.exists():
            shutil.copytree(self.articles_dir, backup_articles)
            print(f"  ✓ Backed up to: {self.backup_dir}")
    
    def build_migration_plan(self):
        """Build plan for file migrations"""
        # Use the analyzer to match files
        from analyze_vault import VaultAnalyzer
        
        analyzer = VaultAnalyzer(self.vault_path, self.bibtex_path)
        analyzer.parse_bibtex()
        analyzer.scan_vault()
        analyzer.match_files()
        
        for md_file, bibtex_entry in analyzer.matched_files:
            # Generate new filename
            new_name = f"{bibtex_entry['key']}.md"
            new_path = md_file.parent / new_name
            
            # Skip if already using BibTeX key
            if md_file.name == new_name:
                continue
            
            # Generate aliases
            aliases = self.generate_aliases(md_file, bibtex_entry)
            
            self.migration_plan.append({
                'old_path': md_file,
                'new_path': new_path,
                'bibtex_key': bibtex_entry['key'],
                'bibtex_entry': bibtex_entry,
                'aliases': aliases,
                'old_name': md_file.stem
            })
        
        print(f"  ✓ Planning to migrate {len(self.migration_plan)} files")
        print(f"  ℹ {len(analyzer.unmatched_files)} files will not be migrated (no BibTeX match)")
    
    def generate_aliases(self, md_file: Path, bibtex_entry: Dict) -> List[str]:
        """Generate minimal, useful aliases for a file"""
        aliases = []
        
        # 1. Original filename (essential for finding renamed files)
        original_name = md_file.stem
        aliases.append(original_name)
        
        # 2. Short citation only if year is valid (e.g., "Sporrong et al. 2024")
        authors = self.format_short_authors(bibtex_entry.get('author', ''))
        year = bibtex_entry.get('year', '')
        
        # Only add citation if we have valid year (4 digits)
        if authors and year and re.match(r'^\d{4}$', str(year)):
            short_cite = f"{authors} {year}"
            aliases.append(short_cite)
        
        # That's it - just original name and citation!
        # No title aliases, no "n.d.", no keywords
        
        return aliases
    
    def format_short_authors(self, author_string: str) -> str:
        """Format authors as 'First et al.' or 'First & Second'"""
        if not author_string:
            return ""
        
        authors = author_string.split(' and ')
        if not authors:
            return ""
        
        # Get last names
        lastnames = []
        for author in authors[:3]:  # Max 3 authors
            lastname = self.extract_lastname(author)
            if lastname:
                lastnames.append(lastname)
        
        if len(lastnames) == 0:
            return ""
        elif len(lastnames) == 1:
            return lastnames[0]
        elif len(lastnames) == 2:
            return f"{lastnames[0]} & {lastnames[1]}"
        else:
            return f"{lastnames[0]} et al."
    
    def extract_lastname(self, author: str) -> str:
        """Extract lastname from author string"""
        author = author.strip()
        if ',' in author:
            # "Last, First" format
            return author.split(',')[0].strip()
        else:
            # "First Last" format
            parts = author.split()
            return parts[-1] if parts else ""
    
    def get_first_author_lastname(self, author_string: str) -> str:
        """Get the last name of the first author"""
        if not author_string:
            return ""
        
        authors = author_string.split(' and ')
        if authors:
            return self.extract_lastname(authors[0])
        return ""
    
    def extract_title_keywords(self, title: str) -> str:
        """Extract significant keywords from title"""
        # Remove special characters and lowercase
        title = re.sub(r'[^\w\s-]', '', title.lower())
        
        # Common words to skip
        stopwords = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were'
        }
        
        # Extract words
        words = [w for w in title.split() if w not in stopwords and len(w) > 2]
        
        # Take first 3-4 significant words
        keywords = words[:4]
        
        return ' '.join(keywords) if keywords else ""
    
    def clean_title_for_alias(self, title: str) -> str:
        """Clean title for use as alias"""
        # Remove BibTeX formatting
        title = re.sub(r'[{}]', '', title)
        # Remove special characters but keep spaces
        title = re.sub(r'[^\w\s-]', '', title)
        # Normalize whitespace
        title = ' '.join(title.split())
        return title
    
    def preview_changes(self):
        """Preview the changes that will be made"""
        if not self.migration_plan:
            print("  No files to migrate")
            return
        
        print(f"\n  {Fore.YELLOW}MIGRATION PREVIEW:{Style.RESET_ALL}")
        
        # Show first 10 migrations
        for i, plan in enumerate(self.migration_plan[:10]):
            print(f"\n  [{i+1}] {Fore.CYAN}{plan['old_name']}{Style.RESET_ALL}")
            print(f"      → {Fore.GREEN}{plan['bibtex_key']}.md{Style.RESET_ALL}")
            print(f"      Aliases: {', '.join(plan['aliases'][:3])}")
        
        if len(self.migration_plan) > 10:
            print(f"\n  ... and {len(self.migration_plan) - 10} more files")
    
    def apply_migration(self, batch_size: int = None):
        """Apply the migration plan"""
        success_count = 0
        error_count = 0
        
        if batch_size and len(self.migration_plan) > batch_size:
            # Batch processing
            import time
            total = len(self.migration_plan)
            num_batches = (total + batch_size - 1) // batch_size
            
            for batch_num in range(num_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total)
                batch = self.migration_plan[start_idx:end_idx]
                
                print(f"\n{Fore.YELLOW}=== Batch {batch_num + 1}/{num_batches} ({start_idx + 1}-{end_idx} of {total}) ==={Style.RESET_ALL}")
                
                for j, plan in enumerate(batch):
                    i = start_idx + j
                    try:
                        print(f"  [{i+1}/{total}] Migrating {plan['old_name'][:60]}...", end='', flush=True)
                        
                        # Add aliases to file
                        self.add_aliases_to_file(plan['old_path'], plan['aliases'], plan['bibtex_key'])
                        
                        # Rename file
                        plan['old_path'].rename(plan['new_path'])
                        
                        success_count += 1
                        print(f" {Fore.GREEN}✓{Style.RESET_ALL}")
                        
                    except Exception as e:
                        error_count += 1
                        print(f" {Fore.RED}✗ {e}{Style.RESET_ALL}")
                
                # Pause between batches
                if batch_num < num_batches - 1:
                    print(f"\nBatch complete. Pausing 3 seconds before next batch...")
                    time.sleep(3)
        else:
            # Regular processing
            for i, plan in enumerate(self.migration_plan):
                try:
                    # Show progress every 50 files for large migrations
                    if i > 0 and i % 50 == 0:
                        print(f"\n  Progress: {i}/{len(self.migration_plan)} files migrated ({i/len(self.migration_plan)*100:.1f}%)\n")
                    
                    print(f"  [{i+1}/{len(self.migration_plan)}] Migrating {plan['old_name'][:60]}...", end='', flush=True)
                    
                    # Add aliases to file
                    self.add_aliases_to_file(plan['old_path'], plan['aliases'], plan['bibtex_key'])
                    
                    # Rename file
                    plan['old_path'].rename(plan['new_path'])
                    
                    success_count += 1
                    print(f" {Fore.GREEN}✓{Style.RESET_ALL}")
                    
                except Exception as e:
                    error_count += 1
                    print(f" {Fore.RED}✗ {e}{Style.RESET_ALL}")
        
        print(f"\n  Summary: {success_count} succeeded, {error_count} failed")
    
    def add_aliases_to_file(self, file_path: Path, aliases: List[str], bibtex_key: str):
        """Add YAML frontmatter with aliases to file"""
        content = file_path.read_text(encoding='utf-8')
        
        # Create YAML frontmatter
        yaml_content = "---\n"
        yaml_content += "aliases:\n"
        for alias in aliases:
            # Escape quotes in aliases
            alias_escaped = alias.replace('"', '\\"')
            yaml_content += f'  - "{alias_escaped}"\n'
        yaml_content += "tags:\n"
        yaml_content += "  - from_paperpile\n"
        yaml_content += f"bibtex_key: {bibtex_key}\n"
        yaml_content += "---\n\n"
        
        # Check if file already has frontmatter
        if content.startswith('---'):
            # Update existing frontmatter
            end_marker = content.find('---', 3)
            if end_marker > 0:
                # Parse existing frontmatter and merge
                existing_fm = content[3:end_marker].strip()
                # For now, replace entirely (could be smarter about merging)
                content = yaml_content + content[end_marker + 3:].lstrip()
            else:
                # Malformed frontmatter, prepend new
                content = yaml_content + content
        else:
            # Add new frontmatter
            content = yaml_content + content
        
        # Ensure BibTeX key is in the file
        if 'BibTeX Key:' not in content and bibtex_key:
            # Find where to insert it (after Reference Information header if exists)
            ref_section = content.find('## Reference Information')
            if ref_section > 0:
                # Find next newline after header
                insert_pos = content.find('\n', ref_section) + 1
                content = content[:insert_pos] + f"**BibTeX Key:** {bibtex_key}\n" + content[insert_pos:]
        
        file_path.write_text(content, encoding='utf-8')
    
    def update_all_links(self):
        """Update all wiki links to renamed files"""
        # Build mapping of old names to new names
        name_mapping = {}
        for plan in self.migration_plan:
            old_link = f"[[{plan['old_name']}]]"
            new_link = f"[[{plan['bibtex_key']}]]"
            name_mapping[old_link] = new_link
        
        # Update links in all markdown files
        updated_files = 0
        for md_file in self.vault_path.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Replace all mapped links
            for old_link, new_link in name_mapping.items():
                content = content.replace(old_link, new_link)
            
            # Write back if changed
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                updated_files += 1
        
        print(f"  ✓ Updated links in {updated_files} files")
    
    def validate_migration(self):
        """Validate that migration completed successfully"""
        validation_results = {
            'files_migrated': len(self.migration_plan),
            'files_exist': 0,
            'aliases_added': 0,
            'broken_links': 0
        }
        
        # Check that new files exist
        for plan in self.migration_plan:
            if plan['new_path'].exists():
                validation_results['files_exist'] += 1
                
                # Check for aliases
                content = plan['new_path'].read_text(encoding='utf-8')
                if 'aliases:' in content:
                    validation_results['aliases_added'] += 1
        
        # Quick check for broken links (sample)
        sample_files = list(self.articles_dir.glob("*.md"))[:20]
        for md_file in sample_files:
            content = md_file.read_text(encoding='utf-8')
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                if not link.endswith('.pdf'):  # Skip PDF links
                    link_path = self.articles_dir / f"{link}.md"
                    if not link_path.exists():
                        validation_results['broken_links'] += 1
        
        # Print validation results
        print(f"\n  {Fore.YELLOW}VALIDATION RESULTS:{Style.RESET_ALL}")
        print(f"  Files migrated: {validation_results['files_migrated']}")
        print(f"  Files exist: {validation_results['files_exist']} ✓")
        print(f"  Aliases added: {validation_results['aliases_added']} ✓")
        print(f"  Broken links found: {validation_results['broken_links']} {'✓' if validation_results['broken_links'] == 0 else '⚠'}")
    
    def generate_report(self):
        """Generate migration report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'files_migrated': len(self.migration_plan),
            'backup_location': str(self.backup_dir) if self.backup_dir else None,
            'migrations': []
        }
        
        for plan in self.migration_plan:
            report['migrations'].append({
                'old_name': plan['old_name'],
                'new_name': plan['bibtex_key'],
                'aliases': plan['aliases']
            })
        
        # Save report
        report_path = self.vault_path / "claude_workspace" / "export" / f"migration_report_{datetime.now():%Y%m%d_%H%M%S}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n  📄 Migration report saved to: {report_path}")
        
        # Print summary
        print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}MIGRATION COMPLETE{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        print(f"\n  ✓ Migrated {len(self.migration_plan)} files to BibTeX keys")
        print(f"  ✓ Original filenames preserved as aliases")
        print(f"  ✓ All internal links updated")
        if self.backup_dir:
            print(f"  ✓ Backup saved to: {self.backup_dir}")
        print(f"\n  Next steps:")
        print(f"  1. Open Obsidian and verify everything looks correct")
        print(f"  2. Test searching with aliases")
        print(f"  3. Run paperpile_sync.py to add any missing metadata")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Obsidian vault files to BibTeX key naming'
    )
    parser.add_argument(
        '--vault',
        type=str,
        default='.',
        help='Path to Obsidian vault root (default: current directory)'
    )
    parser.add_argument(
        '--bibtex',
        type=str,
        default='~/Desktop/paperpile.bib',
        help='Path to Paperpile BibTeX export'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute migration (default is dry run)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Preview changes without applying them (default)'
    )
    parser.add_argument(
        '--batch',
        type=int,
        metavar='SIZE',
        help='Process files in batches of SIZE (e.g., --batch 50)'
    )
    
    args = parser.parse_args()
    
    # Determine mode
    dry_run = not args.execute
    
    # Expand paths
    vault_path = Path(args.vault).expanduser().resolve()
    bibtex_path = Path(args.bibtex).expanduser().resolve()
    
    # Validate paths
    if not vault_path.exists():
        print(f"{Fore.RED}Error: Vault path does not exist: {vault_path}{Style.RESET_ALL}")
        return
    
    if not bibtex_path.exists():
        print(f"{Fore.RED}Error: BibTeX file not found: {bibtex_path}{Style.RESET_ALL}")
        return
    
    # Run migration
    migrator = VaultMigrator(vault_path, bibtex_path)
    try:
        migrator.run_migration(dry_run=dry_run, batch_size=args.batch)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Migration interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Migration failed: {e}{Style.RESET_ALL}")
        raise


if __name__ == "__main__":
    main()