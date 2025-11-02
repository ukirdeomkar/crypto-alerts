# 🚀 CoinDCX Futures Trading Signal System

Professional real-time trading signal system for crypto futures scalping on CoinDCX.

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Cost](https://img.shields.io/badge/cost-%E2%82%B90%2Fmonth-success)

## ✨ Features

- 🎯 Real-time monitoring of 377 futures pairs
- 📊 Technical analysis (RSI, MACD, Bollinger Bands, Volume)
- 💰 Complete risk management & position sizing
- 🤖 Generic & Personalized modes
- 📱 Discord & Telegram alerts
- ⏰ Automated schedule (11 AM - 5 PM IST)
- 💸 100% Free deployment

## 📁 Project Structure

```
crypto-alerts/
├── app/                 # Application code
│   ├── main.py         # Orchestrator
│   ├── scanner.py      # Price fetching
│   ├── indicators.py   # Technical analysis
│   ├── signal_generator.py
│   ├── risk_manager.py
│   ├── account_manager.py
│   ├── alerter.py
│   └── utils.py
├── config/             # Configuration
│   └── config.yaml
├── data/               # Futures pairs list
├── docs/               # Documentation
│   ├── README.md          # Complete guide
│   ├── QUICK_START.md     # 5-min setup
│   ├── DEPLOYMENT.md      # Deploy guide
│   ├── REQUIREMENTS.md    # Tech specs
│   ├── SYSTEM_OVERVIEW.md # Architecture
│   └── PROJECT_SUMMARY.md # Summary
├── scripts/            # Utility scripts
├── logs/               # Application logs
├── run.py              # Entry point
└── requirements.txt    # Dependencies
```

## 🚀 Quick Start

### 1. Setup
```bash
git clone <your-repo>
cd crypto-alerts
pip install -r requirements.txt
```

### 2. Configure
```bash
# Create .env file in root
echo "DISCORD_WEBHOOK=your_webhook_url" > .env

# Edit config/config.yaml for your strategy
```

### 3. Run
```bash
python run.py
```

### OR Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

Add `DISCORD_WEBHOOK` environment variable and deploy!

## 📊 Example Signal

```
🚀 STRONG BUY - BTCINR PERPETUAL
Entry: ₹58,42,500 | Size: ₹10,000 | Leverage: 5x
Target 1: ₹58,60,000 (+₹150)
Target 2: ₹58,77,500 (+₹300)
Stop Loss: ₹58,25,000 (-₹150)
Confidence: 94%
```

## ⚙️ Configuration

Edit `config/config.yaml`:

```yaml
risk:
  total_capital: 100000
  risk_per_trade_percent: 2
  max_concurrent_positions: 3
  default_leverage: 5

scanner:
  interval_seconds: 5

signals:
  min_confidence: 80
  max_alerts_per_scan: 3
```

## 📚 Documentation

- **[docs/README.md](docs/README.md)** - Complete documentation
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - 5-minute setup guide
- **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment instructions
- **[docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)** - Technical specifications
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Project organization
- **[RESTRUCTURE_SUMMARY.md](RESTRUCTURE_SUMMARY.md)** - Restructure details

## 🔐 Personalized Mode (Optional)

Enable account-aware signals with read-only CoinDCX API keys.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for setup instructions.

## ⚠️ Risk Disclaimer

This system provides trading signals, NOT financial advice.
- No profit guarantees
- High risk of loss
- Use stop-losses always
- Start with small capital
- Only trade what you can afford to lose

## 📞 Support

- **Quick Help:** [docs/QUICK_START.md](docs/QUICK_START.md)
- **Full Docs:** [docs/README.md](docs/README.md)
- **Issues:** GitHub Issues

## 📄 License

MIT License

---

**Ready to start?** → [docs/QUICK_START.md](docs/QUICK_START.md)

**Happy Trading! 📈**
