#!/bin/bash

# Fix Markdown Formatting Script
# Addresses common markdown linting issues across documentation

echo "🔧 Fixing markdown formatting issues across documentation..."

# Function to fix common markdown issues
fix_markdown_issues() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "⚠️  File not found: $file"
        return 1
    fi
    
    echo "📝 Processing: $file"
    
    # Create backup
    cp "$file" "$file.backup"
    
    # Fix issues using sed
    sed -i '
        # Add blank lines around headings
        /^#/ {
            i\

            a\

        }
        
        # Add blank lines around lists
        /^[[:space:]]*[-*+]/ {
            i\

        }
        
        # Add blank lines around fenced code blocks
        /^```/ {
            i\

            a\

        }
        
        # Remove trailing spaces
        s/[[:space:]]*$//
        
        # Fix bare URLs by wrapping in <>
        s|\(http[s]*://[^[:space:]]*\)|(<\1>)|g
        
    ' "$file"
    
    echo "✅ Fixed: $file"
}

# List of documentation files to fix
files=(
    "README.md"
    "CHANGELOG.md"
    "CONTRIBUTING.md"
    "DEPLOYMENT.md"
    "SECURITY_STATUS_SUMMARY.md"
    "business_intel_scraper/README.md"
    "business_intel_scraper/frontend/README.md"
    "docs/README.md"
)

# Fix each file
for file in "${files[@]}"; do
    if [[ -f "$file" ]]; then
        fix_markdown_issues "$file"
    else
        echo "⚠️  File not found: $file"
    fi
done

echo ""
echo "🎉 Markdown formatting fixes completed!"
echo ""
echo "📋 Summary:"
echo "- Fixed heading spacing issues"
echo "- Added blank lines around lists"
echo "- Fixed fenced code block spacing"
echo "- Removed trailing spaces"
echo "- Wrapped bare URLs in angle brackets"
echo ""
echo "💾 Backups created with .backup extension"
echo "📖 Review changes and commit when satisfied"
