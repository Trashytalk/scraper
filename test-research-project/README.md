# test-research-project

This project was created using the **business-research** template from the Business Intelligence Scraper framework.

## Quick Start

```bash
# Run the project
./run.sh

# Or manually
source .env
cd ../  # Go back to main scraper directory
source .venv/bin/activate
uvicorn business_intel_scraper.backend.api.main:app --reload
```

## Project Structure

- `config/` - Project-specific configuration
- `data/` - Input data and outputs
- `logs/` - Project logs
- `results/` - Scraping results and reports
- `.env` - Environment configuration (from business-research template)

## Template: business-research

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

## Configuration

Edit `.env` file to customize:

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
