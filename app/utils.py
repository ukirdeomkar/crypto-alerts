import os
import logging
from pathlib import Path
from datetime import datetime
import pytz
import yaml

def load_config():
    config_path = Path("config/config.yaml")
    if not config_path.exists():
        config_path = Path("config.yaml")
        if not config_path.exists():
            raise FileNotFoundError("config.yaml not found in config/ or root directory")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_env_var(var_name, required=True, default=None):
    value = os.getenv(var_name, default)
    if required and not value:
        raise ValueError(f"Environment variable {var_name} is required but not set")
    return value

def setup_logging(config):
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', 'logs/trading.log')
    
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def load_futures_coins(coins_file):
    coins_path = Path(coins_file)
    if not coins_path.exists():
        raise FileNotFoundError(f"Coins file not found: {coins_file}")
    
    with open(coins_path, 'r') as f:
        coins = [line.strip() for line in f if line.strip()]
    
    return coins

def get_ist_time():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)

def format_inr(amount):
    if amount >= 10000000:
        return f"₹{amount/10000000:.2f}Cr"
    elif amount >= 100000:
        return f"₹{amount/100000:.2f}L"
    elif amount >= 1000:
        return f"₹{amount/1000:.2f}K"
    else:
        return f"₹{amount:.2f}"

def format_price(price):
    price_str = f"{price:.8f}".rstrip('0').rstrip('.')
    return f"₹{price_str}"

def format_percentage(value):
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"

def calculate_position_size(capital, risk_percent, stop_loss_percent, leverage):
    risk_amount = capital * (risk_percent / 100)
    position_size = (risk_amount / (stop_loss_percent / 100)) / leverage
    return position_size

def calculate_targets(entry_price, targets_config, direction="LONG"):
    targets = []
    for target_config in targets_config:
        target_percent = target_config['target']
        exit_percent = target_config['exit_percent']
        
        if direction == "LONG":
            target_price = entry_price * (1 + target_percent / 100)
        else:
            target_price = entry_price * (1 - target_percent / 100)
        
        targets.append({
            'price': target_price,
            'exit_percent': exit_percent,
            'profit_percent': target_percent
        })
    
    return targets

def calculate_stop_loss(entry_price, stop_loss_percent, direction="LONG"):
    if direction == "LONG":
        return entry_price * (1 - stop_loss_percent / 100)
    else:
        return entry_price * (1 + stop_loss_percent / 100)

def calculate_profit_loss(entry_price, current_price, position_size, leverage, direction="LONG"):
    if direction == "LONG":
        pnl_percent = ((current_price - entry_price) / entry_price) * 100
    else:
        pnl_percent = ((entry_price - current_price) / entry_price) * 100
    
    pnl_amount = position_size * leverage * (pnl_percent / 100)
    return pnl_amount, pnl_percent

def validate_signal(signal, config):
    risk_config = config.get('risk', {})
    
    stop_loss_distance = abs(signal['entry_price'] - signal['stop_loss']) / signal['entry_price'] * 100
    
    blended_target = 0
    for target in signal['targets']:
        target_distance = abs(target['price'] - signal['entry_price']) / signal['entry_price'] * 100
        blended_target += target_distance * (target['exit_percent'] / 100)
    
    risk_reward = blended_target / stop_loss_distance if stop_loss_distance > 0 else 0
    
    if risk_reward < risk_config['min_risk_reward_ratio']:
        return False, f"Risk:Reward {risk_reward:.2f} below minimum {risk_config['min_risk_reward_ratio']}"
    
    return True, "Valid"

def get_current_trading_period(config):
    ist_time = get_ist_time()
    trading_hours = config.get('trading_hours', {})
    
    current_day = ist_time.strftime('%A').lower()
    if current_day not in trading_hours.get('days', []):
        return None, None
    
    periods = trading_hours.get('periods')
    if not periods:
        signals_config = config.get('signals', {})
        fallback_period = {
            'name': 'default',
            'start_time': trading_hours.get('start_time', '07:30'),
            'end_time': trading_hours.get('end_time', '17:00'),
            'min_confidence': signals_config.get('min_confidence', 60),
            'max_alerts_per_scan': signals_config.get('max_alerts_per_scan', 3)
        }
        periods = [fallback_period]
    
    current_time = ist_time.time()
    
    for period in periods:
        start_time = datetime.strptime(period['start_time'], '%H:%M').time()
        end_time = datetime.strptime(period['end_time'], '%H:%M').time()
        
        is_in_period = False
        if start_time <= end_time:
            is_in_period = start_time <= current_time <= end_time
        else:
            is_in_period = current_time >= start_time or current_time <= end_time
        
        if is_in_period:
            return True, period
    
    return False, None

def is_trading_hours(config):
    is_trading, _ = get_current_trading_period(config)
    return is_trading

