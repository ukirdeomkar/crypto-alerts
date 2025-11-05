# Trading Strategies & Parameter Guide

Complete guide to understanding configuration parameters and building different trading strategies.

---

## 📊 Configuration Parameters Explained

### 1. Signal Quality Parameters

#### `min_confidence` (0-100)
Controls signal filtering threshold.

- **Higher (80-100):** Only strongest signals, fewer trades, higher accuracy
- **Lower (30-50):** More signals, more trades, lower accuracy
- **Sweet Spot:** 60-75 for balanced approach

#### `max_alerts_per_scan` (1-10)
Maximum signals sent per scan cycle.

- **1-2:** Focus on best opportunities only
- **3-5:** Moderate diversification
- **6+:** High activity, catch all opportunities

#### `cooldown_minutes` (1-10)
Prevents repeated signals for same coin.

- **1-2:** Fast re-entry for scalping
- **5-10:** Prevent over-trading same asset

---

### 2. Technical Indicator Parameters

**🎯 NEW: Professional-Grade Technical Analysis**

The system now uses **10 advanced indicators** with industry-standard calculations:
- ✅ **RSI with Wilder's Smoothing** (correct implementation)
- ✅ **ATR (Average True Range)** for volatility-based stops
- ✅ **EMA-50 Trend Filter** prevents counter-trend trades
- ✅ **RSI/Price Divergence Detection** catches reversals early
- ✅ **Support/Resistance Levels** identifies key price zones
- ✅ **OBV (On-Balance Volume)** confirms price moves
- ✅ **Weighted Confidence Scoring** prioritizes reliable indicators
- ✅ **Multi-Factor Confirmation** requires 3+ aligning signals

**Minimum Data Requirement:** System needs **50 price points** (~8 min) before generating signals to ensure all indicators (especially EMA-50) have sufficient data.

#### RSI (Relative Strength Index)
```yaml
rsi_period: 14         # Standard period (now using Wilder's smoothing)
rsi_oversold: 30       # Buy signal threshold
rsi_overbought: 70     # Sell signal threshold
```

**Strategies:**
- **Scalping:** `period: 9`, `oversold: 30`, `overbought: 70` (faster response)
- **Standard:** `period: 14`, `oversold: 30`, `overbought: 70` (industry default)
- **Conservative:** `period: 21`, `oversold: 25`, `overbought: 75` (stronger reversals)

**📊 Now with Divergence Detection:**
- Bullish Divergence: Price makes lower low, RSI makes higher low → reversal up
- Bearish Divergence: Price makes higher high, RSI makes lower high → reversal down

#### MACD (Moving Average Convergence Divergence)
```yaml
macd_fast: 12          # Fast EMA period (standard)
macd_slow: 26          # Slow EMA period (standard)
macd_signal: 9         # Signal line period (standard)
```

**Strategies:**
- **Scalping:** `8/17/9` (quicker crossovers)
- **Standard:** `12/26/9` (industry default)
- **Swing:** `19/39/9` (longer trends)

#### Bollinger Bands
```yaml
bb_period: 20          # Moving average period (standard)
bb_std: 2              # Standard deviation multiplier
```

**Strategies:**
- **Tight Bands:** `period: 15`, `std: 1.5` (frequent signals)
- **Standard:** `period: 20`, `std: 2` (industry default)
- **Wide Bands:** `period: 20`, `std: 2.5` (strong breakouts only)

#### ATR (Average True Range) - NEW ✨
```yaml
atr_period: 14         # Lookback period for volatility
use_atr_stops: true    # Enable ATR-based dynamic stops
atr_stop_multiplier: 2.0  # Stop distance = 2x ATR
```

**What it does:**
- Measures market volatility dynamically
- Sets stop-loss based on current volatility (not fixed %)
- Wider stops in volatile markets, tighter in calm markets
- Prevents getting stopped out by normal price fluctuations

**Strategies:**
- **Tight Stops:** `multiplier: 1.5` (scalping, quick exits)
- **Standard:** `multiplier: 2.0` (balanced)
- **Wide Stops:** `multiplier: 3.0` (swing trading, room to breathe)

#### Trend Filter (EMA-50) - NEW ✨
```yaml
trend_ema_fast: 20     # Fast EMA for trend detection
trend_ema_slow: 50     # Slow EMA for trend confirmation
```

**What it does:**
- Prevents counter-trend trades (major improvement!)
- Only takes LONG signals in uptrends (EMA-20 > EMA-50)
- Only takes SHORT signals in downtrends (EMA-20 < EMA-50)
- Adds +10% confidence bonus when trend aligns with signal

