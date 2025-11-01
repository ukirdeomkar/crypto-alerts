import requests, os, json, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
THRESHOLD = float(os.getenv("THRESHOLD", "5"))
TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS = int(os.getenv("TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS", "30"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GIST_ID = os.getenv("GIST_ID")
PRICES_FILE = Path("prev_prices.json")

def get_all_coindcx_coins():
    try:
        print(f"Fetching all tradeable coins from CoinDCX...")
        response = requests.get("https://api.coindcx.com/exchange/ticker", timeout=10)
        response.raise_for_status()
        tickers = response.json()
        
        inr_markets = []
        for ticker in tickers:
            market = ticker.get("market", "")
            last_price = ticker.get("last_price")
            
            if "INR" in market and last_price is not None:
                try:
                    price = float(last_price)
                    symbol = market.replace("INR", "")
                    
                    inr_markets.append({
                        "id": market.lower(),
                        "symbol": symbol,
                        "name": symbol,
                        "market": market,
                        "current_price": price
                    })
                except (ValueError, TypeError):
                    continue
        
        print(f"Monitoring {len(inr_markets)} coins from CoinDCX\n")
        return inr_markets
        
    except Exception as e:
        print(f"Error fetching top coins: {e}")
        return []

def send_discord_alert(symbol, change, actual_minutes):
    msg = {
        "content": f"⚡ **{symbol}** moved **{change:.2f}%** in last {actual_minutes:.1f} min!"
    }
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json=msg, timeout=10)
        except Exception as e:
            print(f"Failed to send Discord alert: {e}")
    else:
        print(msg["content"])

def send_no_volatility_alert(coins_checked):
    msg = {
        "content": f"✅ No volatile coins found. Checked {coins_checked} coins for {TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS} min volatility ≥{THRESHOLD}%."
    }
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json=msg, timeout=10)
        except Exception as e:
            print(f"Failed to send Discord alert: {e}")
    else:
        print(msg["content"])

def load_previous_prices():
    if GITHUB_TOKEN and GIST_ID:
        try:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            response = requests.get(f"https://api.github.com/gists/{GIST_ID}", headers=headers, timeout=10)
            response.raise_for_status()
            gist_data = response.json()
            content = gist_data.get("files", {}).get("prev_prices.json", {}).get("content", "{}")
            return json.loads(content)
        except Exception as e:
            print(f"Error loading from gist: {e}")
    
    if PRICES_FILE.exists():
        try:
            with open(PRICES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {}

def save_current_prices(price_data):
    if GITHUB_TOKEN and GIST_ID:
        try:
            headers = {
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            payload = {
                "files": {
                    "prev_prices.json": {
                        "content": json.dumps(price_data, indent=2)
                    }
                }
            }
            response = requests.patch(f"https://api.github.com/gists/{GIST_ID}", headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            print("Saved to GitHub Gist")
            return
        except Exception as e:
            print(f"Error saving to gist: {e}")
    
    try:
        with open(PRICES_FILE, 'w') as f:
            json.dump(price_data, f, indent=2)
        print("Saved to local file")
    except Exception as e:
        print(f"Error saving prices: {e}")

def clean_old_entries(history, cutoff_time):
    return {ts: prices for ts, prices in history.items() if float(ts) > cutoff_time}

def main():
    coins = get_all_coindcx_coins()
    if not coins:
        print("No coins data retrieved.")
        return
    
    print(f"Checking {TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS} min volatility...")
    print(f"Alert threshold: ≥{THRESHOLD}%\n")
    
    current_time = int(time.time())
    cutoff_time = current_time - (TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS * 60)
    
    history = load_previous_prices()
    history = clean_old_entries(history, cutoff_time - 3600)
    
    current_prices = {}
    for coin in coins:
        coin_id = coin.get("id")
        current_price = coin.get("current_price")
        if coin_id and current_price:
            current_prices[coin_id] = {
                "price": current_price,
                "name": coin.get("name", coin_id)
            }
    
    history[str(current_time)] = current_prices
    save_current_prices(history)
    
    alerts = []
    for coin_id, coin_data in current_prices.items():
        current_price = coin_data["price"]
        name = coin_data["name"]
        
        old_price = None
        closest_timestamp = None
        min_time_diff = float('inf')
        
        for timestamp in history.keys():
            ts = float(timestamp)
            if ts < current_time and coin_id in history[timestamp]:
                time_diff = abs(ts - cutoff_time)
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_timestamp = timestamp
                    old_price = history[timestamp][coin_id]["price"]
        
        if old_price is None:
            print(f"{name}: no historical data available")
            continue
        
        actual_minutes = (current_time - float(closest_timestamp)) / 60
        change = (current_price - old_price) / old_price * 100
        print(f"{name}: ₹{old_price:.2f} -> ₹{current_price:.2f}, change: {change:.2f}% ({actual_minutes:.1f} min)")
        
        if abs(change) >= THRESHOLD:
            alerts.append((name, change, actual_minutes))
    
    if alerts:
        print(f"\n🚨 {len(alerts)} alert(s) triggered!")
        for sym, chg, mins in alerts:
            send_discord_alert(sym, chg, mins)
    else:
        coins_with_data = sum(1 for coin_id in current_prices if any(
            coin_id in history.get(ts, {}) for ts in history if float(ts) <= cutoff_time
        ))
        print(f"\nNo volatility alerts this run. Checked {coins_with_data} coins.")
        send_no_volatility_alert(coins_with_data)

if __name__ == "__main__":
    main()
