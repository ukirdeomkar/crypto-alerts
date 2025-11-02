# Deploy to Fly.io - Working Solution

## The Problem
Fly.io tried to create builder in Mumbai (bom) region, which isn't available on free tier.

## The Solution
Build locally with Docker, then deploy to Singapore region.

---

## Deploy Command (Verified Working)

```bash
fly deploy --local-only
```

**Requirements:**
- Docker Desktop must be running
- Builds on your local machine
- Uploads to Fly.io Singapore region

---

## First Time Setup

1. **Install Docker Desktop** (if not already installed)
   - Download: https://www.docker.com/products/docker-desktop/
   - Start Docker Desktop before deploying

2. **Login to Fly.io**
   ```bash
   fly auth login
   ```

3. **Set your Discord webhook**
   ```bash
   fly secrets set DISCORD_WEBHOOK="https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
   ```

4. **Deploy**
   ```bash
   fly deploy --local-only
   ```

---

## Files Created

1. **Dockerfile** - Tells Fly.io how to build your app
2. **fly.toml** - Simplified config (removed buildpacks)

---

## After Deployment

### Check Status
```bash
fly status
```

### View Logs
```bash
fly logs
```

### Check if Running
```bash
fly info
```

You should see:
- ✅ App: crypto-alerts
- ✅ Region: sin (Singapore)
- ✅ Status: running

---

## Verify Your Trading System

In the logs, look for:
```
✅ System initialized successfully
📊 Monitoring: 377 futures pairs
⏰ Trading Hours: 10:55 - 17:05 IST
```

You should also receive a startup alert in Discord!

---

## Update Your System

When you make changes to code or config:

```bash
fly deploy --local-only
```

Takes ~2-3 minutes to build and deploy.

---

## Troubleshooting

**"Cannot connect to Docker daemon"**
- Start Docker Desktop
- Wait for it to fully start (whale icon in system tray)
- Run deploy command again

**App won't start?**
Check logs:
```bash
fly logs -n 100
```

**Want faster deploys?**
Keep Docker Desktop running in background.

---

## That's It!

Your trading system is now deployed on Fly.io in Singapore region, running 24/7 (only alerting during your trading hours 10:55 AM - 5:05 PM IST).

**Free tier includes:**
- ✅ 3 VMs with 256MB RAM each
- ✅ 160GB data/month
- ✅ No time limits
- ✅ Always-on (no sleep)

You're using: 1 VM, ~1GB/month = **100% FREE** 🎉
