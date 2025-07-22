# Installation Guide - Consolidated Requirements

This guide explains how to install the Business Intelligence Scraper with the newly consolidated requirements system.

## 🚀 Quick Installation (Recommended)

For most users, install all dependencies at once:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt

# Post-installation setup
python -m spacy download en_core_web_sm
playwright install
```

## 🎯 Selective Installation (Advanced)

If you prefer granular control over dependencies, use the setup.py with extras:

### Core Installation (Minimal)
```bash
pip install -e .
```

### Production Installation
```bash
pip install -e ".[production]"
```

### Development Installation  
```bash
pip install -e ".[dev]"
```

### Full Installation (Everything)
```bash
pip install -e ".[full]"
```

### Feature-Specific Installation
```bash
# Just web scraping
pip install -e ".[scraping]"

# Just data analysis
pip install -e ".[data,analytics]"

# Just NLP features
pip install -e ".[nlp]"

# Advanced NLP (requires system dependencies)
pip install -e ".[nlp-advanced]"

# Security features
pip install -e ".[security]"
```

## 📦 Available Extras

| Extra | Description | Use Case |
|-------|-------------|----------|
| `web` | Web framework & APIs | API development |
| `database` | Database & caching | Data persistence |
| `scraping` | Web scraping tools | Data collection |
| `security` | Auth & encryption | Production security |
| `data` | Data analysis tools | Analytics |
| `nlp` | Basic NLP features | Text processing |
| `nlp-advanced` | Advanced multilingual NLP | International data |
| `vision` | Computer vision & OCR | Image processing |
| `monitoring` | Logging & metrics | Production monitoring |
| `dev` | Development tools | Code development |
| `notebook` | Jupyter notebooks | Data exploration |
| `profiling` | Performance tools | Optimization |
| `production` | Core production stack | Deployment |
| `analytics` | Data science stack | Analysis & ML |
| `all` | All features | Complete functionality |
| `full` | Everything + dev tools | Development environment |

## 🔧 System Dependencies

Some advanced features require system-level packages:

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    tesseract-ocr \
    libicu-dev \
    mecab \
    libmecab-dev \
    build-essential \
    python3-dev
```

### macOS
```bash
brew install tesseract icu4c mecab
```

### Windows
- Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
- Some NLP features may not be available

## 📋 Migration from Old Requirements

### If you previously used multiple requirements files:

1. **Backup your current environment** (optional):
   ```bash
   pip freeze > old_requirements_backup.txt
   ```

2. **Update to new system**:
   ```bash
   # Remove old installations if needed
   pip uninstall -y -r requirements-dev.txt
   pip uninstall -y -r requirements-advanced.txt
   pip uninstall -y -r requirements-ai.txt
   
   # Install with new consolidated requirements
   pip install -r requirements.txt
   ```

3. **Clean up old files** (optional):
   ```bash
   rm requirements-dev.txt requirements-advanced.txt requirements-ai.txt
   rm requirements_advanced.txt  # duplicate file
   ```

## ⚡ Quick Start Commands

### 1. Basic Setup
```bash
git clone https://github.com/Trashytalk/scraper.git
cd scraper
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python -c "from business_intel_scraper.database.config import init_database; import asyncio; asyncio.run(init_database())"
```

### 3. Download Language Models
```bash
python -m spacy download en_core_web_sm
```

### 4. Install Browser Drivers
```bash
playwright install
```

### 5. Start Backend Server
```bash
uvicorn business_intel_scraper.backend.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 🐛 Troubleshooting

### Common Issues:

1. **Missing system dependencies**
   - Install system packages listed above
   - Some packages require compilation

2. **PyICU installation fails**
   - Ubuntu: `sudo apt-get install libicu-dev`
   - macOS: `brew install icu4c`

3. **Playwright browsers not found**
   - Run: `playwright install`

4. **spaCy model not found**
   - Run: `python -m spacy download en_core_web_sm`

5. **Database connection errors**
   - Ensure `.env` file is configured
   - Check `DATABASE_URL` setting

## 📁 File Structure After Consolidation

```
scraper/
├── requirements.txt           # ✅ NEW: All dependencies
├── setup.py                  # ✅ UPDATED: Advanced installation
├── requirements-consolidated.txt  # ✅ BACKUP: Detailed version
├── requirements-dev.txt      # ❌ CAN DELETE: Merged into main
├── requirements-advanced.txt # ❌ CAN DELETE: Merged into main  
├── requirements-ai.txt       # ❌ CAN DELETE: Merged into main
└── business_intel_scraper/
    ├── backend/
    └── database/
        └── config.py         # ✅ FIXED: Database configuration
```

## 💡 Benefits of Consolidation

1. **Simplified Installation**: One command installs everything
2. **Reduced Confusion**: No need to track multiple files
3. **Better Version Control**: Single source of truth
4. **Flexible Options**: Use setup.py extras for granular control
5. **Easier CI/CD**: Simpler deployment scripts
6. **Better Documentation**: Clear installation instructions

## 🚀 Next Steps

After installation:
1. Follow the [Backend Setup Guide](docs/backend_setup.md)
2. Check the [API Documentation](http://localhost:8000/docs)
3. Run the test suite: `pytest`
4. Explore example notebooks in `docs/`