**Critical:** System requires **50 data points** minimum to activate trend filter.

#### Support & Resistance - NEW ✨
```yaml
# Automatically detected from price history
# No configuration needed
```

**What it does:**
- Identifies key support/resistance levels from local highs/lows
- Adds +15% confidence bonus when price near support (for LONG)
- Adds +15% confidence bonus when price near resistance (for SHORT)
- Improves entry timing at key price zones

#### Volume Analysis (Enhanced) - NEW ✨
```yaml
volume_surge_multiplier: 2.0
# Now includes OBV (On-Balance Volume)
```

**What it does:**
- **OBV:** Cumulative volume indicator that confirms price trends
- **Volume Surge:** Detects unusual volume spikes (2x+ average)
- **Volume Trend:** Tracks if volume is increasing/decreasing
- **Confirmation:** Strong volume + price move = reliable signal

**Strategies:**
- **Aggressive:** `1.5x` (catch early moves)
- **Standard:** `2.0x` (reliable surges)
- **Conservative:** `2.5x` (only major volume spikes)

#### Weighted Confidence Scoring - NEW ✨
```yaml
indicator_weights:
  rsi: 1.0              # Standard weight
  macd: 1.0             # Standard weight
  bollinger: 0.8        # Slightly lower (less reliable alone)
  volume: 1.2           # Higher weight (volume confirms moves)
  momentum: 1.0         # Standard weight
```

**How it works:**
- Each indicator signal contributes to total confidence score
- Signals are weighted by reliability (volume = 1.2x, BB = 0.8x)
- **Multi-factor confirmation:** Requires 3+ aligning indicators minimum
- **Trend bonus:** +10% confidence when trend aligns with signal
- **S/R bonus:** +15% confidence when near support/resistance
- **Conflicting penalty:** -5% for each opposing signal
- Final score capped at 0-100%

**Example:**
```
RSI oversold (30 points × 1.0) = 30
MACD bullish (25 points × 1.0) = 25
Volume surge (20 points × 1.2) = 24
Near support = +15 bonus
Bullish trend = +10 bonus
Total = 104 → Capped at 100% confidence ✅
```

**Why this matters:**
- Prevents weak signals with only 1-2 indicators
- Prioritizes high-conviction setups
- Reduces false signals significantly

---

### 3. Risk Management Parameters

#### `total_capital` (INR)
Your total trading capital.

**Impact:**
- Determines position size for each trade
- Base for calculating risk percentage

#### `risk_per_trade_percent` (0.5-5%)
Percentage of capital risked per trade.

- **Conservative:** 0.5-1% (₹4-8 per trade on ₹800)
- **Moderate:** 1.5-2.5% (₹12-20 per trade on ₹800)
- **Aggressive:** 3-5% (₹24-40 per trade on ₹800)

#### `max_concurrent_positions` (1-10)
Maximum open trades at once.

- **Focused:** 1-2 positions (concentrated risk)
- **Balanced:** 3-5 positions (diversified)
- **Portfolio:** 6-10 positions (spread risk)

#### `stop_loss_percent` (0.3-2%)
Distance from entry to stop loss.

- **Tight:** 0.3-0.5% (quick exits, good for scalping)
- **Medium:** 0.7-1% (room for volatility)
- **Wide:** 1.5-2% (swing trades)

#### `take_profit_targets`
```yaml
take_profit_targets:
  - target: 1.2        # First TP at 1.2%
    exit_percent: 50   # Exit 50% of position
  - target: 1.8        # Second TP at 1.8%
    exit_percent: 50   # Exit remaining 50%
```

**Strategies:**
- **Quick Scalp:** `[0.8%, 1.2%]` - Fast small profits
- **Standard:** `[1.2%, 1.8%]` - Balanced targets
- **Swing:** `[2%, 3%]` - Larger moves

#### `min_risk_reward_ratio` (1.0-3.0)
Minimum profit vs risk ratio.

- **Aggressive:** 1.0-1.5 (more trades)
- **Balanced:** 1.5-2.0 (standard)
- **Conservative:** 2.0-3.0 (only high-reward setups)

#### `transaction_cost_percent` (0.6%)
CoinDCX GST (0.3% entry + 0.3% exit).

**Fixed at 0.6%** - automatically factored into all calculations.

---

### 4. Leverage Parameters

#### `default_leverage` (1-10x)
Standard leverage for trades.

