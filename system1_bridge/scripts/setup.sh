#!/bin/bash
# Setup script for System 1 - Paperpile-Obsidian Bridge

echo "Setting up System 1..."

# Make Python scripts executable
chmod +x analyze_vault.py
chmod +x migrate_to_bibtex_keys.py
chmod +x paperpile_sync.py

# Check for required Python packages
echo "Checking Python dependencies..."
python3 -c "import bibtexparser" 2>/dev/null || echo "⚠️  Please install bibtexparser: pip install bibtexparser"
python3 -c "import colorama" 2>/dev/null || echo "⚠️  Please install colorama: pip install colorama"

echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  1. First analyze your vault:"
echo "     python3 analyze_vault.py --vault . --bibtex ~/Desktop/paperpile.bib"
echo ""
echo "  2. Then migrate to BibTeX keys:"
echo "     python3 migrate_to_bibtex_keys.py --dry-run"
echo "     python3 migrate_to_bibtex_keys.py --execute"
echo ""
echo "  3. Finally, sync with Paperpile:"
echo "     python3 paperpile_sync.py --test 5  # Test with 5 articles"
echo "     python3 paperpile_sync.py           # Full sync"