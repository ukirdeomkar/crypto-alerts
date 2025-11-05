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

### Period-Based Trading Hours (Advanced) ⏰

**NEW FEATURE:** Configure different confidence levels and alert limits for different times of the day!

**Perfect for part-time traders who want:**
- More signals during active trading hours
- Fewer but high-quality signals during passive monitoring

```yaml
trading_hours:
  timezone: "Asia/Kolkata"
  periods:
    - name: "active"
      start_time: "07:30"
      end_time: "17:00"
      min_confidence: 55           # Lower threshold = more signals
      max_alerts_per_scan: 4       # More alerts during active hours
    - name: "passive"
      start_time: "17:00"
      end_time: "03:00"
      min_confidence: 80           # Higher threshold = quality only
      max_alerts_per_scan: 2       # Fewer alerts during passive hours
  days: ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
```

**How It Works:**

**Active Period (7:30 AM - 5:00 PM):**
- ✅ More frequent signals (55% confidence minimum)
- ✅ Up to 4 alerts per scan cycle
- ✅ Perfect for when you're available to trade
- 📊 Expected: 15-20 signals per day

**Passive Period (5:00 PM - 3:00 AM):**
- ✅ Only excellent opportunities (80% confidence minimum)
- ✅ Maximum 2 alerts per scan cycle
- ✅ Won't miss major moves while you're busy
- 📊 Expected: 2-5 premium signals

**Example Configurations:**

**Part-Time Trader (Morning + Evening):**
```yaml
periods:
  - name: "morning_active"
    start_time: "09:00"
    end_time: "12:00"
    min_confidence: 50
    max_alerts_per_scan: 5
  - name: "lunch_passive"
    start_time: "12:00"
    end_time: "14:00"
    min_confidence: 85
    max_alerts_per_scan: 1
  - name: "evening_active"
    start_time: "14:00"
    end_time: "18:00"
    min_confidence: 50
    max_alerts_per_scan: 5
  - name: "night_passive"
    start_time: "18:00"
    end_time: "09:00"
    min_confidence: 90
    max_alerts_per_scan: 1
```

**Office Hours Trader:**
```yaml
periods:
  - name: "morning_prep"
    start_time: "08:00"
    end_time: "09:30"
    min_confidence: 60
    max_alerts_per_scan: 3
  - name: "work_hours"
    start_time: "09:30"
    end_time: "18:30"
    min_confidence: 85
    max_alerts_per_scan: 1
  - name: "evening_active"
    start_time: "18:30"
    end_time: "23:00"
    min_confidence: 55
    max_alerts_per_scan: 4
```

**IMPORTANT: Configuration Placement**

When using period-based trading hours:
- ✅ Define `min_confidence` and `max_alerts_per_scan` in EACH period
- ❌ Do NOT define them in the `signals` section (redundant and ignored)

```yaml
# CORRECT - Period-based config
trading_hours:
  periods:
    - name: "active"
      min_confidence: 55          # ✓ Define here
      max_alerts_per_scan: 4      # ✓ Define here

signals:
  cooldown_minutes: 3             # ✓ Keep this
  # min_confidence: NOT HERE!     # ✗ Remove these when using periods
  # max_alerts_per_scan: NOT HERE!
```

**Backward Compatibility:**

If you don't use periods, the old format still works:

```yaml
trading_hours:
  start_time: "10:00"
  end_time: "17:00"
  timezone: "Asia/Kolkata"
  days: ["monday", "tuesday", "wednesday", "thursday", "friday"]

signals:
  min_confidence: 70              # ✓ Define here when NOT using periods
  max_alerts_per_scan: 3          # ✓ Define here when NOT using periods
  cooldown_minutes: 2
```

---

### Scanner Settings 🔍

**Control how frequently the system checks for opportunities:**

```yaml
scanner:
  interval_seconds: 10              # How often to scan (5-60 seconds)
  data_source: "spot"               # Use spot prices for futures signals
  coins_file: "data/futures-coins-filtered.txt"
  batch_size: 50                    # Process 50 coins per API call
  max_history_periods: 100          # Maximum data points to store per coin
  min_history_periods: 50           # Minimum data points before analysis starts
```

