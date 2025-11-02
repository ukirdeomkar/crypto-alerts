import logging
from typing import Dict, Optional
from app.utils import calculate_position_size

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.risk_config = config['risk']
        self.total_capital = self.risk_config['total_capital']
        self.risk_per_trade = self.risk_config['risk_per_trade_percent']
        self.max_leverage = self.risk_config['max_leverage']
        self.default_leverage = self.risk_config['default_leverage']
        self.transaction_cost = self.risk_config.get('transaction_cost_percent', 0)
        
        self.active_positions = []
        
    def calculate_position_size(self, entry_price: float, stop_loss: float, 
                                leverage: Optional[int] = None) -> float:
        if leverage is None:
            leverage = self.default_leverage
        
        stop_loss_distance = abs(entry_price - stop_loss) / entry_price * 100
        
        position_size = calculate_position_size(
            self.total_capital,
            self.risk_per_trade,
            stop_loss_distance,
            leverage
        )
        
        max_position = self.total_capital * 0.2
        position_size = min(position_size, max_position)
        
        return round(position_size, 2)
    
    def can_open_position(self) -> tuple[bool, str]:
        max_positions = self.risk_config['max_concurrent_positions']
        
        if len(self.active_positions) >= max_positions:
            return False, f"Max concurrent positions reached ({max_positions})"
        
        return True, "OK"
    
    def validate_leverage(self, leverage: int) -> tuple[bool, str]:
        if leverage > self.max_leverage:
            return False, f"Leverage {leverage}x exceeds maximum {self.max_leverage}x"
        
        if leverage < 1:
            return False, "Leverage must be at least 1x"
        
        return True, "OK"
    
    def calculate_max_loss(self, position_size: float, leverage: int, 
                          stop_loss_percent: float) -> float:
        exposure = position_size * leverage
        max_loss = exposure * (stop_loss_percent / 100)
        transaction_fees = position_size * (self.transaction_cost / 100)
        total_loss = max_loss + transaction_fees
        return round(total_loss, 2)
    
    def calculate_potential_profit(self, position_size: float, leverage: int, 
                                   target_percent: float) -> float:
        exposure = position_size * leverage
        gross_profit = exposure * (target_percent / 100)
        transaction_fees = position_size * (self.transaction_cost / 100)
        net_profit = gross_profit - transaction_fees
        return round(net_profit, 2)
    
    def calculate_breakeven_percent(self) -> float:
        return self.transaction_cost
    
    def calculate_net_profit(self, position_size: float, leverage: int, 
                           entry_price: float, exit_price: float) -> float:
        exposure = position_size * leverage
        price_change_percent = ((exit_price - entry_price) / entry_price) * 100
        gross_profit = exposure * (price_change_percent / 100)
        transaction_fees = position_size * (self.transaction_cost / 100)
        net_profit = gross_profit - transaction_fees
        return round(net_profit, 2)
    
    def add_position(self, signal: Dict):
        position = {
            'symbol': signal['symbol'],
            'direction': signal['direction'],
            'entry_price': signal['entry_price'],
            'position_size': signal['position_size'],
            'leverage': signal['leverage'],
            'stop_loss': signal['stop_loss'],
            'targets': signal['targets'],
            'entry_time': signal['timestamp']
        }
        self.active_positions.append(position)
        logger.info(f"Position added: {signal['symbol']} {signal['direction']} at ₹{signal['entry_price']}")
    
    def remove_position(self, symbol: str):
        self.active_positions = [p for p in self.active_positions if p['symbol'] != symbol]
        logger.info(f"Position removed: {symbol}")
    
    def get_active_positions(self) -> list:
        return self.active_positions.copy()
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        for position in self.active_positions:
            if position['symbol'] == symbol:
                return position
        return None
    
    def cleanup_expired_positions(self, max_age_minutes: int = 5):
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        initial_count = len(self.active_positions)
        
        self.active_positions = [
            p for p in self.active_positions 
            if p['entry_time'] > cutoff_time
        ]
        
        removed = initial_count - len(self.active_positions)
        if removed > 0:
            logger.info(f"Auto-cleanup: Removed {removed} expired positions (>{max_age_minutes} min old)")
        
        return removed
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, 
                                    target_price: float, direction: str = "LONG") -> float:
        if direction == "LONG":
            risk = entry_price - stop_loss
            reward = target_price - entry_price
        else:
            risk = stop_loss - entry_price
            reward = entry_price - target_price
        
        if risk <= 0:
            return 0
        
        return reward / risk

