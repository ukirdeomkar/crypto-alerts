# 📁 Project Structure Documentation

## Overview

This document explains the organized folder structure of the CoinDCX Futures Trading System. The project follows industry best practices for maintainability, scalability, and readability.

---

## Directory Tree

```
crypto-alerts/
│
├── app/                           # Main application code
│   ├── __init__.py               # Package initialization & exports
│   ├── main.py                   # Application orchestrator (265 lines)
│   ├── scanner.py                # Price data engine (153 lines)
│   ├── indicators.py             # Technical analysis (170 lines)
│   ├── signal_generator.py       # Signal generation logic (158 lines)
│   ├── risk_manager.py           # Risk management (107 lines)
│   ├── account_manager.py        # CoinDCX API integration (201 lines)
│   ├── alerter.py                # Alert system (222 lines)
│   └── utils.py                  # Helper functions (137 lines)
│
├── config/                        # Configuration files
│   ├── config.yaml               # Main system configuration
│   └── .env.example              # Environment variables template
│
├── data/                          # Data files
│   └── futures-coins-filtered.txt  # List of 377 futures pairs
│
├── docs/                          # Documentation
│   ├── README.md                 # Complete user guide (406 lines)
│   ├── QUICK_START.md            # 5-minute setup guide (354 lines)
│   ├── DEPLOYMENT.md             # Deployment instructions (496 lines)
│   ├── REQUIREMENTS.md           # Technical specifications (605 lines)
│   ├── SYSTEM_OVERVIEW.md        # Architecture details (510 lines)
│   └── PROJECT_SUMMARY.md        # Complete summary (546 lines)
│
├── scripts/                       # Utility scripts
│   ├── filter-futures.ps1        # PowerShell: Filter futures pairs
│   ├── trigger-workflow.ps1      # PowerShell: Trigger GitHub Actions
│   └── trigger-workflow.sh       # Bash: Trigger GitHub Actions
│
├── logs/                          # Application logs (gitignored)
│   ├── .gitkeep                  # Keep directory in git
│   └── trading.log               # Main log file (auto-generated)
│
├── .github/                       # GitHub configuration
│   └── workflows/                # GitHub Actions workflows
│
├── .venv/                         # Python virtual environment (gitignored)
│
├── run.py                         # Application entry point
├── requirements.txt               # Python dependencies
├── Procfile                       # Railway deployment command
├── railway.toml                   # Railway configuration
├── runtime.txt                    # Python version specification
├── .gitignore                     # Git ignore rules
├── .env                          # Environment variables (gitignored)
├── README.md                      # Project overview & quick start
└── PROJECT_STRUCTURE.md           # This file

```

---

## Folder Details

### 📦 `app/` - Application Code

**Purpose:** Contains all core application logic and business code.

**Structure:**
```
app/
├── __init__.py          # Package exports for easy imports
├── main.py             # Main orchestrator (scheduler, lifecycle)
├── scanner.py          # CoinDCX API integration, price fetching
├── indicators.py       # Technical analysis calculations
├── signal_generator.py # Signal generation & confidence scoring
├── risk_manager.py     # Position sizing & risk management
├── account_manager.py  # Personalized mode (CoinDCX API)
├── alerter.py          # Multi-channel alert system
└── utils.py            # Shared utility functions
```

**Design Principles:**
- **Single Responsibility:** Each module has one clear purpose
- **Loose Coupling:** Modules interact through well-defined interfaces
- **High Cohesion:** Related functionality grouped together
- **Dependency Injection:** Configuration & dependencies passed in constructors

**Import Convention:**
```python
# Internal imports use 'app.' prefix
from app.scanner import PriceScanner
from app.utils import load_config
```

---

### ⚙️ `config/` - Configuration Files

**Purpose:** Centralized configuration management.

**Files:**
- **`config.yaml`** - Main application configuration
  - Trading parameters (capital, risk, leverage)
  - Scanner settings (interval, data source)
  - Signal generation rules
  - Risk management rules
  - Alert channels configuration
  - Logging settings

- **`.env.example`** - Environment variables template
  - Discord webhook URL
  - Telegram bot credentials
  - CoinDCX API keys (personalized mode)
  - Timezone settings

**Usage:**
```python
from app.utils import load_config

config = load_config()  # Loads from config/config.yaml
capital = config['risk']['total_capital']
```

**Security:**
- Sensitive data (API keys, webhooks) in `.env` (gitignored)
- Non-sensitive settings in `config.yaml` (version controlled)

---

### 📊 `data/` - Data Files

**Purpose:** Static data files used by the application.

