# CoinDCX Futures Trading Signal System - Requirements Document

## Project Overview

**Purpose:** Professional real-time trading signal system for crypto futures scalping on CoinDCX  
**Target User:** Active futures trader executing 1-4 minute scalp trades  
**Trading Hours:** 11:00 AM - 5:00 PM IST (Monday-Friday)  
**Total Futures Pairs:** 377 coins monitored simultaneously  
**Cost:** $0/month (Railway.app free tier: 500 hours, using ~180 hours/month)

---

## Business Requirements

### Trading Strategy
- **Timeframe:** 1-4 minute scalping (ultra-short term)
- **Position Duration:** 1-4 minutes average hold time
- **Trading Session:** 6 hours daily (11 AM - 5 PM IST)
- **Market:** CoinDCX Futures (Perpetual Contracts)
- **Data Source:** Spot market prices from CoinDCX API (same price movements as futures)

### Risk Management
- **Capital Management:** Configurable total capital
- **Risk Per Trade:** 1-2% of total capital (configurable)
- **Max Concurrent Positions:** 3-5 positions (configurable)
- **Leverage:** 5-10x (configurable per trade)
- **Stop Loss:** Dynamic 0.3-0.5% based on volatility
- **Take Profit:** Multi-target strategy (0.3%, 0.6%)
- **Risk:Reward Ratio:** Minimum 1:1.5

### Signal Requirements
- **Latency:** <2 seconds from price change to alert
- **Scan Frequency:** Every 1-5 seconds (configurable)
- **Signal Quality:** Minimum 80% confidence score
- **Alert Priority:** Top 2-3 opportunities only (prevent alert fatigue)
- **False Positive Rate:** Target <20%

---

## System Modes

### Mode 1: Generic (No API Keys Required)
**Features:**
- Market-wide signals (not account-specific)
- Static position sizing based on config
- Manual position tracking required
- Suitable for testing and initial deployment

**Limitations:**
- No awareness of current positions
- Cannot verify available margin
- Risk of over-leveraging
- Manual P&L tracking

### Mode 2: Personalized (Read-Only API Keys)
**Features:**
- Account-aware signals
- Dynamic position sizing based on real available margin
- Automatic position tracking
- Real-time P&L monitoring
- Over-leverage prevention
- Concurrent position limit enforcement

**Security:**
- Read-only API keys (no order execution)
- Keys stored as environment variables
- System never places trades automatically
- Cannot withdraw funds

---

## Technical Requirements

### Data Source
**Primary:** CoinDCX Spot Market REST API
- Endpoint: `https://api.coindcx.com/exchange/ticker`
- Free, no authentication required for public data
- Covers all 377 futures pairs (spot equivalent)
- Rate limit: Suitable for 1-5 second polling

**Optional:** WebSocket for lower latency (future enhancement)

### Technical Indicators
**Primary Indicators (1-minute candles):**
- RSI (Relative Strength Index): 5-period for scalping
- MACD (Moving Average Convergence Divergence): Fast (5,13,5)
- Bollinger Bands: 10-period, 2 standard deviations
- Volume Analysis: 2x average volume surge detection
- Price Action: Support/Resistance levels

**Signal Generation Logic:**
- Strong Buy (90%+ confidence): 3+ indicators align + volume surge
- Weak Buy (70-89%): 2 indicators + moderate volume
- Neutral: Mixed signals (no alert)
- Weak Sell / Strong Sell: Similar logic inverted

### Position Sizing Algorithm
**Generic Mode:**
```
Position Size = (Total Capital × Risk%) / (Stop Loss Distance × Leverage)
Max Loss = Total Capital × Risk%
```

**Personalized Mode:**
```
Available Margin = Total Balance - Used Margin
Position Size = min(
  Available Margin × 0.1,  # Max 10% per trade
  (Total Capital × Risk%) / (Stop Loss Distance × Leverage)
)
```

### Alert Format
**Entry Signal:**
```
🚀 STRONG BUY - BTCINR PERPETUAL

📊 ENTRY DETAILS:
Entry Price: ₹58,42,500
Position Size: ₹10,000
Leverage: 5x → Exposure: ₹50,000
Direction: LONG

🎯 TARGETS:
Target 1 (50%): ₹58,60,000 (+0.30% = ₹150 profit)
Target 2 (50%): ₹58,77,500 (+0.60% = ₹300 profit)

🛡️ PROTECTION:
Stop Loss: ₹58,25,000 (-0.30% = ₹150 loss)
Risk:Reward = 1:2 ✓

📈 SIGNALS:
✓ RSI(5): 28 → Oversold
✓ MACD: Bullish crossover
✓ Volume: 3.2x surge
✓ BB: Lower band bounce

⏰ Valid for: 2 minutes
Confidence: 94%
Time: 14:23:45 IST

[Personalized Mode Only]
💰 YOUR ACCOUNT:
Available Margin: ₹87,500
Current Positions: 2/3
Net P&L Today: +₹1,245
```

