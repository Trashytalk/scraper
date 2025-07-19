#!/bin/bash

# Business Intelligence Scraper - Project Template Setup
# Usage: ./create-project.sh [template] [project-name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

show_help() {
    echo "Business Intelligence Scraper - Project Template Setup"
    echo ""
    echo "Usage: $0 [template] [project-name]"
    echo ""
    echo "Available templates:"
    echo "  business-research    - Company and market research"
    echo "  competitor-analysis  - Competitive intelligence"
    echo "  security-audit      - OSINT and security reconnaissance"
    echo "  development         - Local development and testing"
    echo ""
    echo "Examples:"
    echo "  $0 business-research my-research-project"
    echo "  $0 competitor-analysis acme-competitor-study"
    echo "  $0 security-audit security-assessment"
    echo ""
}

if [ $# -eq 0 ] || [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    show_help
    exit 0
fi

TEMPLATE="$1"
PROJECT_NAME="${2:-scraper-project}"

# Validate template
AVAILABLE_TEMPLATES=("business-research" "competitor-analysis" "security-audit" "development")
if [[ ! " ${AVAILABLE_TEMPLATES[@]} " =~ " ${TEMPLATE} " ]]; then
    print_error "Invalid template: $TEMPLATE"
    echo "Available templates: ${AVAILABLE_TEMPLATES[*]}"
    exit 1
fi

print_step "Creating new project: $PROJECT_NAME with template: $TEMPLATE"

# Create project directory
if [ -d "$PROJECT_NAME" ]; then
    print_error "Directory $PROJECT_NAME already exists"
    exit 1
fi

mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Copy template configuration
print_step "Setting up configuration from template..."
cp "../config/templates/${TEMPLATE}.env" .env
print_success "Configuration copied from $TEMPLATE template"

# Create project structure
print_step "Creating project structure..."

mkdir -p data/{input,output,logs}
mkdir -p config
mkdir -p logs
mkdir -p results

# Create project-specific config
cat > config/project.yaml << EOF
# Project Configuration for $PROJECT_NAME
project:
  name: "$PROJECT_NAME"
  template: "$TEMPLATE"
  created: "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  
settings:
  output_directory: "results/"
  log_directory: "logs/"
  data_directory: "data/"
  
template_settings:
EOF

# Add template-specific settings
case $TEMPLATE in
    "business-research")
        cat >> config/project.yaml << EOF
  focus: "company_research"
  data_sources:
    - "news_articles"
    - "company_websites"
    - "financial_reports"
  export_formats: ["csv", "json", "excel"]
EOF
        ;;
    "competitor-analysis")
        cat >> config/project.yaml << EOF
  focus: "competitive_intelligence"
  data_sources:
    - "competitor_websites"
    - "pricing_data"
    - "product_information"
    - "social_media"
  monitoring: true
  alerts: true
EOF
        ;;
    "security-audit")
        cat >> config/project.yaml << EOF
  focus: "security_assessment"
  data_sources:
    - "domain_reconnaissance"
    - "port_scanning"
    - "vulnerability_assessment"
    - "osint_gathering"
  security_level: "high"
  encryption: true
EOF
        ;;
    "development")
        cat >> config/project.yaml << EOF
  focus: "development_testing"
  data_sources:
    - "test_websites"
    - "sample_data"
  mock_mode: true
  fast_execution: true
EOF
        ;;
esac

print_success "Project structure created"

# Create a project-specific script
print_step "Creating project scripts..."

cat > run.sh << 'EOF'
#!/bin/bash

# Project runner script
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRAPER_ROOT="$(dirname "$PROJECT_ROOT")"

echo "🚀 Starting scraper project..."
echo "Project: $(basename "$PROJECT_ROOT")"

# Check if main scraper is available
if [ ! -f "$MAIN_SCRAPER_ROOT/setup.sh" ]; then
    echo "❌ Main scraper not found. Make sure this project is inside the scraper directory."
    exit 1
fi

# Source the project environment
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✓ Loaded project configuration"
fi

# Activate main scraper environment
if [ -f "$MAIN_SCRAPER_ROOT/.venv/bin/activate" ]; then
    source "$MAIN_SCRAPER_ROOT/.venv/bin/activate"
    echo "✓ Activated scraper environment"
else
    echo "❌ Scraper environment not found. Run setup.sh in main directory first."
    exit 1
