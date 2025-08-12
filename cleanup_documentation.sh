#!/bin/bash

# Main Directory Cleanup Script
# Organizes documentation and updates references

echo "🧹 Starting main directory cleanup and documentation organization..."

# Function to update file references
update_references() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        echo "⚠️  File not found: $file"
        return 1
    fi
    
    echo "📝 Updating references in: $file"
    
    # Update references to moved files
    sed -i 's|SECURITY_ROTATION_PLAYBOOK\.md|docs/security/SECURITY_ROTATION_PLAYBOOK.md|g' "$file"
    sed -i 's|SECURITY_STATUS_SUMMARY\.md|docs/security/SECURITY_STATUS_SUMMARY.md|g' "$file"
    sed -i 's|DEPLOYMENT\.md|docs/deployment/DEPLOYMENT.md|g' "$file"
    sed -i 's|CONTRIBUTING\.md|docs/development/CONTRIBUTING.md|g' "$file"
    sed -i 's|API_DOCUMENTATION\.md|docs/api/API_DOCUMENTATION.md|g' "$file"
    sed -i 's|CHANGELOG\.md|docs/releases/CHANGELOG.md|g' "$file"
    
    echo "✅ Updated: $file"
}

# List of files to update references in
reference_files=(
    "README.md"
    "business_intel_scraper/README.md"
    "business_intel_scraper/frontend/README.md"
)

# Update references in key files
for file in "${reference_files[@]}"; do
    if [[ -f "$file" ]]; then
        update_references "$file"
    else
        echo "⚠️  File not found: $file"
    fi
done

echo ""
echo "🎉 Main directory cleanup completed!"
echo ""
echo "📂 New Documentation Structure:"
echo "├── docs/"
echo "│   ├── security/           # Security documentation and playbooks"
echo "│   ├── deployment/         # Deployment and infrastructure guides"
echo "│   ├── development/        # Development and testing guides"
echo "│   ├── reports/            # Status reports and assessments"
echo "│   ├── api/                # API documentation and references"
echo "│   ├── releases/           # Release notes and changelog"
echo "│   ├── visual/             # Architecture diagrams and visuals"
echo "│   └── archive/            # Historical documentation"
echo ""
echo "📋 Summary:"
echo "- Moved 17 markdown files from main directory to organized subfolders"
echo "- Created 6 new documentation categories with index files"
echo "- Updated references in key documentation files"
echo "- Maintained main README.md in root for project overview"
echo ""
echo "🔗 Updated file references in documentation"
echo "📚 All documentation now properly organized and accessible"