---

## System Architecture

### Component Structure
```
crypto-alerts/
├── config.yaml              # User configuration
├── main.py                  # Scheduler & orchestrator
├── scanner.py               # Price data fetching
├── indicators.py            # Technical analysis
├── signal_generator.py      # Signal logic
├── risk_manager.py          # Position sizing & risk
├── account_manager.py       # Personalized mode API
├── alerter.py               # Discord/Telegram
├── utils.py                 # Helpers
├── data/
│   └── futures-coins-filtered.txt  # 377 coins
├── logs/                    # System logs
├── requirements.txt         # Python dependencies
├── railway.toml            # Railway config
├── Procfile                # Start command
├── .env.example            # Config template
├── REQUIREMENTS.md         # This document
├── DEPLOYMENT.md           # Setup guide
└── README.md               # User documentation
```

### Technology Stack
- **Language:** Python 3.11+
- **Scheduler:** APScheduler 3.10+
- **Data Processing:** Pandas, NumPy
- **HTTP Client:** Requests
- **Configuration:** PyYAML
- **Alerts:** Discord Webhooks, Telegram Bot API
- **Deployment:** Railway.app (Docker container)

### Dependencies
```
requests>=2.32.0
python-dotenv>=1.2.0
APScheduler>=3.10.4
pyyaml>=6.0.1
pandas>=2.2.0
numpy>=1.26.0
websocket-client>=1.7.0  # Optional
```

---

## Deployment Architecture

### Railway.app Configuration
**Resource Usage:**
- Memory: 50-100MB (minimal)
- CPU: Low (mostly I/O bound)
- Network: ~100KB/minute (API calls)
- Storage: <10MB (logs)

**Operating Hours:**
- Container runs 24/7
- Scanner active: 11:00 AM - 5:00 PM IST only
- Idle memory: ~10-20MB outside trading hours
- Monthly usage: 180 hours monitoring time

**Scheduler Logic:**
```
10:55 AM IST: Pre-market prep (load coins, test API)
11:00 AM IST: Start real-time scanning loop
11:00 AM - 5:00 PM: Monitor every 1-5 seconds
5:00 PM IST: Stop scanning, send daily summary
5:00 PM - 10:55 AM: Idle state (minimal resources)
```

### Environment Variables (Railway Dashboard)
```
DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
TELEGRAM_BOT_TOKEN=your_token_here (optional)
TELEGRAM_CHAT_ID=your_chat_id (optional)
TZ=Asia/Kolkata

# Personalized Mode (optional)
COINDCX_API_KEY=your_api_key
COINDCX_API_SECRET=your_api_secret
MODE=generic  # or "personalized"
```

---

## Configuration File (config.yaml)

