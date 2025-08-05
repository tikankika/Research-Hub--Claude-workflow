#!/bin/bash

# Process 5 articles one by one with the article tagger

echo "🔄 Processing 5 articles sequentially"
echo "===================================="

cd "/Users/niklaskarlsson/Obsidian Sandbox/Research Hub"

# First, show how many untagged articles we have
echo -e "\n📊 Checking untagged articles..."
python3 claude_workspace/scripts/tagging/obsidian_article_tagger.py --find-untagged | grep "Found"

echo -e "\n🚀 Starting to process 5 articles...\n"

# Process 5 articles
for i in {1..5}
do
    echo -e "\n=========================================="
    echo "📄 Article $i of 5"
    echo "=========================================="
    
    # Run the article tagger for one article
    python3 claude_workspace/scripts/tagging/obsidian_article_tagger.py --limit 1
    
    echo -e "\n❓ What would you like to do?"
    echo "1) Apply tags (if suggestions were shown)"
    echo "2) Skip to next article"
    echo "3) Exit"
    
    read -p "Choice (1/2/3): " choice
    
    case $choice in
        1)
            echo "📝 Applying tags..."
            python3 claude_workspace/scripts/tagging/obsidian_article_tagger.py --auto-apply --limit 1
            ;;
        2)
            echo "⏭️  Skipping to next article..."
            ;;
        3)
            echo "👋 Exiting..."
            break
            ;;
        *)
            echo "Invalid choice, skipping..."
            ;;
    esac
    
    # Brief pause between articles
    sleep 1
done

echo -e "\n✅ Session complete!"

# Show remaining untagged
echo -e "\n📊 Final status:"
python3 claude_workspace/scripts/tagging/obsidian_article_tagger.py --find-untagged | grep "Found"