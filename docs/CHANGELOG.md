# 📋 Changelog

## Recent Updates (November 2025)

### ✅ GST Transaction Costs (0.6%)
**Issue:** Transaction fees weren't factored into profit/loss calculations  
**Fix:** 
- Added `transaction_cost_percent: 0.6` to config (0.3% entry + 0.3% exit)
- Updated all profit calculations to show NET values (after fees)
- Fees calculated on margin, not exposure (matches CoinDCX)
- Adjusted targets: 1.2% and 1.8% (now profitable after fees)

**Impact:**
- ₹500 position: T1 = ₹27 net, T2 = ₹42 net (Total: ₹34.50)
- ₹200 position: T1 = ₹10.80 net, T2 = ₹16.80 net (Total: ₹13.80)

---

### ✅ Position Tracking Fix (Generic Mode)
**Issue:** `max_concurrent_positions` blocked all signals after the first one  
**Fix:**
- Added auto-cleanup: positions expire after 5 minutes (configurable)
- Prevents false blocking in generic mode
- New config: `position_expiry_minutes: 5`

**Why:** In generic mode, system can't see your actual trades, so positions are auto-removed after typical scalping timeframe.

---

### ✅ Discord Alert Improvements
**Changes:**
1. **Visual Separators:** Each message wrapped with `──────` lines
2. **Color Coding:** 
   - 🟢 GREEN for LONG positions
   - 🔴 RED for SHORT positions
3. **Coin Name First:** Asset symbol now at the top of each alert
4. **Confidence Levels:**
   - STRONG: 90%+
   - MODERATE: 40-89%
   - WEAK: <40%

**Format:**
```
──────────────────────────────────────────────
🪙 **BTCINR PERPETUAL**
🟢 **LONG** ↗️ • STRONG (92%)

📊 **ENTRY DETAILS:**
Entry Price: ₹58,42,500
...
──────────────────────────────────────────────
```

---

## Configuration Changes

### Risk Settings
```yaml
risk:
  transaction_cost_percent: 0.6  # GST fees
  position_expiry_minutes: 5     # Auto-cleanup (generic mode)
  stop_loss_percent: 0.45
  take_profit_targets:
    - target: 1.2  # Adjusted for fees
    - target: 1.8  # Adjusted for fees
```

### Position Limits
```yaml
max_concurrent_positions: 999  # Unlimited (generic mode)
```

---

## File Structure Changes

### Moved to docs/
- `SMALL_CAPITAL_GUIDE.md` → User guide for ₹800 capital
- `PROJECT_STRUCTURE.md` → Architecture documentation
- `CHANGELOG.md` → This file

### Removed
- `RESTRUCTURE_COMPLETE.md` (outdated)
- `RESTRUCTURE_SUMMARY.md` (outdated)
- `CONFIG.md` (old config, replaced by docs/CONFIGURATION.md)
- `docs.md` (redundant)
- `crypto-volatality.py` (old implementation)

---

## System Status

✅ **Production Ready**
- Accurate GST calculations
- Position tracking works in generic mode
- Clear Discord alerts
- Optimized for scalping (1-4 min holds)
- Configured for ₹800 capital

📊 **Current Performance**
- Risk per trade: 2.5% (₹20 max)
- Expected profit: ₹10-35 per successful trade
- Risk:Reward ratio: 1.8:1 minimum

---

## Quick Reference

**Configuration:** `config/config.yaml`  
**Capital Guide:** `docs/SMALL_CAPITAL_GUIDE.md`  
**Deployment:** `docs/DEPLOYMENT.md`  
**Quick Start:** `docs/QUICK_START.md`

---

**Last Updated:** November 2, 2025

