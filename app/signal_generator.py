import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from app.utils import calculate_targets, calculate_stop_loss, validate_signal

logger = logging.getLogger(__name__)

class SignalGenerator:
    def __init__(self, config, indicators, risk_manager):
        self.config = config
        self.indicators = indicators
        self.risk_manager = risk_manager
        self.last_alert_time = defaultdict(lambda: {'LONG': datetime.min, 'SHORT': datetime.min})
        self.cooldown_minutes = config['signals']['cooldown_minutes']
        
    def generate_signal(self, coin_symbol: str, price_data: Dict, analysis: Dict, min_confidence: int = None) -> Optional[Dict]:
        if not analysis.get('has_data'):
            logger.debug(f"{coin_symbol}: Insufficient data for analysis")
            return None
        
        direction, confidence, reasons = self._evaluate_signal(analysis)
        
        if direction == "NEUTRAL":
            return None
        
        if not self._can_send_alert(coin_symbol, direction):
            logger.debug(f"{coin_symbol}: {direction} signal in cooldown period")
            return None
        
        confidence_threshold = min_confidence if min_confidence is not None else self.config['signals']['min_confidence']
        if confidence < confidence_threshold:
            logger.debug(f"{coin_symbol}: Confidence {confidence}% below threshold {confidence_threshold}%")
            return None
        
        entry_price = price_data['price']
        stop_loss = calculate_stop_loss(
            entry_price, 
            self.config['risk']['stop_loss_percent'],
            direction
        )
        
        targets = calculate_targets(
            entry_price,
            self.config['risk']['take_profit_targets'],
            direction
        )
        
        position_size = self.risk_manager.calculate_position_size(entry_price, stop_loss, confidence=confidence)
        leverage = self.config['risk']['default_leverage']
        
        signal = {
            'symbol': coin_symbol,
            'market': price_data['market'],
            'direction': direction,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'targets': targets,
            'position_size': position_size,
            'leverage': leverage,
            'confidence': confidence,
            'reasons': reasons,
            'timestamp': datetime.now(),
            'price_data': price_data,
            'analysis': analysis
        }
        
        momentum = analysis.get('momentum', {})
        recent_change = abs(momentum.get('change_percent', 0))
        target_distance = targets[1]['profit_percent'] if len(targets) > 1 else targets[0]['profit_percent']
        
        if recent_change > 0:
            estimated_minutes = (target_distance / recent_change) * 2
            max_hold = self.config['risk'].get('position_expiry_minutes', 5)
            
            if estimated_minutes > max_hold * 1.5:
                logger.debug(f"{coin_symbol}: Too slow - needs {estimated_minutes:.1f} min but strategy max is {max_hold} min")
                return None
        
        is_valid, reason = validate_signal(signal, self.config)
        if not is_valid:
            logger.debug(f"Signal rejected for {coin_symbol}: {reason}")
            return None
        
        self.last_alert_time[coin_symbol][direction] = datetime.now()
        
        return signal
    
    def _evaluate_signal(self, analysis: Dict) -> tuple[str, float, List[str]]:
        rsi = analysis['rsi']
        macd = analysis['macd']
        bb = analysis['bollinger_bands']
        volume = analysis['volume']
        momentum = analysis['momentum']
        
        buy_signals = []
        sell_signals = []
        confidence_factors = []
        
        rsi_oversold = self.config['signals']['indicators']['rsi_oversold']
        rsi_overbought = self.config['signals']['indicators']['rsi_overbought']
        
        if rsi is not None:
            if rsi < rsi_oversold:
                buy_signals.append(f"RSI({rsi:.1f}) Oversold")
                confidence_factors.append(25)
            elif rsi > rsi_overbought:
                sell_signals.append(f"RSI({rsi:.1f}) Overbought")
                confidence_factors.append(25)
        
        if macd:
            if macd['bullish_crossover']:
                buy_signals.append("MACD Bullish Crossover")
                confidence_factors.append(20)
            elif macd['bearish_crossover']:
                sell_signals.append("MACD Bearish Crossover")
                confidence_factors.append(20)
            elif macd['histogram'] > 0:
                buy_signals.append("MACD Positive")
                confidence_factors.append(10)
            elif macd['histogram'] < 0:
                sell_signals.append("MACD Negative")
                confidence_factors.append(10)
        
        if bb:
            if bb['at_lower']:
                buy_signals.append("BB Lower Band Bounce")
                confidence_factors.append(15)
            elif bb['at_upper']:
                sell_signals.append("BB Upper Band Rejection")
                confidence_factors.append(15)
        
        if volume['is_surge']:
            multiplier = volume['multiplier']
            confidence_factors.append(min(30, multiplier * 10))
        
        if momentum['trend'] == 'bullish' and momentum['strength'] > 0.5:
            buy_signals.append(f"Bullish Momentum ({momentum['change_percent']:.2f}%)")
            confidence_factors.append(15)
        elif momentum['trend'] == 'bearish' and momentum['strength'] > 0.5:
            sell_signals.append(f"Bearish Momentum ({momentum['change_percent']:.2f}%)")
            confidence_factors.append(15)
        
        if volume['is_surge']:
            surge_msg = f"Volume Surge ({volume['multiplier']:.1f}x)"
            if len(buy_signals) > len(sell_signals):
                buy_signals.append(surge_msg)
            elif len(sell_signals) > len(buy_signals):
                sell_signals.append(surge_msg)
        
        if len(buy_signals) > len(sell_signals) and len(buy_signals) >= 2:
            direction = "LONG"
            reasons = buy_signals
            confidence = min(100, sum(confidence_factors[:len(buy_signals)]))
        elif len(sell_signals) > len(buy_signals) and len(sell_signals) >= 2:
            direction = "SHORT"
            reasons = sell_signals
            confidence = min(100, sum(confidence_factors[:len(sell_signals)]))
        else:
            return "NEUTRAL", 0, []
        
        return direction, confidence, reasons
    
    def _can_send_alert(self, coin_symbol: str, direction: str) -> bool:
        last_alert = self.last_alert_time[coin_symbol][direction]
        cooldown = timedelta(minutes=self.cooldown_minutes)
        return datetime.now() - last_alert >= cooldown
    
    def rank_signals(self, signals: List[Dict]) -> List[Dict]:
        return sorted(signals, key=lambda s: s['confidence'], reverse=True)
    
    def filter_top_signals(self, signals: List[Dict], max_alerts: int = None) -> List[Dict]:
        max_alerts_limit = max_alerts if max_alerts is not None else self.config['signals']['max_alerts_per_scan']
        ranked = self.rank_signals(signals)
        return ranked[:max_alerts_limit]