### Complete Configuration Schema
```yaml
# System Mode
mode: "generic"  # "generic" or "personalized"

# Trading Hours (IST)
trading_hours:
  start_time: "10:55"
  end_time: "17:05"
  timezone: "Asia/Kolkata"
  days: ["monday", "tuesday", "wednesday", "thursday", "friday"]

# Scanner Settings
scanner:
  interval_seconds: 5  # Scan frequency (1-10 seconds)
  data_source: "spot"  # Use spot data for futures signals
  coins_file: "data/futures-coins-filtered.txt"
  batch_size: 50  # API batch processing

# Signal Generation
signals:
  min_confidence: 80  # Minimum confidence score (0-100)
  max_alerts_per_scan: 3  # Prevent alert spam
  cooldown_minutes: 2  # Min time between alerts for same coin
  
  indicators:
    rsi_period: 5
    rsi_oversold: 30
    rsi_overbought: 70
    
    macd_fast: 5
    macd_slow: 13
    macd_signal: 5
    
    bb_period: 10
    bb_std: 2
    
    volume_surge_multiplier: 2.0  # 2x average = surge

# Risk Management
risk:
  # Generic Mode
  total_capital: 100000  # ₹1,00,000
  risk_per_trade_percent: 2  # 2% max loss per trade
  
  # Position Limits
  max_concurrent_positions: 3
  max_leverage: 10
  default_leverage: 5
  
  # Stop Loss & Take Profit
  stop_loss_percent: 0.3  # 0.3%
  take_profit_targets:
    - target: 0.3  # 0.3% - exit 50%
      exit_percent: 50
    - target: 0.6  # 0.6% - exit remaining 50%
      exit_percent: 50
  
  # Risk:Reward
  min_risk_reward_ratio: 1.5

# Personalized Mode (API Integration)
personalized:
  enabled: false  # Set to true when API keys configured
  api_endpoint: "https://api.coindcx.com"
  
  # Account Settings
  max_margin_per_trade_percent: 10  # Max 10% of available margin
  refresh_interval_seconds: 30  # Account data refresh rate
  
  # Position Tracking
  track_pnl: true
  send_position_updates: true
  update_interval_minutes: 1

# Alert Channels
alerts:
  discord:
    enabled: true
    webhook_env_var: "DISCORD_WEBHOOK"
    
  telegram:
    enabled: false
    bot_token_env_var: "TELEGRAM_BOT_TOKEN"
    chat_id_env_var: "TELEGRAM_CHAT_ID"
  
  # Alert Preferences
  send_entry_signals: true
  send_exit_signals: true
  send_position_updates: true  # Personalized mode only
  send_daily_summary: true
  
  # Format
  include_charts: false  # Future: Include chart images
  use_mentions: false    # Discord @mentions

# Logging
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/trading.log"
  max_file_size_mb: 10
  backup_count: 5
  
  log_signals: true
  log_api_calls: false  # Set true for debugging

# Performance
performance:
  cache_price_data_seconds: 5
  max_api_retries: 3
  api_timeout_seconds: 10
  parallel_requests: true
```

---

## Functional Requirements

### FR1: Market Data Collection
- System SHALL fetch price data for all 377 futures pairs every 1-5 seconds
- System SHALL handle API rate limits gracefully
- System SHALL cache data to minimize redundant API calls
- System SHALL validate data integrity (detect stale/invalid prices)

### FR2: Technical Analysis
- System SHALL calculate RSI, MACD, Bollinger Bands for each coin
- System SHALL detect volume surges (>2x average)
- System SHALL identify price momentum and trends
- System SHALL maintain rolling price history (minimum 60 data points)

### FR3: Signal Generation
- System SHALL score each opportunity 0-100 based on indicator alignment
- System SHALL generate signals only when confidence ≥80%
- System SHALL rank signals and alert top 2-3 per scan
- System SHALL prevent duplicate alerts (2-minute cooldown per coin)
- System SHALL calculate exact entry, stop-loss, and take-profit prices

### FR4: Risk Management
- System SHALL calculate position size based on available capital and risk%
- System SHALL enforce max concurrent position limits
- System SHALL validate risk:reward ratio ≥1.5
- System SHALL calculate maximum potential loss per trade
- System SHALL adjust leverage recommendations based on volatility

### FR5: Position Tracking (Personalized Mode)
- System SHALL fetch account balance and available margin
- System SHALL track all open positions automatically
- System SHALL calculate real-time P&L for each position
- System SHALL prevent over-leveraging warnings
- System SHALL update position status every 30-60 seconds

### FR6: Alert System
- System SHALL send formatted alerts to Discord/Telegram
- System SHALL include all trade parameters (entry, SL, TP, size)
- System SHALL send position updates during active trades
- System SHALL send daily summary at 5 PM IST
- System SHALL handle alert delivery failures gracefully

### FR7: Scheduler
- System SHALL start scanning at 10:55 AM IST (pre-market)
- System SHALL run active monitoring 11 AM - 5 PM IST
- System SHALL stop scanning at 5:05 PM IST
- System SHALL idle with minimal resources outside trading hours
- System SHALL operate Monday-Friday only (configurable)

---

## Non-Functional Requirements

### NFR1: Performance
- Alert latency: <2 seconds from price change to notification
- API response time: <500ms average
- Memory usage: <100MB during active trading
- CPU usage: <10% average
- Startup time: <10 seconds

### NFR2: Reliability
- Uptime: 99% during trading hours
- API error handling: Automatic retry with exponential backoff
- Zero data loss: All signals logged to disk
- Graceful degradation: Continue operation if alert fails

### NFR3: Security
- API keys stored as environment variables only
- Read-only API access (no order execution)
- No sensitive data in logs
- HTTPS for all API communications
- Webhook URL protection

### NFR4: Scalability
- Handle 377 coins simultaneously
- Support adding more coins without code changes
- Process 50+ coins per API call (batching)
- Parallel API requests when possible

