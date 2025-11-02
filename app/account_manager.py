import requests
import hmac
import hashlib
import json
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class AccountManager:
    def __init__(self, config, api_key: str, api_secret: str):
        self.config = config
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_endpoint = config['personalized']['api_endpoint']
        self.timeout = config['performance']['api_timeout_seconds']
        
        self.account_balance = {}
        self.open_positions = []
        self.last_refresh = None
        
    def _generate_signature(self, secret: str, payload: str) -> str:
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_authenticated_request(self, endpoint: str, payload: Dict) -> Optional[Dict]:
        try:
            secret_bytes = bytes(self.api_secret, encoding='utf-8')
            payload_json = json.dumps(payload, separators=(',', ':'))
            signature = hmac.new(secret_bytes, payload_json.encode(), hashlib.sha256).hexdigest()
            
            headers = {
                'Content-Type': 'application/json',
                'X-AUTH-APIKEY': self.api_key,
                'X-AUTH-SIGNATURE': signature
            }
            
            url = f"{self.api_endpoint}{endpoint}"
            response = requests.post(url, data=payload_json, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            return None
    
    def fetch_account_balance(self) -> Optional[Dict]:
        timestamp = int(time.time() * 1000)
        payload = {
            'timestamp': timestamp
        }
        
        result = self._make_authenticated_request('/exchange/v1/users/balances', payload)
        
        if result:
            self.account_balance = self._parse_balance(result)
            self.last_refresh = datetime.now()
            return self.account_balance
        
        return None
    
    def _parse_balance(self, balance_data: List[Dict]) -> Dict:
        total_inr = 0
        available_inr = 0
        locked_inr = 0
        
        for asset in balance_data:
            if asset.get('currency') == 'INR':
                available_inr = float(asset.get('balance', 0))
                locked_inr = float(asset.get('locked_balance', 0))
                total_inr = available_inr + locked_inr
                break
        
        return {
            'total_balance': total_inr,
            'available_balance': available_inr,
            'locked_balance': locked_inr,
            'available_margin': available_inr,
            'used_margin': locked_inr,
            'last_updated': datetime.now()
        }
    
    def fetch_open_positions(self) -> Optional[List[Dict]]:
        timestamp = int(time.time() * 1000)
        payload = {
            'timestamp': timestamp
        }
        
        result = self._make_authenticated_request('/exchange/v1/orders/active_orders', payload)
        
        if result:
            self.open_positions = self._parse_positions(result)
            return self.open_positions
        
        return None
    
    def _parse_positions(self, orders_data: List[Dict]) -> List[Dict]:
        positions = []
        
        for order in orders_data:
            position = {
                'symbol': order.get('market', '').replace('INR', ''),
                'side': order.get('side', ''),
                'entry_price': float(order.get('price', 0)),
                'quantity': float(order.get('total_quantity', 0)),
                'filled_quantity': float(order.get('filled_quantity', 0)),
                'order_id': order.get('id', ''),
                'status': order.get('status', '')
            }
            positions.append(position)
        
        return positions
    
    def get_available_margin(self) -> float:
        if not self.account_balance:
            self.fetch_account_balance()
        
        return self.account_balance.get('available_margin', 0)
    
    def get_used_margin(self) -> float:
        if not self.account_balance:
            self.fetch_account_balance()
        
        return self.account_balance.get('used_margin', 0)
    
    def calculate_dynamic_position_size(self, entry_price: float, stop_loss: float, 
                                       base_position_size: float) -> float:
        available_margin = self.get_available_margin()
        max_margin_percent = self.config['personalized']['max_margin_per_trade_percent']
        
        max_position_from_margin = available_margin * (max_margin_percent / 100)
        
        adjusted_size = min(base_position_size, max_position_from_margin)
        
        return round(adjusted_size, 2)
    
    def can_open_position(self, position_size: float) -> tuple[bool, str]:
        available_margin = self.get_available_margin()
        
        if position_size > available_margin:
            return False, f"Insufficient margin. Required: ₹{position_size}, Available: ₹{available_margin}"
        
        max_positions = self.config['risk']['max_concurrent_positions']
        if len(self.open_positions) >= max_positions:
            return False, f"Max concurrent positions reached ({max_positions})"
        
        return True, "OK"
    
    def calculate_position_pnl(self, position: Dict, current_price: float) -> Dict:
        entry_price = position['entry_price']
        quantity = position['filled_quantity']
        side = position['side']
        
        if side.upper() == 'BUY':
            pnl = (current_price - entry_price) * quantity
            pnl_percent = ((current_price - entry_price) / entry_price) * 100
        else:
            pnl = (entry_price - current_price) * quantity
            pnl_percent = ((entry_price - current_price) / entry_price) * 100
        
        return {
            'pnl_amount': round(pnl, 2),
            'pnl_percent': round(pnl_percent, 2)
        }
    
    def get_account_summary(self) -> Dict:
        total_pnl = 0
        positions_summary = []
        
        for position in self.open_positions:
            positions_summary.append({
                'symbol': position['symbol'],
                'side': position['side'],
                'quantity': position['filled_quantity']
            })
        
        return {
            'total_balance': self.account_balance.get('total_balance', 0),
            'available_margin': self.account_balance.get('available_margin', 0),
            'used_margin': self.account_balance.get('used_margin', 0),
            'open_positions_count': len(self.open_positions),
            'positions': positions_summary,
            'total_pnl': total_pnl
        }
    
    def refresh_account_data(self):
        self.fetch_account_balance()
        self.fetch_open_positions()
        logger.info("Account data refreshed")

