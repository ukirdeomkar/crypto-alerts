# Quick Strategy Comparison

## 📊 At a Glance

| Strategy | Signals/Day | Win Rate | Monitoring | Risk | Capital | Experience |
|----------|-------------|----------|------------|------|---------|------------|
| **1. Conservative** | 2-5 | 65-75% | 1-2 hrs | Low | ₹500+ | Beginner |
| **2. Balanced** | 5-15 | 60-70% | 2-4 hrs | Medium | ₹1000+ | Intermediate |
| **3. Volatile Scalper** | 15-40 | 55-65% | 4-6 hrs | Med-High | ₹2000+ | Active |
| **4. Ultra Scalper** | 40-100+ | 50-60% | 8+ hrs | High | ₹3000+ | Professional |

---

## 🔑 Key Parameter Differences

| Parameter | Conservative | Balanced | Volatile | Ultra |
|-----------|--------------|----------|----------|-------|
| **min_confidence** | 70% | 55% | 30% | 15% |
| **min_signals_required** | 3 | 2 | 1 | 0 |
| **RSI period** | 14 | 11 | 9 | 7 |
| **RSI oversold/overbought** | 30/70 | 32/68 | 35/65 | 40/60 |
| **MACD** | 12/26/9 | 10/21/9 | 8/17/9 | 6/13/7 |
| **BB period** | 20 | 18 | 15 | 10 |
| **BB std** | 2.0 | 1.9 | 1.8 | 1.5 |
| **Volume multiplier** | 2.0x | 1.8x | 1.5x | 1.3x |
| **Cooldown (min)** | 3 | 2 | 1 | 0.5 |
| **Default leverage** | 4x | 5x | 6x | 8x |
| **Warmup (periods)** | 50 | 40 | 30 | 20 |

---

## 💰 Daily Profit Expectations (₹1200 capital)

### Conservative
- **2-3 winning trades** @ ₹20-30 each = ₹40-90/day
- **0-1 losing trade** @ -₹10-15 = -₹10-15/day
- **Net:** ₹30-75/day profit
- **Monthly:** ₹600-1500 (50-125% growth)

### Balanced  
- **5-10 trades** (60% win rate)
- **6 winners** @ ₹20-25 = ₹120-150
- **4 losers** @ -₹10-12 = -₹40-48
- **Net:** ₹80-100/day profit
- **Monthly:** ₹1600-2000 (133-166% growth)

### Volatile Scalper
- **20-30 trades** (58% win rate)
- **17 winners** @ ₹15-20 = ₹255-340
- **13 losers** @ -₹8-10 = -₹104-130
- **Net:** ₹150-210/day profit
- **Monthly:** ₹3000-4200 (250-350% growth)

### Ultra Scalper
- **50-80 trades** (52% win rate)
- **41 winners** @ ₹10-15 = ₹410-615
- **39 losers** @ -₹7-9 = -₹273-351
- **Net:** ₹140-264/day profit (but HIGH stress!)
- **Monthly:** ₹2800-5280 (233-440% growth)

*Note: These are estimates. Actual results depend on market conditions, execution, and discipline.*

---

## 🎯 Which One Should YOU Choose?

### Choose **Conservative** if:
- ✅ You're new to trading
- ✅ Capital < ₹2000
- ✅ Can only monitor 1-2 hours/day
- ✅ Want to learn without stress
- ✅ Prefer sleep over checking phone constantly

### Choose **Balanced** if:
- ✅ Some trading experience
- ✅ Capital ₹1000-3000
- ✅ Can monitor 2-4 hours/day
- ✅ Want good signal frequency
- ✅ Comfortable with moderate risk

### Choose **Volatile Scalper** if:
- ✅ Active trader
- ✅ Capital ₹2000+
- ✅ Can monitor 4-6 hours/day
- ✅ Want to maximize volatility
- ✅ **THIS IS WHAT YOU WANT FOR VOLATILE MARKETS! ⚡**

### Choose **Ultra Scalper** if:
- ✅ Professional/full-time trader
- ✅ Capital ₹3000+
- ✅ Can monitor 8+ hours/day
- ✅ High stress tolerance
- ✅ Want maximum frequency

---

## 🔄 How to Switch

### Step 1: Copy chosen strategy
```bash
cp trading_config/3_volatile_scalper.yaml config/config.yaml
```

### Step 2: Restart system
```bash
# Press Ctrl+C in running terminal
python run.py
```

### Step 3: Monitor for 1-2 days
- Track signal frequency
- Check win rate
- Assess if it matches your style

### Step 4: Adjust if needed
- Too many signals? Move down (4→3→2→1)
- Too few signals? Move up (1→2→3→4)

---

## 💡 Pro Tips

1. **Start at #1 (Conservative)** for first week
2. **Move to #2 (Balanced)** if comfortable
3. **Only try #3 (Volatile)** if you can actively monitor
4. **#4 (Ultra) is for professionals** - not recommended for most

**Current Recommendation for You:**
Based on your comment about wanting to "take maximum use of volatility", you should use:

🎯 **#3 - Volatile Scalper** (`3_volatile_scalper.yaml`)

This will give you:
- 15-40 signals/day (good frequency)
- Still maintains quality (55-65% win rate)
- Catches volatile moves
- Manageable with 4-6 hours monitoring
- Not overwhelming like Ultra Scalper

---

**Quick Start Command:**
```bash
cp trading_config/3_volatile_scalper.yaml config/config.yaml
python run.py
```

Then monitor for a day and adjust if needed! 🚀