### NFR5: Maintainability
- Modular architecture (separate concerns)
- Configuration-driven (no hardcoded values)
- Comprehensive logging
- Clear error messages
- Self-documenting code structure

### NFR6: Usability
- One-click Railway deployment
- Simple YAML configuration
- Clear alert formatting
- Helpful error messages
- Status health checks

---

## Risk Considerations

### Market Risks
- High volatility can trigger false signals
- Slippage on fast-moving markets
- Liquidity issues on smaller coins
- Futures-spot price deviations

**Mitigation:**
- Focus on high-liquidity pairs (BTC, ETH, major altcoins)
- Include volume validation in signals
- Set realistic take-profit targets
- User education on market risks

### Technical Risks
- API downtime or rate limiting
- Network latency issues
- Discord/Telegram delivery failures
- Railway.app service disruptions

**Mitigation:**
- Implement retry logic
- Multiple alert channels
- Local logging of all signals
- Fallback to webhook alternatives

### Trading Risks
- System provides signals, not guarantees
- User executes trades manually (human error)
- Over-leveraging if ignoring recommendations
- Emotional trading (ignoring stop-loss)

**Mitigation:**
- Clear disclaimer in documentation
- Risk management education
- Position size calculations
- Conservative default settings

---

## Success Metrics

### System Performance
- Signal latency: <2 seconds (target: <1 second)
- Uptime during trading hours: >99%
- False positive rate: <20%
- Alert delivery success rate: >99.5%

### Trading Performance (User)
- Win rate: Target 55-60% (scalping baseline)
- Average risk:reward: >1.5:1
- Max drawdown: <10% of capital
- Daily profitable sessions: >60%

### User Satisfaction
- Ease of deployment: <30 minutes from zero to running
- Configuration clarity: No support needed for basic setup
- Alert clarity: User understands action without guessing
- System reliability: <2 issues per month

---

## Future Enhancements (Out of Scope - Phase 1)

### Phase 2 (Optional)
- WebSocket real-time streaming (lower latency)
- Machine learning signal optimization
- Automated backtesting interface
- Trade execution API (with user confirmation)
- Simple web dashboard for monitoring

### Phase 3 (Advanced)
- Multi-exchange support (Binance, ByBit)
- Advanced order types (trailing stop-loss)
- Portfolio analytics and performance tracking
- Mobile app (React Native)
- Community signal sharing

---

## Constraints & Assumptions

### Constraints
- Free tier limits: 500 hours/month Railway.app
- CoinDCX API rate limits (public endpoint)
- No automated order execution
- Manual trade execution on CoinDCX platform

### Assumptions
- User has CoinDCX account with futures access
- User understands futures trading risks
- User has Discord or Telegram for alerts
- User trades during IST market hours
- Spot prices correlate with futures prices (0.05-0.1% deviation)

---

## Compliance & Disclaimers

### Legal Disclaimer
- System provides SIGNALS only, not financial advice
- User responsible for all trading decisions
- No profit guarantees or performance warranties
- Past performance does not indicate future results
- System creator not liable for trading losses

### Terms of Use
- For personal use only (no redistribution)
- User must comply with CoinDCX terms of service
- User responsible for tax reporting
- System may stop working if APIs change

---

## Glossary

**Scalping:** Trading strategy with very short hold times (seconds to minutes)  
**Perpetual Contract:** Futures contract with no expiry date  
**Spot Market:** Regular buy/sell without leverage  
**Leverage:** Borrowed capital to amplify position size  
**Stop Loss:** Price level to exit trade and limit loss  
**Take Profit:** Price level to exit trade and lock in profit  
**RSI:** Momentum indicator (oversold <30, overbought >70)  
**MACD:** Trend-following momentum indicator  
**Bollinger Bands:** Volatility indicator using standard deviations  
**Risk:Reward:** Ratio of potential profit to potential loss  
**Available Margin:** Funds available for new positions  
**Used Margin:** Funds locked in open positions  

---

## Document Control

**Version:** 1.0  
**Date:** November 2, 2025  
**Author:** CoinDCX Futures Trading System  
**Status:** Approved for Development  

**Approval:**
- User Requirements: ✅ Confirmed
- Technical Feasibility: ✅ Validated
- Deployment Plan: ✅ Railway.app free tier
- Risk Assessment: ✅ Documented

**Next Steps:**
1. Create system architecture files
2. Implement core scanning engine
3. Build indicator calculations
4. Implement signal generation logic
5. Create alert system
6. Setup Railway deployment
7. User acceptance testing
8. Production deployment