**New History Management Parameters (Configurable!):**

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `max_history_periods` | 100 | 50-200 | Maximum historical data points stored per coin |
| `min_history_periods` | 50 | 20-100 | Minimum data points required before generating signals |

**Why This Matters:**
- **`min_history_periods`**: Must be ≥ 50 for EMA-50 trend filter to work properly
  - Set to 30 for faster signals (but trend filter won't work until 50)
  - Set to 50+ for full indicator suite with trend filter active
- **`max_history_periods`**: Higher = more memory usage, but better long-term analysis
  - 100 periods = ~16 minutes of data at 10-second intervals
  - 200 periods = ~33 minutes of data

**⚠️ IMPORTANT:** 
- If you lower `min_history_periods` below 50, the trend filter (EMA-50) won't activate
- RSI needs 14 periods minimum, MACD needs 26, Bollinger Bands needs 20
- Recommended: Keep at 50 for professional-grade analysis

**Recommendations:**

| Trading Style | Interval | min_history | Why |
|--------------|----------|-------------|-----|
| **Ultra-fast scalping (30s-2min)** | 5 seconds | 30 | Faster signals (no trend filter) |
| **Fast scalping (1-4min)** | 10 seconds | 50 | Full indicators with trend filter |
| **Moderate scalping (3-10min)** | 10-15 seconds | 50 | Quality signals, less noise |
| **Swing trading (>15min)** | 30-60 seconds | 60 | Long-term trends only |

---

### Signal Generation 🎯

**Control signal quality and frequency:**

> **NOTE:** If using period-based trading hours, `min_confidence` and `max_alerts_per_scan` are defined in EACH period, not here!

```yaml
signals:
  # Only define these if NOT using period-based trading hours:
  # min_confidence: 80           # Minimum confidence score (0-100)
  # max_alerts_per_scan: 3       # Top N signals per scan
  
  cooldown_minutes: 2          # Wait time between alerts for same coin
  min_signals_required: 3      # NEW: Minimum indicators needed (was 2)
  
  indicators:
    # UPDATED: Industry-standard parameters (November 2025)
    rsi_period: 14             # RSI period (Wilder's original: 14)
    rsi_oversold: 30           # Buy signal threshold
    rsi_overbought: 70         # Sell signal threshold
    
    macd_fast: 12              # MACD fast line (Appel's original: 12)
    macd_slow: 26              # MACD slow line (Appel's original: 26)
    macd_signal: 9             # MACD signal line (Appel's original: 9)
    
    bb_period: 20              # Bollinger Bands period (Bollinger's original: 20)
    bb_std: 2                  # Standard deviations
    
    # NEW: Additional professional indicators
    atr_period: 14             # Average True Range period
    trend_ema_fast: 20         # Fast EMA for trend filter
    trend_ema_slow: 50         # Slow EMA for trend filter
    
    volume_surge_multiplier: 2.0  # Volume surge = 2x average
  
  # NEW: Weighted confidence scoring
  indicator_weights:
    rsi: 1.0
    macd: 1.2
    trend: 1.5                 # Trend filter most important
    volume: 1.0
    momentum: 0.8
    divergence: 1.3            # Divergence highly valued
    support_resistance: 1.1
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
  
  # NEW: ATR-based dynamic stops (adapts to market volatility)
  use_atr_stops: true            # Enable ATR-based stops (optional)
  atr_stop_multiplier: 2.0       # Stop = Entry ± (ATR × 2.0)
  
  stop_loss_percent: 0.5         # Fixed stop loss (if ATR disabled)
  take_profit_targets:
    - target: 0.9                # Target 1: +0.9%
      exit_percent: 50           # Exit 50% of position
    - target: 1.8                # Target 2: +1.8%
      exit_percent: 50           # Exit remaining 50%
  
  min_risk_reward_ratio: 1.5     # Minimum risk:reward (1:1.5)
  transaction_cost_percent: 0.6  # GST fees (0.3% entry + 0.3% exit)
  position_expiry_minutes: 10    # Auto-cleanup in generic mode
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