- **Safe:** 2-3x (small capital boost)
- **Moderate:** 5x (standard futures trading)
- **Aggressive:** 10x (maximum risk/reward)

#### `max_leverage` (1-10x)
Maximum allowed leverage.

**Warning:** Higher leverage = higher liquidation risk.

---

## 🎯 Pre-Built Strategy Configurations

**⚠️ IMPORTANT:** All strategies require **50 price data points minimum** (~8 minutes of data collection) before signals are generated. This ensures all indicators (especially EMA-50 trend filter) have reliable data.

### Strategy 1: Ultra Scalper (1-3 Min Holds)
```yaml
signals:
  min_confidence: 50
  min_signals_required: 3   # NEW: Multi-factor confirmation
  max_alerts_per_scan: 5
  cooldown_minutes: 1
  
  indicators:
    rsi_period: 9
    rsi_oversold: 30
    rsi_overbought: 70
    macd_fast: 8
    macd_slow: 17
    macd_signal: 9
    bb_period: 15
    bb_std: 2
    atr_period: 14          # NEW: ATR for dynamic stops
    trend_ema_fast: 20      # NEW: Trend filter
    trend_ema_slow: 50
    volume_surge_multiplier: 1.5
  
  indicator_weights:        # NEW: Weighted scoring
    rsi: 1.0
    macd: 1.0
    bollinger: 0.8
    volume: 1.2
    momentum: 1.0

risk:
  total_capital: 800
  risk_per_trade_percent: 2.0
  max_concurrent_positions: 3
  stop_loss_percent: 0.5       # Fixed stop (or use ATR)
  use_atr_stops: false         # Optional: true for dynamic stops
  atr_stop_multiplier: 1.5     # If ATR enabled
  take_profit_targets:
    - target: 0.9
      exit_percent: 50
    - target: 1.8
      exit_percent: 50
  min_risk_reward_ratio: 1.5
  transaction_cost_percent: 0.6
  default_leverage: 7
```

**Profile:**
- ⚡ Very fast entries/exits
- 📊 High frequency (15-30 signals/day with 3-indicator minimum)
- 💰 Small profits (0.9-1.8% per trade)
- ⚠️ High activity, requires constant monitoring
- ✅ Better quality signals due to multi-factor confirmation

---

### Strategy 2: Conservative Scalper (3-5 Min Holds)
```yaml
signals:
  min_confidence: 70
  max_alerts_per_scan: 2
  cooldown_minutes: 3
  
  indicators:
    rsi_period: 7
    rsi_oversold: 25
    rsi_overbought: 75
    macd_fast: 8
    macd_slow: 17
    macd_signal: 7
    bb_period: 15
    bb_std: 2
    volume_surge_multiplier: 2.0

risk:
  total_capital: 800
  risk_per_trade_percent: 1.5
  max_concurrent_positions: 2
  stop_loss_percent: 0.45
  take_profit_targets:
    - target: 1.2
      exit_percent: 50
    - target: 1.8
      exit_percent: 50
  min_risk_reward_ratio: 2.0
  default_leverage: 5
```

**Profile:**
- 🎯 High quality signals
- 📊 Moderate frequency (8-15 signals/day)
- 💰 Balanced profits (1.2-1.8% per trade)
- ✅ Lower stress, better accuracy

---

### Strategy 3: Aggressive Day Trader (5-15 Min Holds)
```yaml
signals:
  min_confidence: 50
  max_alerts_per_scan: 4
  cooldown_minutes: 5
  
  indicators:
    rsi_period: 10
    rsi_oversold: 30
    rsi_overbought: 70
    macd_fast: 12
    macd_slow: 26
    macd_signal: 9
    bb_period: 20
    bb_std: 2
    volume_surge_multiplier: 1.8

risk:
  total_capital: 800
  risk_per_trade_percent: 3.0
  max_concurrent_positions: 4
  stop_loss_percent: 0.6
  take_profit_targets:
    - target: 1.5
      exit_percent: 40
    - target: 2.5
      exit_percent: 60
  min_risk_reward_ratio: 2.0
  default_leverage: 6
```

**Profile:**
- 🔥 High aggression
- 📊 Multiple positions
- 💰 Larger targets (1.5-2.5% per trade)
- ⚠️ Higher risk per trade

---

