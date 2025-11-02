# ⚙️ Configuration Guide

Complete guide to configuring the CoinDCX Futures Trading System.

---

## 📁 Configuration Files

### 1. `config/config.yaml` - Main Configuration
All trading parameters, risk settings, and system behavior.

### 2. `.env` - Environment Variables
Sensitive data like API keys, webhooks, and secrets.

---

## 🎯 Main Configuration (`config/config.yaml`)

### Trading Hours ⏰

**Customize when the system actively monitors and sends signals:**

```yaml
trading_hours:
  start_time: "10:55"      # Trading session starts (pre-market prep)
  end_time: "17:05"        # Trading session ends
  timezone: "Asia/Kolkata" # IST timezone
  days: ["monday", "tuesday", "wednesday", "thursday", "friday"]
```

**Examples:**

**Standard Market Hours:**
```yaml
trading_hours:
  start_time: "11:00"   # 11 AM IST
  end_time: "17:00"     # 5 PM IST
```

**Extended Hours:**
```yaml
trading_hours:
  start_time: "09:00"   # 9 AM IST
  end_time: "20:00"     # 8 PM IST
```

**US Market Hours (for global coins):**
```yaml
trading_hours:
  start_time: "19:00"   # 7 PM IST (overlap with US open)
  end_time: "01:30"     # 1:30 AM IST (next day)
```

**Weekend Trading:**
```yaml
trading_hours:
  days: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
```

---

### Scanner Settings 🔍

**Control how frequently the system checks for opportunities:**

```yaml
scanner:
  interval_seconds: 5        # How often to scan (1-60 seconds)
  data_source: "spot"        # Use spot prices for futures signals
  coins_file: "data/futures-coins-filtered.txt"
  batch_size: 50             # Process 50 coins per API call
```

**Recommendations:**

| Trading Style | Interval | Why |
|--------------|----------|-----|
| **Ultra-fast scalping (30s-2min)** | 1-3 seconds | Catch quick moves |
| **Fast scalping (1-4min)** | 3-5 seconds | Balance speed & API usage |
| **Moderate scalping (3-10min)** | 5-10 seconds | Less noise, quality signals |
| **Swing trading (>15min)** | 15-30 seconds | Long-term moves only |

---

### Signal Generation 🎯

**Control signal quality and frequency:**

```yaml
signals:
  min_confidence: 80           # Minimum confidence score (0-100)
  max_alerts_per_scan: 3       # Top N signals per scan
  cooldown_minutes: 2          # Wait time between alerts for same coin
  
  indicators:
    rsi_period: 5              # RSI period (lower = faster)
    rsi_oversold: 30           # Buy signal threshold
    rsi_overbought: 70         # Sell signal threshold
    
    macd_fast: 5               # MACD fast line
    macd_slow: 13              # MACD slow line
    macd_signal: 5             # MACD signal line
    
    bb_period: 10              # Bollinger Bands period
    bb_std: 2                  # Standard deviations
    
    volume_surge_multiplier: 2.0  # Volume surge = 2x average
```

**Signal Quality Presets:**

**Conservative (High Quality, Fewer Signals):**
```yaml
signals:
  min_confidence: 85
  max_alerts_per_scan: 2
  cooldown_minutes: 5
```

**Balanced (Default):**
```yaml
signals:
  min_confidence: 80
  max_alerts_per_scan: 3
  cooldown_minutes: 2
```

**Aggressive (More Signals, Lower Quality):**
```yaml
signals:
  min_confidence: 75
  max_alerts_per_scan: 5
  cooldown_minutes: 1
```

---

### Risk Management 💰

**Configure position sizing, leverage, and risk limits:**

```yaml
risk:
  total_capital: 100000          # Your total trading capital (₹)
  risk_per_trade_percent: 2      # Max loss per trade (%)
  
  max_concurrent_positions: 3    # Max open trades at once
  max_leverage: 10               # Maximum allowed leverage
  default_leverage: 5            # Default leverage for signals
  
  stop_loss_percent: 0.3         # Stop loss distance (%)
  take_profit_targets:
    - target: 0.3                # Target 1: +0.3%
      exit_percent: 50           # Exit 50% of position
    - target: 0.6                # Target 2: +0.6%
      exit_percent: 50           # Exit remaining 50%
  
  min_risk_reward_ratio: 1.5     # Minimum risk:reward (1:1.5)
```

**Risk Profiles:**

**Conservative (Low Risk):**
```yaml
risk:
  total_capital: 100000
  risk_per_trade_percent: 1      # Only 1% risk
  max_concurrent_positions: 2
  default_leverage: 3            # Lower leverage
  stop_loss_percent: 0.5         # Wider stop loss
```

**Moderate (Balanced):**
```yaml
risk:
  total_capital: 100000
  risk_per_trade_percent: 2      # 2% risk
  max_concurrent_positions: 3
  default_leverage: 5
  stop_loss_percent: 0.3
```

**Aggressive (Higher Risk):**
```yaml
risk:
  total_capital: 100000
  risk_per_trade_percent: 3      # 3% risk
  max_concurrent_positions: 5
  default_leverage: 7            # Higher leverage
  stop_loss_percent: 0.2         # Tighter stop
```

---

### Personalized Mode 🔐

**Account-aware signals using CoinDCX API:**

```yaml
personalized:
  enabled: false                        # Enable after setting API keys
  api_endpoint: "https://api.coindcx.com"
  max_margin_per_trade_percent: 10     # Max 10% of available margin
  refresh_interval_seconds: 30          # Update account data frequency
  track_pnl: true                       # Track profit/loss
  send_position_updates: true           # Send position update alerts
  update_interval_minutes: 1            # Position update frequency
```

