# Trading Strategy Configurations

This folder contains pre-configured trading strategies for different trading styles and risk tolerances.

## 📁 Available Strategies

| File | Style | Signal Frequency | Risk Level | Best For |
|------|-------|-----------------|------------|----------|
| `1_conservative.yaml` | Quality-focused | Low (2-5/day) | Low | Beginners, capital preservation |
| `2_balanced.yaml` | Mixed approach | Medium (5-15/day) | Medium | Most traders |
| `3_volatile_scalper.yaml` | Active trading | High (15-40/day) | Medium-High | Volatile markets, active monitoring |
| `4_ultra_scalper.yaml` | Maximum signals | Very High (40+/day) | High | Experienced, full-time monitoring |

## 🔧 How to Use

### Option 1: Copy to Main Config (Recommended)
```bash
# Copy your chosen strategy to main config
cp trading_config/3_volatile_scalper.yaml config/config.yaml

# Then restart the system
python run.py
```

### Option 2: Compare & Customize
1. Open your chosen strategy file
2. Compare with `config/config.yaml`
3. Copy only the sections you want to change
4. Restart the system

## 📊 Strategy Details

### 1️⃣ Conservative (DEFAULT)
**Perfect for:** New traders, small capital (₹500-2000), learning phase

**Characteristics:**
- High confidence threshold (70%+)
- Requires 3+ indicators to align
- Industry-standard parameters (RSI-14, MACD 12/26/9)
- Lower leverage (3-5x)
- Fewer but higher-quality signals

**Expected:**
- 2-5 signals per day
- 65-75% win rate
- Lower stress

---

### 2️⃣ Balanced
**Perfect for:** Intermediate traders, ₹2000-5000 capital, part-time trading

**Characteristics:**
- Moderate confidence (50-60%)
- Requires 2+ indicators
- Slightly faster parameters
- Medium leverage (5x)
- Good signal-to-quality ratio

**Expected:**
- 5-15 signals per day
- 60-70% win rate
- Manageable activity level

---

### 3️⃣ Volatile Scalper ⚡
**Perfect for:** Active traders, volatile markets, 4-6 hours monitoring

**Characteristics:**
- Lower confidence (25-40%)
- Single indicator sufficient
- Fast-reacting parameters (RSI-9, MACD 8/17)
- Higher leverage (5-7x)
- Catches more market moves

**Expected:**
- 15-40 signals per day
- 55-65% win rate
- Requires active monitoring

---

### 4️⃣ Ultra Scalper 🚀
**Perfect for:** Professional traders, full-time monitoring, high experience

**Characteristics:**
- Very low confidence (15-30%)
- No minimum indicators required
- Ultra-fast parameters
- Maximum leverage (7-10x)
- Catches every potential move

**Expected:**
- 40-100 signals per day
- 50-60% win rate
- Requires constant attention

---

## ⚙️ Key Parameters Explained

### Signal Quality
- **min_confidence**: Lower = more signals, higher = better quality
- **min_signals_required**: How many indicators must agree (0 = any, 3 = all)

### Indicator Speed
- **rsi_period**: 9 (fast) vs 14 (standard) vs 21 (slow)
- **macd_fast/slow**: 8/17 (fast) vs 12/26 (standard) vs 19/39 (slow)
- **bb_period**: 15 (tight) vs 20 (standard) vs 25 (wide)

### Sensitivity
- **rsi_oversold/overbought**: 35/65 (loose) vs 30/70 (standard) vs 25/75 (tight)
- **bb_std**: 1.5 (tight) vs 2.0 (standard) vs 2.5 (wide)
- **volume_surge_multiplier**: 1.5 (loose) vs 2.0 (standard) vs 2.5 (tight)

### Trading Window
- **cooldown_minutes**: 1 (aggressive) vs 2 (standard) vs 5 (conservative)
- **max_alerts_per_scan**: Higher = more simultaneous signals

---

## 💡 Tips

1. **Start Conservative**: Begin with `1_conservative.yaml` to learn the system
2. **Test Before Live**: Run each strategy for 1-2 days to see signal frequency
3. **Match Your Schedule**: 
   - Can't monitor often? → Conservative or Balanced
   - Full-time available? → Volatile or Ultra Scalper
4. **Adjust Gradually**: Move from 1 → 2 → 3 → 4 as you gain experience
5. **Monitor Win Rate**: If <50%, move to more conservative settings

---

## 🔄 Switching Strategies

It's safe to switch strategies anytime. The system will:
- Keep existing position tracking
- Apply new parameters to future scans
- No need to clear history

**Recommended:** Switch during passive hours or when no positions are open.

---

## 📈 Performance Tracking

After running a strategy for a week, ask yourself:
- ✅ Am I comfortable with the signal frequency?
- ✅ Can I monitor this many signals?
- ✅ Is my win rate acceptable (>55%)?
- ✅ Are profits meeting expectations?

If all YES → Keep it!  
If NO → Move to adjacent strategy (more or less aggressive)

---

**Need help?** Check `docs/TRADING_STRATEGIES.md` for detailed parameter tuning guides.