**Files:**
- **`futures-coins-filtered.txt`** - List of 377 CoinDCX futures pairs
  - One symbol per line (e.g., BTC, ETH, SOL)
  - Loaded at startup by scanner
  - Updated manually when new futures added

**Future Data:**
- Price history cache (if implemented)
- Backtesting datasets
- Performance statistics

---

### 📚 `docs/` - Documentation

**Purpose:** Comprehensive project documentation.

**Structure:**

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** | Complete user guide | All users |
| **QUICK_START.md** | 5-minute setup | New users |
| **DEPLOYMENT.md** | Deployment instructions | Deployers |
| **REQUIREMENTS.md** | Technical specifications | Developers |
| **SYSTEM_OVERVIEW.md** | Architecture details | Developers |
| **PROJECT_SUMMARY.md** | Complete project summary | Stakeholders |

**Documentation Standards:**
- Markdown format for readability
- Clear headings and structure
- Code examples where applicable
- Step-by-step instructions
- Troubleshooting sections

---

### 🛠️ `scripts/` - Utility Scripts

**Purpose:** Helper scripts for development and operations.

**Files:**

**`filter-futures.ps1`** (PowerShell)
- Filters futures pairs from raw data
- Usage: `.\scripts\filter-futures.ps1`

**`trigger-workflow.ps1`** (PowerShell)
- Manually triggers GitHub Actions workflow
- Usage: `.\scripts\trigger-workflow.ps1`

**`trigger-workflow.sh`** (Bash)
- Same as above for Linux/Mac
- Usage: `./scripts/trigger-workflow.sh`

**Future Scripts:**
- Backup configuration
- Test alert system
- Generate performance reports
- Database migrations (if needed)

---

### 📝 `logs/` - Application Logs

**Purpose:** Runtime logs for monitoring and debugging.

**Structure:**
```
logs/
├── .gitkeep         # Keeps directory in git
└── trading.log      # Main log file (auto-generated)
```

**Log Rotation:**
- Max size: 10MB per file
- Backup count: 5 files
- Older logs automatically rotated

**Log Levels:**
- **DEBUG:** Detailed diagnostic information
- **INFO:** General informational messages
- **WARNING:** Warning messages (non-critical)
- **ERROR:** Error messages (critical)

**Configuration:**
```yaml
logging:
  level: "INFO"
  file: "logs/trading.log"
  max_file_size_mb: 10
  backup_count: 5
```

---

### ⚡ Root Level Files

**`run.py`** - Application Entry Point
```python
# Main entry point for the application
# Usage: python run.py
```
- Sets up Python path
- Imports and runs main()
- Simplifies deployment commands

**`requirements.txt`** - Python Dependencies
```
requests>=2.32.0
APScheduler>=3.10.4
pandas>=2.2.0
numpy>=1.26.0
pyyaml>=6.0.1
pytz>=2024.1
python-dotenv>=1.2.0
```
- Pinned versions for reproducibility
- Install: `pip install -r requirements.txt`

**`Procfile`** - Railway Deployment
```
worker: python run.py
```
- Specifies how to run the application
- Used by Railway.app and Heroku