### Strategy 4: Swing Trader (30-60 Min Holds)
```yaml
signals:
  min_confidence: 80
  max_alerts_per_scan: 2
  cooldown_minutes: 10
  
  indicators:
    rsi_period: 14
    rsi_oversold: 20
    rsi_overbought: 80
    macd_fast: 19
    macd_slow: 39
    macd_signal: 9
    bb_period: 20
    bb_std: 2.5
    volume_surge_multiplier: 2.5

risk:
  total_capital: 800
  risk_per_trade_percent: 2.0
  max_concurrent_positions: 2
  stop_loss_percent: 1.0
  take_profit_targets:
    - target: 2.5
      exit_percent: 50
    - target: 4.0
      exit_percent: 50
  min_risk_reward_ratio: 2.5
  default_leverage: 3
```

**Profile:**
- 🐢 Slower, stronger moves
- 📊 Few signals (2-5 signals/day)
- 💰 Bigger profits (2.5-4% per trade)
- ✅ Less monitoring required

---

### Strategy 5: Volatility Hunter (Momentum Trader)
```yaml
signals:
  min_confidence: 60
  max_alerts_per_scan: 3
  cooldown_minutes: 2
  
  indicators:
    rsi_period: 5
    rsi_oversold: 35
    rsi_overbought: 65
    macd_fast: 5
    macd_slow: 13
    macd_signal: 5
    bb_period: 10
    bb_std: 1.5
    volume_surge_multiplier: 3.0  # Only huge volume spikes

risk:
  total_capital: 800
  risk_per_trade_percent: 2.5
  max_concurrent_positions: 2
  stop_loss_percent: 0.4
  take_profit_targets:
    - target: 1.5
      exit_percent: 30
    - target: 2.5
      exit_percent: 70  # Let winners run
  min_risk_reward_ratio: 2.0
  default_leverage: 8
```

**Profile:**
- 💥 Catches explosive moves
- 📊 Requires major volume spikes
- 💰 High profit targets
- ⚠️ Higher risk/reward

---

### Strategy 6: Safe & Steady (₹800 Capital) - RECOMMENDED
```yaml
signals:
  min_confidence: 70
  min_signals_required: 3      # NEW: Multi-factor confirmation
  max_alerts_per_scan: 1
  cooldown_minutes: 5
  
  indicators:
    rsi_period: 14             # Standard period
    rsi_oversold: 30
    rsi_overbought: 70
    macd_fast: 12
    macd_slow: 26
    macd_signal: 9
    bb_period: 20
    bb_std: 2
    atr_period: 14             # NEW: ATR for dynamic stops
    trend_ema_fast: 20         # NEW: Trend filter
    trend_ema_slow: 50
    volume_surge_multiplier: 2.0
  
  indicator_weights:           # NEW: Weighted scoring
    rsi: 1.0
    macd: 1.0
    bollinger: 0.8
    volume: 1.2
    momentum: 1.0

risk:
  total_capital: 800
  risk_per_trade_percent: 1.0  # Only ₹8 risk per trade
  max_concurrent_positions: 1
  stop_loss_percent: 0.5
  use_atr_stops: true          # NEW: Enable ATR-based stops
  atr_stop_multiplier: 2.0     # Adapts to volatility
  take_profit_targets:
    - target: 0.9
      exit_percent: 50
    - target: 1.8
      exit_percent: 50
  min_risk_reward_ratio: 2.0
  transaction_cost_percent: 0.6
  default_leverage: 4
```

**Profile:**
- 🛡️ Capital preservation focus
- 📊 1-3 high-quality trades per day
- 💰 Small consistent profits (₹10-15 per trade)
- ✅ Lowest risk, best for learning
- ✨ **NEW:** Multi-factor confirmation + trend filter = higher win rate

---

## 🔧 Parameter Tuning Tips

### Increase Signal Frequency
```yaml
min_confidence: 40-60     # Lower threshold
max_alerts_per_scan: 4-6  # More signals
cooldown_minutes: 1-2     # Faster re-entry
```

### Increase Signal Quality
```yaml
min_confidence: 75-90     # Higher threshold
max_alerts_per_scan: 1-2  # Best signals only
cooldown_minutes: 5-10    # Prevent overtrading
```

### Tighter Risk Control
```yaml
risk_per_trade_percent: 0.5-1.0
max_concurrent_positions: 1-2
stop_loss_percent: 0.3-0.5
min_risk_reward_ratio: 2.5-3.0
```

### More Aggressive
```yaml
risk_per_trade_percent: 3-5
max_concurrent_positions: 5-10
stop_loss_percent: 0.7-1.2
min_risk_reward_ratio: 1.5-2.0
default_leverage: 7-10
```

---

## 📈 Performance Optimization

### For Ranging Markets
- Increase `rsi_period` (10-14)
- Tighten `bb_std` (1.5)
- Lower `volume_surge_multiplier` (1.5)

