import requests, os, json, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
THRESHOLD = float(os.getenv("THRESHOLD", "5"))
TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS = int(os.getenv("TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS", "30"))
PRICES_FILE = Path("prev_prices.json")

def get_top_30_coins_by_24h_change():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    all_coins = []
    
    try:
        for page in range(1, 6):
            params = {
                "vs_currency": "inr",
                "order": "market_cap_desc",
                "per_page": 250,
                "page": page,
                "price_change_percentage": "24h"
            }
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            coins = response.json()
            if not coins:
                break
            all_coins.extend(coins)
        
        valid_coins = [
            c for c in all_coins 
            if c.get("price_change_percentage_24h") is not None
            and c.get("current_price") is not None
            and c.get("current_price") > 0
        ]
        
        sorted_coins = sorted(
            valid_coins,
            key=lambda x: abs(x.get("price_change_percentage_24h", 0)),
            reverse=True
        )
        
        return sorted_coins[:30]
        
    except Exception as e:
        print(f"Error fetching top coins: {e}")
        return []

def send_discord_alert(symbol, change):
    msg = {
        "content": f"⚡ **{symbol}** moved **{change:.2f}%** in last {TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS} min!"
    }
    if DISCORD_WEBHOOK:
        try:
            requests.post(DISCORD_WEBHOOK, json=msg, timeout=10)
        except Exception as e:
            print(f"Failed to send Discord alert: {e}")
    else:
        print(msg["content"])

def load_previous_prices():
    if not PRICES_FILE.exists():
        return {}
    try:
        with open(PRICES_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_current_prices(price_data):
    try:
        with open(PRICES_FILE, 'w') as f:
            json.dump(price_data, f, indent=2)
    except Exception as e:
        print(f"Error saving prices: {e}")

def clean_old_entries(history, cutoff_time):
    return {ts: prices for ts, prices in history.items() if float(ts) > cutoff_time}

def main():
    print(f"Fetching top 30 most volatile coins (by 24h % change)...")
    
    coins = get_top_30_coins_by_24h_change()
    if not coins:
        print("No coins data retrieved.")
        return
    
    print(f"\nTop 30 coins by 24h volatility:")
    for i, coin in enumerate(coins[:10], 1):
        name = coin.get("name", "Unknown")
        change_24h = coin.get("price_change_percentage_24h", 0)
        print(f"  {i}. {name}: {change_24h:+.2f}% (24h)")
    print(f"  ... and 20 more\n")
    
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
        for timestamp in sorted(history.keys()):
            if float(timestamp) <= cutoff_time:
                if coin_id in history[timestamp]:
                    old_price = history[timestamp][coin_id]["price"]
        
        if old_price is None:
            print(f"{name}: no data from {TIME_INTERVAL_BETWEEN_VOLATALITY_CHECKS} min ago (first run or new coin)")
            continue
        
        change = (current_price - old_price) / old_price * 100
        print(f"{name}: ₹{old_price:.2f} -> ₹{current_price:.2f}, change: {change:.2f}%")
        
        if abs(change) >= THRESHOLD:
            alerts.append((name, change))
    
    if alerts:
        print(f"\n🚨 {len(alerts)} alert(s) triggered!")
        for sym, chg in alerts:
            send_discord_alert(sym, chg)
    else:
        print("\nNo volatility alerts this run.")

if __name__ == "__main__":
    main()