**To Enable:**
1. Create read-only API keys on CoinDCX
2. Add to `.env`:
   ```env
   COINDCX_API_KEY=your_key
   COINDCX_API_SECRET=your_secret
   ```
3. Update config:
   ```yaml
   mode: "personalized"
   personalized:
     enabled: true
   ```

---

### Alert Channels 📱

**Configure Discord and Telegram notifications:**

```yaml
alerts:
  discord:
    enabled: true
    webhook_env_var: "DISCORD_WEBHOOK"
    
  telegram:
    enabled: false                      # Set to true to enable
    bot_token_env_var: "TELEGRAM_BOT_TOKEN"
    chat_id_env_var: "TELEGRAM_CHAT_ID"
  
  send_entry_signals: true              # Entry signal alerts
  send_exit_signals: true               # Exit signal alerts
  send_position_updates: true           # Position update alerts
  send_daily_summary: true              # End-of-day summary
  
  include_charts: false                 # Future: Chart images
  use_mentions: false                   # Discord @mentions
```

---

### Logging 📝

**Configure system logging:**

```yaml
logging:
  level: "INFO"                         # DEBUG, INFO, WARNING, ERROR
  file: "logs/trading.log"
  max_file_size_mb: 10                  # Max log file size
  backup_count: 5                       # Number of backup logs
  log_signals: true                     # Log all generated signals
  log_api_calls: false                  # Log API requests (debug)
```

**Log Levels:**
- **DEBUG:** Very detailed (for troubleshooting)
- **INFO:** Normal operations (recommended)
- **WARNING:** Important warnings only
- **ERROR:** Errors only

---

### Performance ⚡

**Optimize system performance:**

```yaml
performance:
  cache_price_data_seconds: 5           # Cache duration
  max_api_retries: 3                    # Retry failed requests
  api_timeout_seconds: 10               # API timeout
  parallel_requests: true               # Process coins in parallel
```

---

## 🔐 Environment Variables (`.env`)

Create `.env` file in project root:

```env
# Required
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN

# Optional (for Telegram)
TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF...
TELEGRAM_CHAT_ID=123456789

# Optional (for Personalized Mode)
COINDCX_API_KEY=your_read_only_api_key
COINDCX_API_SECRET=your_api_secret

# Timezone
TZ=Asia/Kolkata
```

**Security Notes:**
- ✅ Never commit `.env` to git (already in `.gitignore`)
- ✅ Use read-only API keys
- ✅ Rotate keys regularly
- ✅ Keep webhook URLs private

---

## 🎨 Configuration Examples

### Example 1: Day Trader (9 AM - 5 PM)

```yaml
trading_hours:
  start_time: "09:00"
  end_time: "17:00"

scanner:
  interval_seconds: 5

signals:
  min_confidence: 80
  max_alerts_per_scan: 3

risk:
  total_capital: 200000
  risk_per_trade_percent: 2
  default_leverage: 5
```

### Example 2: Night Scalper (8 PM - 2 AM)

```yaml
trading_hours:
  start_time: "20:00"
  end_time: "02:00"
  days: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

scanner:
  interval_seconds: 3

signals:
  min_confidence: 85
  max_alerts_per_scan: 2

risk:
  total_capital: 100000
  risk_per_trade_percent: 1.5
  default_leverage: 7
```

### Example 3: Conservative Swing Trader

```yaml
trading_hours:
  start_time: "10:00"
  end_time: "16:00"

scanner:
  interval_seconds: 15

signals:
  min_confidence: 85
  max_alerts_per_scan: 2
  cooldown_minutes: 10

risk:
  total_capital: 500000
  risk_per_trade_percent: 1
  max_concurrent_positions: 2
  default_leverage: 3
  stop_loss_percent: 0.5
  take_profit_targets:
    - target: 1.0
      exit_percent: 50
    - target: 2.0
      exit_percent: 50
```

---

## ✅ Validation & Testing

### Test Your Configuration

```bash
cd C:\Projects\crypto-alerts

# Test config loads correctly
python -c "from app.utils import load_config; config = load_config(); print('✅ Config valid')"

# Test with dry run
python run.py
```

### Common Issues

**Issue: "Config file not found"**
- Solution: Ensure `config/config.yaml` exists
- Check you're running from project root

**Issue: "Trading hours not working"**
- Solution: Verify timezone is correct (`Asia/Kolkata`)
- Check system time matches IST

**Issue: "Too many/too few signals"**
- Adjust `min_confidence` (higher = fewer signals)
- Adjust `max_alerts_per_scan`
- Increase `cooldown_minutes`

---

## 📊 Quick Reference

### Most Important Settings

| Setting | Default | Effect |
|---------|---------|--------|
| `trading_hours.start_time` | "10:55" | When to start monitoring |
| `trading_hours.end_time` | "17:05" | When to stop monitoring |
| `scanner.interval_seconds` | 5 | Scan frequency |
| `signals.min_confidence` | 80 | Signal quality threshold |
| `risk.total_capital` | 100000 | Your trading capital |
| `risk.risk_per_trade_percent` | 2 | Max loss per trade |
| `risk.default_leverage` | 5 | Default leverage |

---

## 🔄 Making Changes

1. **Edit** `config/config.yaml`
2. **Save** the file
3. **Restart** the application:
   ```bash
   # Local
   python run.py
   
   # Railway
   git add config/config.yaml
   git commit -m "Update configuration"
   git push origin main
   ```

Changes take effect immediately on restart!

---

## 📞 Need Help?

- **Configuration issues:** Check logs at `logs/trading.log`
- **Signal quality:** Adjust `min_confidence` and indicators
- **Risk management:** Start conservative, increase gradually
- **Trading hours:** Test different windows based on volatility

---

**Happy Configuring! ⚙️**

