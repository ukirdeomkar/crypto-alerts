# Configuration Guide

## Environment Variables

### Local Development (.env file)
```env
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_WEBHOOK_URL
THRESHOLD=5
TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS=30
```

### GitHub Actions

**Secrets (Settings → Secrets and variables → Actions → Secrets):**
- `DISCORD_WEBHOOK` - Your Discord webhook URL

**Variables (Settings → Secrets and variables → Actions → Variables):**
- `THRESHOLD` - Minimum % change to trigger alert (default: 5)
- `TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS` - Minutes to compare prices (default: 30)

## Cron Schedule vs Volatility Check Period

**Important:** The workflow cron schedule and volatility check period work together:

### Current Configuration:
- **Cron runs:** Every 15 minutes (defined in `.github/workflows/volatality.yml`)
- **Volatility check:** 30 minutes (checks prices from 30 min ago)
- **Result:** Each run compares with data from 2 runs ago

### To Change Cron Schedule:

Edit `.github/workflows/volatality.yml`:

```yaml
schedule:
  - cron: "*/15 * * * *"  # Every 15 minutes
```

**Common schedules:**
- `*/15 * * * *` - Every 15 minutes
- `*/30 * * * *` - Every 30 minutes
- `0 * * * *` - Every hour at minute 0
- `0 */2 * * *` - Every 2 hours

### Recommended Combinations:

| Cron Interval | Volatility Check | Description |
|---------------|------------------|-------------|
| 15 min | 30 min | More frequent monitoring (recommended) |
| 30 min | 30 min | Check same interval volatility |
| 15 min | 60 min | Check longer-term moves frequently |
| 30 min | 60 min | Less frequent, longer-term volatility |

**Note:** Volatility check period should be ≥ cron interval. For example, don't check 15-min volatility if cron runs every 30 min.

