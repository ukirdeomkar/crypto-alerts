import requests
import time
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class PriceScanner:
    def __init__(self, config):
        self.config = config
        self.api_endpoint = "https://api.coindcx.com/exchange/ticker"
        self.timeout = config['performance']['api_timeout_seconds']
        self.max_retries = config['performance']['max_api_retries']
        self.cache_duration = config['performance']['cache_price_data_seconds']
        
        self.price_cache = {}
        self.cache_timestamp = None
        self.price_history = defaultdict(lambda: deque(maxlen=100))
        self.volume_history = defaultdict(lambda: deque(maxlen=20))
        
    def fetch_all_tickers(self) -> Optional[Dict]:
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Fetching tickers from CoinDCX API (attempt {attempt + 1}/{self.max_retries})...")
                response = requests.get(self.api_endpoint, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                ticker_dict = {}
                for ticker in data:
                    if isinstance(ticker, dict):
                        market = ticker.get('market', '')
                        ticker_dict[market] = ticker
                
                logger.debug(f"Successfully fetched {len(ticker_dict)} market tickers")
                return ticker_dict
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"API request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("Max retries reached, API unavailable")
                    return None
        
        return None
    
    def get_coin_price_data(self, coin_symbol: str) -> Optional[Dict]:
        market_symbol = f"{coin_symbol}INR"
        
        if self.cache_timestamp and (datetime.now() - self.cache_timestamp).seconds < self.cache_duration:
            if market_symbol in self.price_cache:
                return self.price_cache[market_symbol]
        
        all_tickers = self.fetch_all_tickers()
        if not all_tickers:
            return None
        
        self.price_cache = all_tickers
        self.cache_timestamp = datetime.now()
        
        ticker = all_tickers.get(market_symbol)
        if not ticker:
            return None
        
        try:
            price_data = {
                'symbol': coin_symbol,
                'market': market_symbol,
                'price': float(ticker.get('last_price', 0)),
                'volume': float(ticker.get('volume', 0)),
                'high': float(ticker.get('high', 0)),
                'low': float(ticker.get('low', 0)),
                'change_24h': float(ticker.get('change_24_hour', 0)),
                'timestamp': datetime.now()
            }
            
            if price_data['price'] > 0:
                self.price_history[coin_symbol].append({
                    'price': price_data['price'],
                    'timestamp': price_data['timestamp']
                })
                self.volume_history[coin_symbol].append(price_data['volume'])
                
            return price_data
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error parsing ticker data for {coin_symbol}: {e}")
            return None
    
    def get_bulk_price_data(self, coin_symbols: List[str]) -> Dict[str, Dict]:
        all_tickers = self.fetch_all_tickers()
        if not all_tickers:
            return {}
        
        self.price_cache = all_tickers
        self.cache_timestamp = datetime.now()
        
        results = {}
        for coin_symbol in coin_symbols:
            market_symbol = f"{coin_symbol}INR"
            ticker = all_tickers.get(market_symbol)
            
            if ticker:
                try:
                    price_data = {
                        'symbol': coin_symbol,
                        'market': market_symbol,
                        'price': float(ticker.get('last_price', 0)),
                        'volume': float(ticker.get('volume', 0)),
                        'high': float(ticker.get('high', 0)),
                        'low': float(ticker.get('low', 0)),
                        'change_24h': float(ticker.get('change_24_hour', 0)),
                        'timestamp': datetime.now()
                    }
                    
                    if price_data['price'] > 0:
                        self.price_history[coin_symbol].append({
                            'price': price_data['price'],
                            'timestamp': price_data['timestamp']
                        })
                        self.volume_history[coin_symbol].append(price_data['volume'])
                        results[coin_symbol] = price_data
                        
                except (ValueError, TypeError) as e:
                    logger.error(f"Error parsing ticker for {coin_symbol}: {e}")
                    continue
        
        return results
    
    def get_price_history(self, coin_symbol: str, periods: int = 20) -> List[float]:
        history = self.price_history.get(coin_symbol, deque())
        return [item['price'] for item in list(history)[-periods:]]
    
    def get_volume_history(self, coin_symbol: str) -> List[float]:
        return list(self.volume_history.get(coin_symbol, deque()))
    
    def get_average_volume(self, coin_symbol: str) -> float:
        volumes = self.get_volume_history(coin_symbol)
        return sum(volumes) / len(volumes) if volumes else 0
    
    def has_sufficient_history(self, coin_symbol: str, min_periods: int = 20) -> bool:
        return len(self.price_history.get(coin_symbol, deque())) >= min_periods
    
    def clear_old_history(self, hours: int = 24):
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for coin_symbol in list(self.price_history.keys()):
            history = self.price_history[coin_symbol]
            while history and history[0]['timestamp'] < cutoff_time:
                history.popleft()

