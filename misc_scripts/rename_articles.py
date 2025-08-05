#!/usr/bin/env python3
import os
import re
import shutil

def parse_filename(filename):
    """Parse different filename patterns to extract author(s), year, and title."""
    
    # Remove .md extension
    if filename.endswith('.md'):
        base_name = filename[:-3]
    else:
        return None
    
    # Pattern 1: Author_Year_Title (underscore separated)
    pattern1 = r'^(.+?)_(\d{4})_(.+)$'
    match1 = re.match(pattern1, base_name)
    if match1:
        authors = match1.group(1)
        year = match1.group(2)
        title = match1.group(3).replace('-', ' ')
        return authors, year, title
    
    # Pattern 2: Author (Year). Title
    pattern2 = r'^(.+?)\s*\((\d{4})\)\.\s*(.+)$'
    match2 = re.match(pattern2, base_name)
    if match2:
        authors = match2.group(1)
        year = match2.group(2)
        title = match2.group(3)
        return authors, year, title
    
    # Pattern 3: Author_n.d._Title (no date)
    pattern3 = r'^(.+?)_n\.d\._(.+)$'
    match3 = re.match(pattern3, base_name)
    if match3:
        authors = match3.group(1)
        year = 'n.d.'
        title = match3.group(2).replace('-', ' ')
        return authors, year, title
    
    return None

def format_authors(authors_str):
    """Format author names properly with commas and ampersands."""
    # Replace underscores with spaces if present
    authors_str = authors_str.replace('_', ' ')
    
    # Split by common separators
    if ' & ' in authors_str:
        author_list = authors_str.split(' & ')
    elif ' and ' in authors_str:
        author_list = authors_str.split(' and ')
    elif ',' in authors_str:
        author_list = [a.strip() for a in authors_str.split(',')]
    else:
        # Single author
        return authors_str.strip()
    
    # Format multiple authors
    if len(author_list) == 1:
        return author_list[0].strip()
    elif len(author_list) == 2:
        return f"{author_list[0].strip()} & {author_list[1].strip()}"
    else:
        # More than 2 authors
        formatted = ", ".join([a.strip() for a in author_list[:-1]])
        formatted += f" & {author_list[-1].strip()}"
        return formatted

def create_new_filename(authors, year, title):
    """Create the new standardized filename."""
    formatted_authors = format_authors(authors)
    # Clean up the title - remove extra spaces and ensure proper capitalization
    title = ' '.join(title.split())  # Remove extra spaces
    return f"{formatted_authors} ({year}). {title}.md"

def main():
    # Directory containing the articles
    directory = "/Users/niklaskarlsson/Obsidian Sandbox/Research Hub/4 Articles/Test articles abstracts"
    
    # Create a mapping of old to new filenames
    rename_map = {}
    errors = []
    
    print("Analyzing files...")
    print("-" * 80)
    
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            parsed = parse_filename(filename)
            if parsed:
                authors, year, title = parsed
                new_filename = create_new_filename(authors, year, title)
                
                # Check if new filename already exists or conflicts
                if new_filename != filename:
                    rename_map[filename] = new_filename
                    print(f"OLD: {filename}")
                    print(f"NEW: {new_filename}")
                    print()
            else:
                errors.append(filename)
    
    if errors:
        print("\nCould not parse these files:")
        for error in errors:
            print(f"  - {error}")
    
    print("-" * 80)
    print(f"\nFound {len(rename_map)} files to rename.")
    
    if rename_map:
        response = input("\nDo you want to proceed with renaming? (yes/no): ")
        
        if response.lower() == 'yes':
            print("\nRenaming files...")
            for old_name, new_name in rename_map.items():
                old_path = os.path.join(directory, old_name)
                new_path = os.path.join(directory, new_name)
                
                try:
                    os.rename(old_path, new_path)
                    print(f"✓ Renamed: {old_name} -> {new_name}")
                except Exception as e:
                    print(f"✗ Error renaming {old_name}: {str(e)}")
            
            print("\nRenaming complete!")
        else:
            print("\nRenaming cancelled.")

if __name__ == "__main__":
    main()