**`railway.toml`** - Railway Configuration
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python run.py"
```

**`runtime.txt`** - Python Version
```
python-3.11
```

**`.gitignore`** - Git Ignore Rules
- Excludes `.env`, `.venv/`, `logs/*.log`
- Keeps repository clean

**`README.md`** - Project Overview
- Quick start guide
- Feature highlights
- Links to detailed documentation

---

## Import Hierarchy

### Application Imports

```python
# Entry point
run.py
    └── app.main.main()

# Main application
app.main
    ├── app.utils (load_config, setup_logging)
    ├── app.scanner.PriceScanner
    ├── app.indicators.TechnicalIndicators
    ├── app.signal_generator.SignalGenerator
    ├── app.risk_manager.RiskManager
    ├── app.account_manager.AccountManager (optional)
    └── app.alerter.Alerter

# Signal generation flow
app.signal_generator
    └── app.utils (calculate_targets, calculate_stop_loss, validate_signal)

# Risk management
app.risk_manager
    └── app.utils (calculate_position_size)

# Alert system
app.alerter
    └── app.utils (format_inr, format_percentage, get_env_var)
```

**Import Rules:**
1. Use `from app.module import Class` for internal imports
2. Never use relative imports (no `from .module import`)
3. Import only what you need (specific classes/functions)
4. Group imports: stdlib → third-party → internal

---

## Configuration Flow

```
1. Environment Variables (.env)
   ↓
2. Config File (config/config.yaml)
   ↓
3. Application Modules
   ↓
4. Runtime
```

**Precedence:**
1. Environment variables (highest priority)
2. Configuration file
3. Default values in code (lowest priority)

**Example:**
```python
# Environment variable
DISCORD_WEBHOOK=https://discord.com/...

# Config file
risk:
  total_capital: 100000

# Runtime
webhook = os.getenv('DISCORD_WEBHOOK')  # From .env
capital = config['risk']['total_capital']  # From config.yaml
```

---

## Data Flow

```
CoinDCX API
    ↓
app/scanner.py (fetch & cache)
    ↓
app/indicators.py (calculate RSI, MACD, BB)
    ↓
app/signal_generator.py (evaluate & score)
    ↓
app/risk_manager.py (position sizing)
    ↓
[Optional] app/account_manager.py (margin check)
    ↓
app/alerter.py (Discord/Telegram)
    ↓
USER (execute trade)
```

---

## Extension Points

### Adding New Indicators

1. Add calculation method in `app/indicators.py`
2. Update `analyze_coin()` to include new indicator
3. Modify `app/signal_generator.py` to use indicator
4. Update config schema in `config/config.yaml`
5. Document in `docs/SYSTEM_OVERVIEW.md`

### Adding New Alert Channels

1. Add channel config in `config/config.yaml`
2. Implement `_send_[channel]()` in `app/alerter.py`
3. Update `_send_alert()` dispatcher
4. Add credentials to `.env.example`
5. Document in `docs/DEPLOYMENT.md`

### Adding New Data Sources

1. Create new scanner class in `app/scanner.py` or new file
2. Implement same interface as `PriceScanner`
3. Update `app/main.py` to use new scanner
4. Configure in `config/config.yaml`
5. Update docs

---

## Testing Structure (Future)

```
tests/
├── __init__.py
├── test_scanner.py
├── test_indicators.py
├── test_signal_generator.py
├── test_risk_manager.py
├── test_account_manager.py
├── test_alerter.py
└── test_utils.py
```

**Testing Commands:**
```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_scanner.py

# Run with coverage
pytest --cov=app tests/
```

---

## Best Practices

### Code Organization
✅ **Do:**
- Keep files under 300 lines
- One class per file (primary)
- Group related functions
- Use clear, descriptive names
- Add docstrings to classes and methods

❌ **Don't:**
- Mix configuration with logic
- Use global variables
- Create circular dependencies
- Hardcode values

### Configuration Management
✅ **Do:**
- Use `config/config.yaml` for application settings
- Use `.env` for secrets and credentials
- Provide `.env.example` template
- Validate configuration at startup
- Use type hints

❌ **Don't:**
- Commit `.env` to git
- Hardcode API keys or secrets
- Mix environments (dev/prod)
- Ignore configuration errors

### Documentation
✅ **Do:**
- Keep README.md up to date
- Document all configuration options
- Include code examples
- Maintain changelog
- Use clear headings

❌ **Don't:**
- Duplicate documentation
- Leave outdated docs
- Assume prior knowledge
- Skip error scenarios

---

## Maintenance Tasks

### Daily
- Check logs for errors: `tail -f logs/trading.log`
- Monitor alert delivery
- Verify system uptime

### Weekly
- Review log files
- Check Railway usage hours
- Update config if needed
- Review signal quality

### Monthly
- Update dependencies: `pip install -r requirements.txt --upgrade`
- Backup configuration files
- Rotate API keys (good practice)
- Review documentation accuracy

---

## Migration Guide

### From Old Structure to New

**Old:**
```
crypto-alerts/
├── main.py
├── scanner.py
├── indicators.py
├── config.yaml
└── README.md
```

**New:**
```
crypto-alerts/
├── app/
│   ├── main.py
│   ├── scanner.py
│   └── indicators.py
├── config/
│   └── config.yaml
├── docs/
│   └── README.md
└── run.py
```

**Migration Steps:**
1. Files moved to appropriate directories
2. Imports updated (`from scanner` → `from app.scanner`)
3. Config paths updated (`config.yaml` → `config/config.yaml`)
4. New entry point created (`run.py`)
5. Documentation reorganized in `docs/`

---

## Summary

### Key Benefits of This Structure

✅ **Maintainability**
- Clear separation of concerns
- Easy to locate specific functionality
- Predictable file locations

✅ **Scalability**
- Easy to add new modules
- Extension points well-defined
- Configuration-driven

✅ **Readability**
- Intuitive directory names
- Grouped related files
- Clear import paths

✅ **Best Practices**
- Industry-standard structure
- Separation of code/config/docs
- Professional organization

✅ **Developer Experience**
- Quick onboarding
- Self-documenting structure
- Easy to navigate

---

**For detailed usage instructions, see [docs/README.md](docs/README.md)**

**For quick setup, see [docs/QUICK_START.md](docs/QUICK_START.md)**

