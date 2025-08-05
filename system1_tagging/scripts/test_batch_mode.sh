#!/bin/bash

# Test script for batch tagging mode

echo "🧪 Testing Batch Tagging Mode"
echo "============================"

# Change to vault directory
cd "/Users/niklaskarlsson/Obsidian Sandbox/Research Hub"

# First, let's see how many untagged articles we have
echo -e "\n1. Finding untagged articles..."
python3 claude_workspace/scripts/tagging/obsidian_article_tagger.py --find-untagged

# Process 3 articles in batch mode
echo -e "\n2. Running batch mode for 3 articles..."
python3 claude_workspace/scripts/tagging/obsidian_article_tagger.py --batch --limit 3

# Check the suggestions directory
echo -e "\n3. Checking saved suggestions..."
ls -la claude_workspace/export/tagging/tag_suggestions/suggestion_*.json 2>/dev/null | wc -l | xargs -I {} echo "Found {} suggestion files"

echo -e "\n✅ Test complete!"
echo "To review suggestions, run:"
echo "python3 claude_workspace/scripts/tagging/obsidian_article_tagger.py --review"