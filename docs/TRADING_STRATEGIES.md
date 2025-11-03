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

#### RSI (Relative Strength Index)
```yaml
rsi_period: 5          # Lookback period
rsi_oversold: 30       # Buy signal threshold
rsi_overbought: 70     # Sell signal threshold
```

**Strategies:**
- **Scalping:** `period: 5`, `oversold: 30`, `overbought: 70` (fast response)
- **Swing:** `period: 14`, `oversold: 25`, `overbought: 75` (smoother signals)
- **Conservative:** `period: 21`, `oversold: 20`, `overbought: 80` (strong reversals)

#### MACD (Moving Average Convergence Divergence)
```yaml
macd_fast: 5           # Fast EMA period
macd_slow: 13          # Slow EMA period
macd_signal: 5         # Signal line period
```

**Strategies:**
- **Scalping:** `5/13/5` (quick crossovers)
- **Day Trading:** `12/26/9` (standard settings)
- **Swing:** `19/39/9` (longer trends)

#### Bollinger Bands
```yaml
bb_period: 10          # Moving average period
bb_std: 2              # Standard deviation multiplier
```

**Strategies:**
- **Tight Bands:** `period: 10`, `std: 1.5` (frequent signals)
- **Standard:** `period: 20`, `std: 2` (balanced)
- **Wide Bands:** `period: 20`, `std: 3` (strong breakouts only)

#### Volume Surge
```yaml
volume_surge_multiplier: 2.0
```

**Strategies:**
- **Aggressive:** `1.5x` (catch early moves)
- **Moderate:** `2.0x` (standard)
- **Conservative:** `3.0x` (only major surges)

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

### Strategy 1: Ultra Scalper (1-3 Min Holds)
```yaml
signals:
  min_confidence: 40
  max_alerts_per_scan: 5
  cooldown_minutes: 1
  
  indicators:
    rsi_period: 5
    rsi_oversold: 30
    rsi_overbought: 70
    macd_fast: 5
    macd_slow: 13
    macd_signal: 5
    bb_period: 10
    bb_std: 1.5
    volume_surge_multiplier: 1.5

risk:
  total_capital: 800
  risk_per_trade_percent: 2.0
  max_concurrent_positions: 3
  stop_loss_percent: 0.35
  take_profit_targets:
    - target: 0.7
      exit_percent: 50
    - target: 1.0
      exit_percent: 50
  min_risk_reward_ratio: 1.5
  default_leverage: 7
```

**Profile:**
- ⚡ Very fast entries/exits
- 📊 High frequency (20-50 signals/day)
- 💰 Small profits (0.7-1% per trade)
- ⚠️ High activity, requires constant monitoring

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

### Strategy 6: Safe & Steady (₹800 Capital)
```yaml
signals:
  min_confidence: 75
  max_alerts_per_scan: 1
  cooldown_minutes: 5
  
  indicators:
    rsi_period: 10
    rsi_oversold: 25
    rsi_overbought: 75
    macd_fast: 12
    macd_slow: 26
    macd_signal: 9
    bb_period: 20
    bb_std: 2
    volume_surge_multiplier: 2.0

risk:
  total_capital: 800
  risk_per_trade_percent: 1.0  # Only ₹8 risk per trade
  max_concurrent_positions: 1
  stop_loss_percent: 0.45
  take_profit_targets:
    - target: 1.0
      exit_percent: 50
    - target: 1.5
      exit_percent: 50
  min_risk_reward_ratio: 2.0
  default_leverage: 4
```

**Profile:**
- 🛡️ Capital preservation focus
- 📊 1-3 trades per day
- 💰 Small consistent profits (₹8-12 per trade)
- ✅ Lowest risk, best for learning

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

## 🚨 Important Warnings

1. **Start Conservative:** Always begin with lower risk parameters
2. **Test First:** Run for 1-2 days with minimal capital
3. **Track Results:** Monitor win rate and adjust accordingly
4. **Avoid Over-Leverage:** 5x is safer than 10x for small capital
5. **Respect Stop-Loss:** Never trade without proper risk management

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

