#!/usr/bin/env python3
"""
Merge duplicate tags based on similarity analysis
"""

import os
import sys
from pathlib import Path
import argparse

# Add the scripts directory to the path so we can import obsidian_tag_manager
sys.path.append(str(Path(__file__).parent))

from obsidian_tag_manager import ObsidianTagManager

# Define the tag merges based on the similarity analysis
TAG_MERGES = [
    # Format: (old_tag, new_tag, reason)
    ('on-line_teacher_communities', 'online_teacher_communities', 'Remove hyphen in "online"'),
    ('socio-cultural_perspective', 'sociocultural_perspective', 'Remove hyphen'),
    ('socio-cultural_theory', 'sociocultural_theory', 'Remove hyphen'),
    ('pre-service_teachers', 'preservice_teachers', 'Remove hyphen'),
    ('metaregularities', 'meta_regularities', 'Add underscore for clarity'),
    ('maskin inlärning', 'maskininlärning', 'Remove space (Swedish)'),
    ('massively_open_online_courses', 'massive_open_online_courses', 'Standardize to common form'),
    ('digitaldivide', 'digital_divide', 'Add underscore'),
    ('k-12_education', 'k12_education', 'Remove hyphen for consistency'),
    ('artificial_intelligence_education', 'artificial_intelligence_in_education', 'Add "in" for clarity'),
    ('design-based_research', 'design_based_research', 'Remove hyphen'),
    ('agi_ethics', 'ai_ethics', 'Standardize to AI (not AGI)'),
    ('game-based_learning', 'game_based_learning', 'Remove hyphen'),
    ('cerratto-pargman_t', 'cerratto_pargman_t', 'Remove hyphen in name'),
    ('dialogical_approach', 'dialogic_approach', 'Use standard form'),
    ('education_policy', 'educational_policy', 'Use adjective form'),
    ('behavior_change', 'behavioral_change', 'Use adjective form'),
    ('machine learning', 'machine_learning', 'Already fixed by standardization'),
    ('neural network', 'neural_network', 'Already fixed by standardization'),
    ('educationtechnology', 'educational_technology', 'Add underscore and fix spelling'),
]

# Additional merges for common standardizations
ADDITIONAL_MERGES = [
    ('massive_open_online_courses', 'moocs', 'Use common abbreviation'),
    ('k12_education', 'k_12_education', 'Standardize K-12 format'),
    ('k12', 'k_12', 'Standardize K-12 format'),
    ('preservice_teacher', 'pre_service_teacher', 'Consistency with plural form'),
    ('inservice_teacher', 'in_service_teacher', 'Consistency'),
    ('sociocultural', 'socio_cultural', 'Consistency across variants'),
]

def main():
    parser = argparse.ArgumentParser(description='Merge duplicate tags in Obsidian vault')
    parser.add_argument('--vault-path', default='.',
                       help='Path to Obsidian vault (default: current directory)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--apply', action='store_true',
                       help='Apply the merges (use with --force to actually make changes)')
    parser.add_argument('--force', action='store_true',
                       help='Actually apply changes (not dry-run)')
    parser.add_argument('--additional', action='store_true',
                       help='Include additional standardization merges')
    
    args = parser.parse_args()
    
    if not args.apply:
        parser.print_help()
        print("\nThis script will merge the following duplicate tags:")
        print("\nPrimary merges (from similarity analysis):")
        for old, new, reason in TAG_MERGES:
            print(f"  '{old}' → '{new}' ({reason})")
        
        if args.additional:
            print("\nAdditional standardization merges:")
            for old, new, reason in ADDITIONAL_MERGES:
                print(f"  '{old}' → '{new}' ({reason})")
        
        print("\nUse --apply to perform these merges (dry-run by default)")
        print("Use --apply --force to actually make changes")
        return
    
    try:
        manager = ObsidianTagManager(args.vault_path)
        
        # Determine which merges to apply
        merges_to_apply = TAG_MERGES.copy()
        if args.additional:
            merges_to_apply.extend(ADDITIONAL_MERGES)
        
        # Apply merges
        dry_run = not args.force or args.dry_run
        
        if dry_run:
            print("\n🔍 DRY RUN - No changes will be made")
        else:
            print("\n⚠️  Applying tag merges...")
        
        total_changes = 0
        errors = []
        successful_merges = []
        
        for old_tag, new_tag, reason in merges_to_apply:
            print(f"\n{'Would merge' if dry_run else 'Merging'}: '{old_tag}' → '{new_tag}'")
            print(f"  Reason: {reason}")
            
            result = manager.merge_tags(old_tag, new_tag, dry_run=dry_run)
            
            if 'error' in result:
                if "not found" not in result['error']:  # Skip "not found" errors
                    errors.append(f"{old_tag}: {result['error']}")
            else:
                total_changes += result['files_affected']
                if result['files_affected'] > 0:
                    successful_merges.append({
                        'old': old_tag,
                        'new': new_tag,
                        'files': result['files_affected']
                    })
                    print(f"  Files affected: {result['files_affected']}")
        
        # Summary
        print(f"\n{'='*60}")
        print(f"\n{'Would make' if dry_run else 'Made'} changes to {total_changes} file occurrences")
        
        if successful_merges:
            print(f"\nSuccessful merges: {len(successful_merges)}")
            for merge in successful_merges[:10]:
                print(f"  '{merge['old']}' → '{merge['new']}' ({merge['files']} files)")
            if len(successful_merges) > 10:
                print(f"  ... and {len(successful_merges) - 10} more")
        
        if errors:
            print(f"\nErrors encountered: {len(errors)}")
            for error in errors[:5]:
                print(f"  {error}")
        
        if dry_run:
            print("\nTo apply these changes, run with --apply --force")
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())