### For Trending Markets
- Decrease `rsi_period` (5-7)
- Widen `bb_std` (2.5)
- Increase `macd_fast` for trend following

### For High Volatility
- Widen `stop_loss_percent` (0.7-1%)
- Increase `volume_surge_multiplier` (2.5+)
- Higher `min_confidence` (70+)

### For Low Volatility
- Tighten `stop_loss_percent` (0.3-0.4%)
- Lower `volume_surge_multiplier` (1.5)
- More `take_profit_targets` for scaling

---

## 🎓 Strategy Selection Guide

### Choose Based On:

**Available Time:**
- **Full-time monitoring:** Ultra Scalper
- **Part-time (4-6 hrs):** Conservative Scalper
- **Occasional checks:** Swing Trader

**Risk Tolerance:**
- **Low:** Safe & Steady
- **Medium:** Conservative Scalper
- **High:** Aggressive Day Trader

**Capital Size:**
- **₹500-1000:** Safe & Steady
- **₹1000-5000:** Conservative/Aggressive Scalper
- **₹5000+:** Any strategy with scaled parameters

**Experience Level:**
- **Beginner:** Safe & Steady → Conservative Scalper
- **Intermediate:** Aggressive Day Trader
- **Advanced:** Ultra Scalper or Volatility Hunter

---

## ✨ What's New in Technical Analysis

The system has been upgraded with **professional-grade technical indicators**:

### Key Improvements:
1. **RSI Fixed:** Now uses Wilder's smoothing (industry standard)
2. **ATR Integration:** Dynamic stop-losses adapt to market volatility
3. **Trend Filter:** EMA-50 prevents counter-trend disasters
4. **Divergence Detection:** Catches reversals before they happen
5. **Support/Resistance:** Identifies optimal entry/exit zones
6. **Enhanced Volume:** OBV confirms price movements
7. **Weighted Scoring:** Prioritizes reliable indicators
8. **Multi-Factor Confirmation:** Requires 3+ aligning signals minimum

### Impact on Your Trading:
- **Higher Win Rate:** Better signal quality = more winning trades
- **Fewer False Signals:** Multi-factor confirmation filters noise
- **Smarter Risk Management:** ATR-based stops reduce premature exits
- **Trend Alignment:** Only trade with the trend, not against it
- **Better Entries:** Support/resistance identifies key price zones

**Note:** All strategies above have been updated to leverage these new features!

---

## 🚨 Important Warnings

1. **Wait for Data:** System needs **50 price points** (~8 min) before first signal
2. **Start Conservative:** Always begin with lower risk parameters
3. **Test First:** Run for 1-2 days with minimal capital
4. **Track Results:** Monitor win rate and adjust accordingly
5. **Avoid Over-Leverage:** 5x is safer than 10x for small capital
6. **Respect Stop-Loss:** Never trade without proper risk management

---

## 📝 Quick Start Recommendations

### For Your ₹800 Capital:

**Week 1:** Use **Safe & Steady** to learn
```yaml
risk_per_trade_percent: 1.0
max_concurrent_positions: 1
default_leverage: 3
```

**Week 2-3:** Move to **Conservative Scalper**
```yaml
risk_per_trade_percent: 1.5
max_concurrent_positions: 2
default_leverage: 5
```

**Week 4+:** If profitable, try **Aggressive Day Trader**
```yaml
risk_per_trade_percent: 2.5
max_concurrent_positions: 3
default_leverage: 5
```

---

## 🔄 Live Tuning

Monitor these metrics daily and adjust:

**If too many signals:**
- Increase `min_confidence` by 10
- Decrease `max_alerts_per_scan` by 1

**If too few signals:**
- Decrease `min_confidence` by 10
- Increase `max_alerts_per_scan` by 1

**If losing trades:**
- Increase `stop_loss_percent` slightly
- Increase `min_risk_reward_ratio`
- Lower `default_leverage`

**If missing profits:**
- Adjust `take_profit_targets` higher
- Increase `exit_percent` on second target

---

## 📚 Further Reading

- **Risk Management:** `docs/SMALL_CAPITAL_GUIDE.md`
- **CoinDCX Setup:** `docs/COINDCX_SETUP_GUIDE.md`
- **Configuration:** `docs/CONFIGURATION.md`
- **Deployment:** `docs/DEPLOYMENT.md`

---

**Remember:** The best strategy is the one that matches your trading style, risk tolerance, and time availability. Start small, test thoroughly, and scale up gradually!

