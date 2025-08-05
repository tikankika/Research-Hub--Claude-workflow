#!/usr/bin/env python3
"""
Analyze Obsidian vault to prepare for Paperpile synchronization.
Matches existing files to BibTeX entries and reports on migration readiness.
"""

import re
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
import bibtexparser
from colorama import init, Fore, Style

init(autoreset=True)

class VaultAnalyzer:
    def __init__(self, vault_path: str, bibtex_path: str):
        self.vault_path = Path(vault_path)
        self.bibtex_path = Path(bibtex_path)
        self.articles_dir = self.vault_path / "4 Articles"
        self.pdf_dir = self.vault_path / "9 Paperpile"
        
        # Analysis results
        self.bibtex_entries = {}
        self.vault_files = []
        self.matched_files = []
        self.unmatched_files = []
        self.pdf_links = {}
        self.content_analysis = {}
        
    def run_analysis(self):
        """Run complete vault analysis"""
        print(f"\n{Fore.CYAN}=== VAULT ANALYSIS ==={Style.RESET_ALL}\n")
        
        # Step 1: Parse BibTeX
        print("1. Parsing BibTeX file...")
        self.parse_bibtex()
        
        # Step 2: Scan vault
        print("2. Scanning Obsidian vault...")
        self.scan_vault()
        
        # Step 3: Match files
        print("3. Matching files to BibTeX entries...")
        self.match_files()
        
        # Step 4: Analyze content
        print("4. Analyzing file content...")
        self.analyze_content()
        
        # Step 5: Check PDF links
        print("5. Checking PDF links...")
        self.check_pdf_links()
        
        # Step 6: Generate report
        print("\n6. Generating report...")
        return self.generate_report()
    
    def parse_bibtex(self):
        """Parse BibTeX file and extract all entries"""
        try:
            with open(self.bibtex_path, 'r', encoding='utf-8') as f:
                bib_database = bibtexparser.load(f)
            
            for entry in bib_database.entries:
                key = entry.get('ID', '')
                self.bibtex_entries[key] = {
                    'key': key,
                    'type': entry.get('ENTRYTYPE', 'article'),
                    'title': self.clean_title(entry.get('title', '')),
                    'author': entry.get('author', ''),
                    'year': entry.get('year', 'n.d.'),
                    'journal': entry.get('journaltitle', entry.get('journal', '')),
                    'doi': entry.get('doi', ''),
                    'file': entry.get('file', ''),
                    'note': entry.get('note', ''),
                    'abstract': entry.get('abstract', ''),
                    'raw_entry': entry
                }
            
            print(f"  ✓ Found {len(self.bibtex_entries)} BibTeX entries")
            
        except Exception as e:
            print(f"  {Fore.RED}✗ Error parsing BibTeX: {e}{Style.RESET_ALL}")
            raise
    
    def clean_title(self, title: str) -> str:
        """Clean BibTeX title formatting"""
        # Remove BibTeX formatting
        title = re.sub(r'[{}]', '', title)
        title = re.sub(r'\s+', ' ', title)
        return title.strip()
    
    def scan_vault(self):
        """Scan vault for markdown files"""
        if not self.articles_dir.exists():
            print(f"  {Fore.YELLOW}⚠ Articles directory not found: {self.articles_dir}{Style.RESET_ALL}")
            return
        
        self.vault_files = list(self.articles_dir.glob("*.md"))
        print(f"  ✓ Found {len(self.vault_files)} markdown files in /4 Articles/")
    
    def match_files(self):
        """Match vault files to BibTeX entries"""
        for md_file in self.vault_files:
            match = self.find_bibtex_match(md_file)
            if match:
                self.matched_files.append((md_file, match))
            else:
                self.unmatched_files.append(md_file)
        
        print(f"  ✓ Matched: {len(self.matched_files)} files")
        print(f"  ⚠ Unmatched: {len(self.unmatched_files)} files")
    
    def find_bibtex_match(self, md_file: Path) -> Optional[Dict]:
        """Find matching BibTeX entry for a markdown file"""
        content = md_file.read_text(encoding='utf-8')
        
        # Strategy 1: Look for BibTeX key in file
        key_match = re.search(r'BibTeX Key:\s*(\S+)', content)
        if key_match:
            key = key_match.group(1)
            if key in self.bibtex_entries:
                return self.bibtex_entries[key]
        
        # Strategy 2: Extract title from first heading
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            file_title = title_match.group(1).strip()
            # Try to match against BibTeX titles
            for key, entry in self.bibtex_entries.items():
                if self.titles_match(file_title, entry['title']):
                    return entry
        
        # Strategy 3: Extract authors and year from filename
        filename = md_file.stem
        year_match = re.search(r'\((\d{4})\)', filename)
        if year_match:
            year = year_match.group(1)
            # Extract potential author names
            author_part = filename.split('(')[0].strip()
            
            for key, entry in self.bibtex_entries.items():
                if entry['year'] == year:
                    # Check if authors match
                    if self.authors_match(author_part, entry['author']):
                        return entry
        
        return None
    
    def titles_match(self, title1: str, title2: str) -> bool:
        """Check if two titles match (fuzzy matching)"""
        # Normalize titles
        def normalize(t):
            t = re.sub(r'[^\w\s]', '', t.lower())
            t = re.sub(r'\s+', ' ', t)
            return t.strip()
        
        t1 = normalize(title1)
        t2 = normalize(title2)
        
        # Exact match
        if t1 == t2:
            return True
        
        # Check if one contains the other (for subtitles)
        if t1 in t2 or t2 in t1:
            return True
        
        # Check word overlap (at least 70% of words match)
        words1 = set(t1.split())
        words2 = set(t2.split())
        if words1 and words2:
            overlap = len(words1 & words2) / min(len(words1), len(words2))
            return overlap >= 0.7
        
        return False
    
    def authors_match(self, filename_authors: str, bibtex_authors: str) -> bool:
        """Check if authors from filename match BibTeX authors"""
        # Extract last names from BibTeX authors
        bibtex_lastnames = []
        for author in bibtex_authors.split(' and '):
            if ',' in author:
                lastname = author.split(',')[0].strip()
            else:
                parts = author.strip().split()
                if parts:
                    lastname = parts[-1]
                else:
                    continue  # Skip empty author
            bibtex_lastnames.append(lastname.lower())
        
        # Check if filename contains these names
        filename_lower = filename_authors.lower()
        matches = sum(1 for name in bibtex_lastnames if name in filename_lower)
        
        return matches >= min(2, len(bibtex_lastnames))  # At least 2 or all authors
    
    def analyze_content(self):
        """Analyze content of matched files"""
        for md_file, bibtex_entry in self.matched_files[:5]:  # Sample first 5
            content = md_file.read_text(encoding='utf-8')
            
            analysis = {
                'has_bibtex_key': bool(re.search(r'BibTeX Key:', content)),
                'has_doi': bool(re.search(r'DOI:|doi\.org', content)),
                'has_abstract': bool(re.search(r'## Abstract', content)),
                'has_tags': bool(re.search(r'#\w+', content)),
                'has_user_notes': bool(re.search(r'## (My )?Notes|## Ideas|## Connections', content)),
                'has_paperpile_marker': bool(re.search(r'Imported from Paperpile', content)),
                'has_pdf_link': bool(re.search(r'\[\[.*\.pdf\]\]', content)),
                'content_sections': self.extract_sections(content)
            }
            
            self.content_analysis[md_file.name] = analysis
    
    def extract_sections(self, content: str) -> List[str]:
        """Extract section headers from content"""
        headers = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        return headers
    
    def check_pdf_links(self):
        """Check PDF links in files"""
        pdf_check_results = {
            'working': 0,
            'broken': 0,
            'missing': 0,
            'examples': []
        }
        
        for md_file in self.vault_files[:10]:  # Check first 10 files
            content = md_file.read_text(encoding='utf-8')
            pdf_links = re.findall(r'\[\[([^\]]+\.pdf)\]\]', content)
            
            for pdf_link in pdf_links:
                # Check if PDF exists
                if pdf_link.startswith('../'):
                    # Relative path from /4 Articles/
                    pdf_path = self.vault_path / pdf_link[3:]
                else:
                    pdf_path = self.vault_path / pdf_link
                
                if pdf_path.exists():
                    pdf_check_results['working'] += 1
                else:
                    pdf_check_results['broken'] += 1
                    if len(pdf_check_results['examples']) < 3:
                        pdf_check_results['examples'].append({
                            'file': md_file.name,
                            'link': pdf_link,
                            'expected_path': str(pdf_path)
                        })
        
        self.pdf_links = pdf_check_results
    
    def generate_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        report = {
            'summary': {
                'bibtex_entries': len(self.bibtex_entries),
                'vault_files': len(self.vault_files),
                'matched_files': len(self.matched_files),
                'unmatched_files': len(self.unmatched_files),
                'match_rate': f"{len(self.matched_files) / len(self.vault_files) * 100:.1f}%" if self.vault_files else "0%"
            },
            'pdf_links': self.pdf_links,
            'content_patterns': self.analyze_content_patterns(),
            'migration_readiness': self.assess_migration_readiness(),
            'unmatched_files': [f.name for f in self.unmatched_files[:10]],  # First 10
            'recommendations': self.generate_recommendations()
        }
        
        # Save detailed report
        report_path = self.vault_path / Path(__file__).parent.parent / "export" / f"vault_analysis_{datetime.now():%Y%m%d_%H%M%S}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.print_report(report)
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        return report
    
    def analyze_content_patterns(self) -> Dict:
        """Analyze patterns in content structure"""
        if not self.content_analysis:
            return {'sample_size': 0}
        
        patterns = {
            'sample_size': len(self.content_analysis),
            'has_bibtex_key': sum(1 for a in self.content_analysis.values() if a['has_bibtex_key']),
            'has_user_notes': sum(1 for a in self.content_analysis.values() if a['has_user_notes']),
            'has_paperpile_marker': sum(1 for a in self.content_analysis.values() if a['has_paperpile_marker']),
            'common_sections': self.find_common_sections()
        }
        
        return patterns
    
    def find_common_sections(self) -> List[str]:
        """Find most common section headers"""
        all_sections = []
        for analysis in self.content_analysis.values():
            all_sections.extend(analysis['content_sections'])
        
        # Count occurrences
        section_counts = {}
        for section in all_sections:
            section_counts[section] = section_counts.get(section, 0) + 1
        
        # Return top 5
        sorted_sections = sorted(section_counts.items(), key=lambda x: x[1], reverse=True)
        return [s[0] for s in sorted_sections[:5]]
    
    def assess_migration_readiness(self) -> Dict:
        """Assess readiness for migration"""
        readiness = {
            'score': 0,
            'factors': {}
        }
        
        # Factor 1: Match rate
        match_rate = len(self.matched_files) / len(self.vault_files) if self.vault_files else 0
        readiness['factors']['match_rate'] = {
            'value': f"{match_rate * 100:.1f}%",
            'status': '✅' if match_rate > 0.8 else '⚠️' if match_rate > 0.5 else '❌'
        }
        if match_rate > 0.8:
            readiness['score'] += 25
        
        # Factor 2: PDF links
        if self.pdf_links.get('working', 0) > 0:
            broken_rate = self.pdf_links['broken'] / (self.pdf_links['working'] + self.pdf_links['broken'])
            readiness['factors']['pdf_links'] = {
                'value': f"{broken_rate * 100:.1f}% broken",
                'status': '✅' if broken_rate < 0.1 else '⚠️' if broken_rate < 0.3 else '❌'
            }
            if broken_rate < 0.1:
                readiness['score'] += 25
        
        # Factor 3: BibTeX keys present
        if self.content_analysis:
            key_rate = self.analyze_content_patterns()['has_bibtex_key'] / len(self.content_analysis)
            readiness['factors']['bibtex_keys'] = {
                'value': f"{key_rate * 100:.1f}% have keys",
                'status': '✅' if key_rate > 0.5 else '⚠️' if key_rate > 0.2 else '❌'
            }
            if key_rate > 0.5:
                readiness['score'] += 25
        
        # Factor 4: User content
        if self.content_analysis:
            user_content_rate = self.analyze_content_patterns()['has_user_notes'] / len(self.content_analysis)
            readiness['factors']['user_content'] = {
                'value': f"{user_content_rate * 100:.1f}% have user notes",
                'status': '✅ Important to preserve'
            }
            readiness['score'] += 25
        
        # Overall assessment
        if readiness['score'] >= 75:
            readiness['overall'] = '✅ Ready for migration'
        elif readiness['score'] >= 50:
            readiness['overall'] = '⚠️ Migration possible with care'
        else:
            readiness['overall'] = '❌ Needs preparation'
        
        return readiness
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on match rate
        match_rate = len(self.matched_files) / len(self.vault_files) if self.vault_files else 0
        if match_rate < 0.8:
            recommendations.append(f"Review {len(self.unmatched_files)} unmatched files - they may need manual matching")
        
        # Based on PDF links
        if self.pdf_links.get('broken', 0) > 0:
            recommendations.append(f"Fix {self.pdf_links['broken']} broken PDF links before migration")
        
        # Based on content analysis
        if self.content_analysis:
            patterns = self.analyze_content_patterns()
            if patterns['has_bibtex_key'] < patterns['sample_size'] * 0.5:
                recommendations.append("Many files lack BibTeX keys - migration will rely on title/author matching")
            
            if patterns['has_user_notes'] > patterns['sample_size'] * 0.3:
                recommendations.append("Significant user content detected - will be preserved during migration")
        
        # General recommendations
        recommendations.append("Create a full backup before migration")
        recommendations.append("Test migration with 5-10 files first")
        
        return recommendations
    
    def print_report(self, report: Dict):
        """Print formatted report to console"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}VAULT ANALYSIS REPORT{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        # Summary
        print(f"{Fore.YELLOW}📊 SUMMARY{Style.RESET_ALL}")
        print(f"  BibTeX entries: {report['summary']['bibtex_entries']}")
        print(f"  Vault files: {report['summary']['vault_files']}")
        print(f"  Matched: {report['summary']['matched_files']} ({report['summary']['match_rate']})")
        print(f"  Unmatched: {report['summary']['unmatched_files']}")
        
        # Migration readiness
        print(f"\n{Fore.YELLOW}🚀 MIGRATION READINESS{Style.RESET_ALL}")
        readiness = report['migration_readiness']
        for factor, details in readiness['factors'].items():
            print(f"  {details['status']} {factor}: {details['value']}")
        print(f"\n  {readiness['overall']} (Score: {readiness['score']}/100)")
        
        # PDF Links
        print(f"\n{Fore.YELLOW}🔗 PDF LINKS{Style.RESET_ALL}")
        print(f"  Working: {report['pdf_links']['working']}")
        print(f"  Broken: {report['pdf_links']['broken']}")
        if report['pdf_links']['examples']:
            print(f"  Examples of broken links:")
            for ex in report['pdf_links']['examples']:
                print(f"    - {ex['file']}: {ex['link']}")
        
        # Content patterns
        if report['content_patterns'].get('sample_size', 0) > 0:
            print(f"\n{Fore.YELLOW}📝 CONTENT PATTERNS (sample of {report['content_patterns']['sample_size']}){Style.RESET_ALL}")
            patterns = report['content_patterns']
            print(f"  Files with BibTeX keys: {patterns['has_bibtex_key']}")
            print(f"  Files with user notes: {patterns['has_user_notes']}")
            print(f"  Files from Paperpile: {patterns['has_paperpile_marker']}")
            if patterns['common_sections']:
                print(f"  Common sections: {', '.join(patterns['common_sections'][:3])}")
        
        # Unmatched files
        if report['unmatched_files']:
            print(f"\n{Fore.YELLOW}❓ UNMATCHED FILES (first 10){Style.RESET_ALL}")
            for filename in report['unmatched_files'][:10]:
                print(f"  - {filename}")
        
        # Recommendations
        print(f"\n{Fore.YELLOW}💡 RECOMMENDATIONS{Style.RESET_ALL}")
        for rec in report['recommendations']:
            print(f"  • {rec}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Obsidian vault for Paperpile synchronization'
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
        help='Path to Paperpile BibTeX export (default: ~/Desktop/paperpile.bib)'
    )
    
    args = parser.parse_args()
    
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
    
    # Run analysis
    analyzer = VaultAnalyzer(vault_path, bibtex_path)
    try:
        report = analyzer.run_analysis()
    except Exception as e:
        print(f"\n{Fore.RED}Analysis failed: {e}{Style.RESET_ALL}")
        raise


if __name__ == "__main__":
    main()