# Deployment Guide - CoinDCX Futures Trading System

## Quick Start (Fly.io - Recommended)

### Prerequisites
- GitHub account
- Discord webhook URL ([Create one](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks))
- Fly.io account (free tier: 3 VMs, 256MB RAM each)

---

## Option 1: Fly.io Deployment (Free Forever)

### Step 1: Install Prerequisites

**Fly CLI (Windows PowerShell):**
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Docker Desktop:**
- Download: https://www.docker.com/products/docker-desktop/
- Install and start Docker Desktop

Restart your terminal after installations.

### Step 2: Login to Fly.io

```bash
fly auth login
```

This opens your browser for authentication.

### Step 3: Create Fly App

```bash
cd C:\Projects\crypto-alerts

fly launch --no-deploy
```

**Configuration prompts:**
- Region: Select **Singapore (sin)** (closest to India)
- Database: **No**
- Deploy now: **No** (we'll set secrets first)

### Step 4: Set Environment Secrets

```bash
# Required
fly secrets set DISCORD_WEBHOOK="https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"

# Optional (Telegram)
fly secrets set TELEGRAM_BOT_TOKEN="your_token"
fly secrets set TELEGRAM_CHAT_ID="your_chat_id"

# Optional (Personalized Mode)
fly secrets set COINDCX_API_KEY="your_key"
fly secrets set COINDCX_API_SECRET="your_secret"
```

### Step 5: Deploy (Local Build)

**Important: Start Docker Desktop first!**

```bash
fly deploy --local-only
```

First deployment takes 2-3 minutes.

**Why `--local-only`?**
- Mumbai region builder not available on free tier
- Local build with Docker works perfectly
- Faster subsequent deploys

### Step 7: Verify Deployment

```bash
# Check if app is running
fly status

# View real-time logs
fly logs

# Check app info
fly info
```

You should see:
```
✅ System initialized successfully
📊 Monitoring: 377 futures pairs
⏰ Trading Hours: 10:55 - 17:05 IST
```

### Step 8: Monitor

```bash
# Real-time logs
fly logs

# Check app status
fly status

# SSH into the container (if needed)
fly ssh console
```

---

## Fly.io Configuration Explained

**`fly.toml` breakdown:**
```toml
app = "crypto-alerts"           # Your app name
primary_region = "sin"          # Singapore (low latency to India)

[vm]
  memory = '256mb'              # Free tier: 256MB RAM
  cpu_kind = 'shared'           # Shared CPU (free tier)
  cpus = 1                      # 1 CPU core
```

**Free Tier Limits:**
- ✅ 3 VMs with 256MB RAM
- ✅ Shared CPU
- ✅ 160GB outbound data/month
- ✅ **No time limits** (unlike Render/Railway)

---

## Managing Your Deployment

### Update Configuration

Edit `config/config.yaml`, then:
```bash
fly deploy
```

### View Logs
```bash
# Tail logs
fly logs

# Last 200 lines
fly logs -n 200
```

### Restart App
```bash
fly apps restart crypto-alerts
```

### Scale Resources (if needed)
```bash
# Upgrade to 512MB (still free tier)
fly scale memory 512

# Check current scaling
fly scale show
```

### Stop App
```bash
fly apps pause crypto-alerts
```

### Resume App
```bash
fly apps resume crypto-alerts
```

### Delete App
```bash
fly apps destroy crypto-alerts
```

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

Create `.env` file:
```env
DISCORD_WEBHOOK=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
```

### Step 4: Run System

```powershell
python run.py
```

### Step 5: Run on Startup (Optional)

**Using Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Crypto Trading Alerts"
4. Trigger: "When I log on"
5. Action: "Start a program"
   - Program: `C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe`
   - Arguments: `run.py`
   - Start in: `C:\Projects\crypto-alerts`
6. Finish

**Or run manually during trading hours:**
```powershell
.venv\Scripts\Activate.ps1
python run.py
```

---

## Troubleshooting

### Fly.io Issues

**"App not responding":**
```bash
fly logs
fly apps restart crypto-alerts
```

**"Out of memory":**
```bash
fly scale memory 512
```

**"Can't connect to API":**
- Check secrets: `fly secrets list`
- Re-set webhook: `fly secrets set DISCORD_WEBHOOK="..."`

**"App keeps restarting":**
```bash
fly logs -n 500
```
Check for Python errors in logs.

### Discord Not Receiving Alerts

1. Check webhook URL:
```bash
fly secrets list
```

2. Test webhook:
```bash
fly ssh console
python -c "import requests; requests.post('YOUR_WEBHOOK', json={'content': 'Test'})"
```

3. Check if system is in trading hours (10:55-17:05 IST)

### System Not Starting

**Check logs:**
```bash
fly logs -n 200
```

**Common issues:**
- Missing environment variables
- Invalid webhook URL
- Timezone not set (should be Asia/Kolkata)

**Verify config:**
```bash
fly ssh console
cat config/config.yaml
```

---

## Cost Optimization

### Fly.io Free Tier (Recommended for Your Use Case)

**Your usage:**
- 1 VM × 256MB RAM
- Runs 6 hours/day (11 AM - 5 PM)
- ~1GB data/month

**Free tier includes:**
- ✅ 3 VMs (you only need 1)
- ✅ 256MB RAM each
- ✅ 160GB data/month
- ✅ **Always free, no expiration**

**Result:** 100% free! ✅

### Auto-Stop (Optional)

If you want to ensure it only runs during trading hours:

**Option 1:** Use cron on another platform to wake/sleep the app
**Option 2:** Just let it run 24/7 (still free)

The system already has built-in trading hours (10:55-17:05), so it won't send alerts outside those times anyway.

---

## Updating Your System

### Update Code

```bash
# Make your changes locally

# Deploy to Fly.io
fly deploy --local-only
```

### Update Configuration

Edit `config/config.yaml` locally, then:
```bash
fly deploy --local-only
```

Changes take effect in ~2 minutes.

### Update Dependencies

Edit `requirements.txt`, then:
```bash
fly deploy --local-only
```

**Note:** Always use `--local-only` flag to avoid Mumbai builder region issue.

---

## Monitoring & Maintenance

### Daily Checks

1. **Check Discord** for session start/end alerts
2. **Verify signals** are being sent
3. **Review logs** (if any issues):
```bash
fly logs -n 50
```

### Weekly Maintenance

1. Check free tier usage:
```bash
fly dashboard
```

2. Review trading performance (if personalized mode)
3. Adjust `min_confidence` if needed

### Monthly Review

1. Check system uptime: `fly status`
2. Review capital growth
3. Adjust position sizing if capital increased

---

## Security Best Practices

### Secrets Management

✅ **DO:**
- Use `fly secrets set` for sensitive data
- Keep `.env` in `.gitignore`
- Use read-only API keys (personalized mode)

❌ **DON'T:**
- Commit secrets to Git
- Share webhook URLs publicly
- Use write-enabled API keys

### API Key Permissions (Personalized Mode)

When creating CoinDCX API keys:
- ✅ Enable: Read account info
- ✅ Enable: Read positions
- ❌ Disable: Place orders
- ❌ Disable: Withdraw funds

---

## Advanced Configuration

### Custom Domain (Optional)

```bash
fly certs add trading-alerts.yourdomain.com
```

### Multiple Environments

**Production:**
```bash
fly deploy --app crypto-alerts-prod
```

**Testing:**
```bash
fly deploy --app crypto-alerts-test
```

### Automated Backups

```bash
# Backup logs weekly
fly logs -n 10000 > backup-$(date +%Y%m%d).log
```

---

## Migration from Other Platforms

### From Railway

1. Export environment variables from Railway
2. Set them in Fly.io:
```bash
fly secrets set DISCORD_WEBHOOK="..."
```
3. Deploy: `fly deploy`
4. Verify, then delete Railway app

### From Render

Same process as Railway - just export env vars and redeploy.

### From Local PC

1. Your `.env` file → Fly.io secrets
2. Deploy: `fly deploy`
3. Keep local setup as backup

---

## Support & Resources

**Fly.io Docs:**
- [Fly.io Documentation](https://fly.io/docs/)
- [Python Apps on Fly.io](https://fly.io/docs/languages-and-frameworks/python/)
- [Fly.io CLI Reference](https://fly.io/docs/flyctl/)

**Project Docs:**
- Configuration: `docs/CONFIGURATION.md`
- Quick Start: `docs/QUICK_START.md`
- Trading Guide: `docs/SMALL_CAPITAL_GUIDE.md`

**Community:**
- Fly.io Community: [community.fly.io](https://community.fly.io)
- Discord: [Fly.io Discord](https://fly.io/discord)

---

## Quick Reference

### Common Commands

```bash
# Deploy
fly deploy

# Logs
fly logs

# Status
fly status

# Restart
fly apps restart crypto-alerts

# SSH access
fly ssh console

# Set secret
fly secrets set KEY="value"

# Scale memory
fly scale memory 512

# Dashboard
fly dashboard
```

### File Structure

```
crypto-alerts/
├── fly.toml              ← Fly.io config
├── Procfile              ← Process definition
├── requirements.txt      ← Python dependencies
├── run.py               ← Entry point
├── .env                 ← Local env vars (not committed)
└── config/
    └── config.yaml      ← Trading configuration
```

### Environment Variables

**Required:**
- `DISCORD_WEBHOOK` - Discord webhook URL

**Optional:**
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Telegram chat ID
- `COINDCX_API_KEY` - CoinDCX API key (personalized mode)
- `COINDCX_API_SECRET` - CoinDCX API secret (personalized mode)

---

**Status:** ✅ Updated for Fly.io deployment
**Last Updated:** November 2, 2025
