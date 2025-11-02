# Deployment Guide - CoinDCX Futures Trading System

## Quick Start (Railway.app - Recommended)

### Prerequisites
- GitHub account
- Discord webhook URL ([Create one](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks))
- Railway.app account (free tier: 500 hours/month)

---

## Option 1: One-Click Railway Deployment

### Step 1: Prepare Your Repository
```bash
git add .
git commit -m "Setup futures trading system"
git push origin main
```

### Step 2: Deploy to Railway

1. Go to [Railway.app](https://railway.app/) and sign up/login
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select this repository (`crypto-alerts`)
4. Railway will auto-detect Python and deploy

### Step 3: Configure Environment Variables

In Railway dashboard, go to **Variables** tab and add:

**Required:**
```
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
TZ=Asia/Kolkata
```

**Optional (for Telegram):**
```
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

**Optional (for Personalized Mode):**
```
COINDCX_API_KEY=your_api_key
COINDCX_API_SECRET=your_api_secret
```

### Step 4: Verify Deployment

1. Check **Logs** tab in Railway dashboard
2. You should see: "System initialized successfully"
3. First trading session starts at 10:55 AM IST

### Step 5: Monitor

- View logs in real-time in Railway dashboard
- Receive alerts in your Discord channel
- System runs automatically every trading day

---

## Option 2: Local PC Deployment (Windows)

### Step 1: Install Python

Download and install Python 3.11+ from [python.org](https://www.python.org/downloads/)

### Step 2: Setup Project

```powershell
cd C:\Projects\crypto-alerts

python -m venv .venv

.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Step 3: Configure Environment

Create `.env` file in project root:
```env
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
TZ=Asia/Kolkata
```

### Step 4: Edit Configuration

Edit `config.yaml` to customize:
- Capital amount
- Risk per trade
- Scan interval
- Trading hours

### Step 5: Run System

```powershell
python main.py
```

**To run as Windows Service (Always On):**

1. Install NSSM: `winget install NSSM`
2. Create service:
   ```powershell
   nssm install CryptoAlerts "C:\Projects\crypto-alerts\.venv\Scripts\python.exe" "C:\Projects\crypto-alerts\main.py"
   nssm start CryptoAlerts
   ```

---

## Option 3: GitHub Actions (5-Minute Intervals)

### Step 1: Create Workflow File

Already exists: `.github/workflows/futures-scanner.yml`

### Step 2: Setup GitHub Secrets

Go to **Settings → Secrets and variables → Actions → New repository secret**

Add:
- `DISCORD_WEBHOOK`
- `COINDCX_API_KEY` (optional)
- `COINDCX_API_SECRET` (optional)

### Step 3: Enable Actions

Go to **Actions** tab → Enable workflows

**⚠️ Limitation:** Runs every 5 minutes minimum (not ideal for 1-4 min scalping)

---

## Configuration Guide

### Basic Settings (config.yaml)

**Capital & Risk:**
```yaml
risk:
  total_capital: 100000        # Your trading capital
  risk_per_trade_percent: 2    # Max 2% loss per trade
  max_concurrent_positions: 3  # Max 3 open trades
  default_leverage: 5          # Default 5x leverage
```

**Trading Hours:**
```yaml
trading_hours:
  start_time: "10:55"          # Start 5 min before market
  end_time: "17:05"            # End 5 min after market
  timezone: "Asia/Kolkata"
```

**Scan Frequency:**
```yaml
scanner:
  interval_seconds: 5          # Scan every 5 seconds
                               # Lower = faster signals, higher API usage
                               # Recommended: 3-10 seconds
```

**Signal Quality:**
```yaml
signals:
  min_confidence: 80           # Minimum 80% confidence
  max_alerts_per_scan: 3       # Top 3 signals only
  cooldown_minutes: 2          # Wait 2 min between same coin alerts
```

---

## Personalized Mode Setup

### Step 1: Create Read-Only API Keys

1. Login to [CoinDCX](https://coindcx.com/)
2. Go to **Profile → API Management**
3. Click **"Create New API"**
4. **Important:** Enable ONLY:
   - ✅ Read Account Balance
   - ✅ Read Orders
   - ✅ Read Positions
   - ❌ **Disable** Place Orders
   - ❌ **Disable** Withdrawals
5. Copy API Key and Secret

### Step 2: Configure System

**In config.yaml:**
```yaml
mode: "personalized"

personalized:
  enabled: true
```

**In .env or Railway Variables:**
```
COINDCX_API_KEY=your_api_key_here
COINDCX_API_SECRET=your_api_secret_here
```

### Step 3: Verify

Check logs for:
```
Personalized mode enabled with API integration
Account Balance: ₹100000.00
Available Margin: ₹95000.00
```

---

## Discord Webhook Setup

### Step 1: Create Webhook

1. Open Discord Server
2. Go to **Server Settings → Integrations → Webhooks**
3. Click **"New Webhook"**
4. Name it (e.g., "CoinDCX Signals")
5. Select channel (e.g., #trading-signals)
6. Click **"Copy Webhook URL"**

### Step 2: Test Webhook

```bash
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"content": "Test message from CoinDCX Trading System"}'
```

You should see message in Discord channel.

---

## Telegram Setup (Optional)

### Step 1: Create Bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Follow instructions to create bot
4. Copy the **Bot Token** (format: `123456:ABC-DEF...`)

### Step 2: Get Chat ID

1. Start chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find `"chat":{"id":123456789}` in response
5. Copy the chat ID

### Step 3: Configure

**In config.yaml:**
```yaml
alerts:
  telegram:
    enabled: true
```

**In .env or Railway:**
```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
```

---

## Monitoring & Logs

### Railway.app

- Real-time logs: **Railway Dashboard → Logs tab**
- Metrics: **Railway Dashboard → Metrics tab**
- Usage: Check free tier hours remaining

### Local PC

Logs saved to: `logs/trading.log`

View real-time:
```powershell
Get-Content logs\trading.log -Wait -Tail 50
```

### What to Monitor

**System Health:**
- "System initialized successfully" at startup
- "Trading session started" at 10:55 AM
- No repeated API errors

**Trading Activity:**
- "Generated X signals, sending top Y"
- "Signal sent: SYMBOL DIRECTION at ₹PRICE"
- Confidence scores 80-100%

**Warnings to Watch:**
- "API request failed" (network issues)
- "Max concurrent positions reached"
- "Insufficient margin"

---

## Troubleshooting

### Issue: No Alerts Received

**Check:**
1. Discord webhook URL is correct
2. System is running (check logs)
3. Currently in trading hours (11 AM - 5 PM IST)
4. Confidence threshold not too high

**Test webhook:**
```bash
python -c "import requests; requests.post('YOUR_WEBHOOK', json={'content': 'Test'})"
```

### Issue: "API request failed"

**Solutions:**
1. Check internet connection
2. Verify CoinDCX API is up: https://api.coindcx.com/exchange/ticker
3. Reduce scan frequency in config (5s → 10s)
4. Check Railway logs for specific error

### Issue: Railway App Stopped

**Check:**
1. Free tier hours remaining (500/month)
2. Deployment logs for errors
3. Environment variables are set correctly

**Restart:**
Railway Dashboard → **Deployments → Redeploy**

### Issue: Too Many / Too Few Signals

**Adjust config.yaml:**
```yaml
signals:
  min_confidence: 85           # Increase for fewer, higher quality
  max_alerts_per_scan: 2       # Reduce to top 2 only
  cooldown_minutes: 5          # Increase to spread out alerts
```

### Issue: Personalized Mode Not Working

**Verify:**
1. API keys are correct (no extra spaces)
2. Keys have read permissions enabled on CoinDCX
3. Check logs: "Personalized mode enabled..."
4. Test API manually:
   ```python
   # Test script provided in logs/
   ```

---

## Cost Analysis

### Railway.app Free Tier

**Limits:**
- 500 hours/month free
- 512MB RAM
- Shared CPU

**Our Usage:**
- 6 hours/day × 22 trading days = 132 hours/month
- Plus idle time: ~200 hours/month total
- **Well within free tier ✓**

### Alternative Costs

**Render.com:** 750 hours/month free  
**Fly.io:** 3 shared VMs free  
**Oracle Cloud:** Always free tier (2 VMs)

**Local PC:** $0 but requires PC running

---

## Performance Optimization

### Reduce Latency

1. **Faster scans:** `interval_seconds: 3` (more API calls)
2. **Use parallel requests:** Already enabled
3. **Deploy near Mumbai:** Railway auto-selects region

### Reduce API Usage

1. **Slower scans:** `interval_seconds: 10`
2. **Batch processing:** Already implemented
3. **Cache duration:** `cache_price_data_seconds: 5`

### Balance Quality vs Speed

**Fast Scalping (1-2 min holds):**
```yaml
scanner:
  interval_seconds: 3
signals:
  min_confidence: 85
  max_alerts_per_scan: 2
```

**Moderate Scalping (2-5 min holds):**
```yaml
scanner:
  interval_seconds: 5
signals:
  min_confidence: 80
  max_alerts_per_scan: 3
```

---

## Security Best Practices

1. **Never commit .env file** (already in .gitignore)
2. **Use read-only API keys** for personalized mode
3. **Rotate API keys monthly**
4. **Monitor API usage** on CoinDCX dashboard
5. **Keep Railway variables private**
6. **Don't share webhook URLs publicly**

---

## Backup & Recovery

### Backup Configuration

```bash
cp config.yaml config.yaml.backup
cp .env .env.backup
```

### Export Logs

Railway: **Logs → Export logs**

Local: Logs automatically in `logs/` folder

### Disaster Recovery

1. Keep config files in private repo
2. Document custom settings
3. Export trading history periodically
4. Test deployment on new Railway project

---

## Support & Updates

### Check for Updates

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### Rolling Back

```bash
git log --oneline  # Find commit hash
git checkout <commit-hash>
```

Railway: **Deployments → Select previous deployment → Redeploy**

---

## Next Steps

1. ✅ Deploy to Railway.app
2. ✅ Configure Discord webhook
3. ✅ Customize config.yaml for your strategy
4. ⏳ Test with low capital first (₹10,000)
5. ⏳ Monitor signals for 2-3 days
6. ⏳ Adjust confidence/risk settings
7. ⏳ Enable personalized mode once comfortable
8. ⏳ Scale up capital gradually

**Ready to deploy? Start with Option 1 (Railway) - it's the easiest and most reliable!**