fi

# Change to main scraper directory and run
cd "$MAIN_SCRAPER_ROOT"

echo "🔄 Starting API server..."
uvicorn business_intel_scraper.backend.api.main:app --host 0.0.0.0 --port 8000
EOF

chmod +x run.sh

cat > README.md << EOF
# $PROJECT_NAME

This project was created using the **$TEMPLATE** template from the Business Intelligence Scraper framework.

## Quick Start

\`\`\`bash
# Run the project
./run.sh

# Or manually
source .env
cd ../  # Go back to main scraper directory
source .venv/bin/activate
uvicorn business_intel_scraper.backend.api.main:app --reload
\`\`\`

## Project Structure

- \`config/\` - Project-specific configuration
- \`data/\` - Input data and outputs
- \`logs/\` - Project logs
- \`results/\` - Scraping results and reports
- \`.env\` - Environment configuration (from $TEMPLATE template)

## Template: $TEMPLATE

EOF

# Add template-specific documentation
case $TEMPLATE in
    "business-research")
        cat >> README.md << EOF
This template is optimized for business and market research:

- **Company Information**: Automated collection of company data
- **Market Analysis**: Industry trends and competitive landscape
- **Financial Data**: Revenue, funding, and financial metrics
- **News Monitoring**: Real-time business news tracking

### Common Use Cases
- Due diligence research
- Market entry analysis
- Investment research
- Competitive benchmarking
EOF
        ;;
    "competitor-analysis")
        cat >> README.md << EOF
This template is optimized for competitive intelligence:

- **Competitor Monitoring**: Automated tracking of competitor activities
- **Pricing Intelligence**: Price comparison and monitoring
- **Product Analysis**: Feature comparison and product updates
- **Market Positioning**: Brand and messaging analysis

### Common Use Cases
- Competitive pricing strategy
- Product benchmarking
- Market positioning analysis
- Competitive threat assessment
EOF
        ;;
    "security-audit")
        cat >> README.md << EOF
This template is optimized for security assessments and OSINT:

- **Domain Reconnaissance**: Subdomain discovery and analysis
- **Vulnerability Assessment**: Security weakness identification
- **OSINT Gathering**: Open source intelligence collection
- **Threat Intelligence**: Security threat monitoring

### Common Use Cases
- Security audits
- Penetration testing reconnaissance
- Threat intelligence gathering
- Digital footprint analysis

### ⚠️ Legal Notice
Use this template only for authorized security assessments and research.
EOF
        ;;
    "development")
        cat >> README.md << EOF
This template is optimized for development and testing:

- **Fast Development**: Quick setup for testing and development
- **Mock Data**: Sample data for testing purposes
- **Debug Features**: Enhanced logging and debugging tools
- **Local Testing**: Safe local development environment

### Common Use Cases
- Framework development
- Feature testing
- Educational purposes
- Proof of concept development
EOF
        ;;
esac

cat >> README.md << EOF

## Configuration

Edit \`.env\` file to customize:

- API keys and credentials
- Data sources and targets
- Output formats and destinations
- Scraping behavior and limits

## Documentation

- [Main Documentation](../docs/README.md)
- [API Usage](../docs/api_usage.md)
- [Configuration Guide](../docs/setup.md)

## Support

For issues and questions, see the main project documentation or create an issue in the repository.
EOF

print_success "Project scripts created"

# Create .gitignore
cat > .gitignore << EOF
# Environment and secrets
.env.local
*.key
*.pem

# Data and outputs
data/output/*
!data/output/.gitkeep
results/*
!results/.gitkeep
logs/*
!logs/.gitkeep

# Cache and temporary files
cache/
*.tmp
*.log

# Python
__pycache__/
*.pyc
*.pyo

# Database
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db
EOF

# Create placeholder files
touch data/input/.gitkeep
touch data/output/.gitkeep
touch results/.gitkeep
touch logs/.gitkeep

print_step "Project setup complete!"

echo ""
echo -e "${GREEN}🎉 Project '$PROJECT_NAME' created successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your specific configuration"
echo "2. Review config/project.yaml for project settings"  
echo "3. Run the project:"
echo "   ${BLUE}cd $PROJECT_NAME && ./run.sh${NC}"
echo ""
echo "Project location: $(pwd)"
echo "Template used: $TEMPLATE"
echo ""
