import numpy as np
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    def __init__(self, config):
        self.config = config['signals']['indicators']
        
    def calculate_rsi(self, prices: List[float], period: Optional[int] = None) -> Optional[float]:
        if period is None:
            period = self.config['rsi_period']
        
        if len(prices) < period + 1:
            return None
        
        prices_array = np.array(prices)
        deltas = np.diff(prices_array)
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    def calculate_macd(self, prices: List[float]) -> Optional[Dict[str, float]]:
        fast = self.config['macd_fast']
        slow = self.config['macd_slow']
        signal = self.config['macd_signal']
        
        if len(prices) < slow + signal:
            return None
        
        prices_array = np.array(prices)
        
        ema_fast = self._calculate_ema(prices_array, fast)
        ema_slow = self._calculate_ema(prices_array, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema(macd_line, signal)
        histogram = macd_line[-1] - signal_line[-1]
        
        return {
            'macd': float(macd_line[-1]),
            'signal': float(signal_line[-1]),
            'histogram': float(histogram),
            'bullish_crossover': histogram > 0 and len(macd_line) > 1 and (macd_line[-2] - signal_line[-2]) < 0,
            'bearish_crossover': histogram < 0 and len(macd_line) > 1 and (macd_line[-2] - signal_line[-2]) > 0
        }
    
    def calculate_bollinger_bands(self, prices: List[float]) -> Optional[Dict[str, float]]:
        period = self.config['bb_period']
        std_dev = self.config['bb_std']
        
        if len(prices) < period:
            return None
        
        prices_array = np.array(prices[-period:])
        sma = np.mean(prices_array)
        std = np.std(prices_array)
        
        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)
        current_price = prices[-1]
        
        bb_position = (current_price - lower_band) / (upper_band - lower_band) if upper_band != lower_band else 0.5
        
        return {
            'upper': float(upper_band),
            'middle': float(sma),
            'lower': float(lower_band),
            'current': float(current_price),
            'position': float(bb_position),
            'at_lower': bb_position < 0.2,
            'at_upper': bb_position > 0.8,
            'bandwidth': float((upper_band - lower_band) / sma * 100)
        }
    
    def detect_volume_surge(self, current_volume: float, volume_history: List[float]) -> Dict[str, any]:
        multiplier = self.config['volume_surge_multiplier']
        
        if len(volume_history) < 5:
            return {
                'is_surge': False,
                'multiplier': 1.0,
                'average': current_volume
            }
        
        avg_volume = np.mean(volume_history[:-1])
        
        if avg_volume == 0:
            return {
                'is_surge': False,
                'multiplier': 1.0,
                'average': 0
            }
        
        volume_multiplier = current_volume / avg_volume
        is_surge = volume_multiplier >= multiplier
        
        return {
            'is_surge': is_surge,
            'multiplier': float(volume_multiplier),
            'average': float(avg_volume)
        }
    
    def detect_price_momentum(self, prices: List[float]) -> Dict[str, any]:
        if len(prices) < 5:
            return {
                'trend': 'neutral',
                'strength': 0
            }
        
        recent_prices = prices[-5:]
        price_changes = [recent_prices[i] - recent_prices[i-1] for i in range(1, len(recent_prices))]
        
        positive_changes = sum(1 for change in price_changes if change > 0)
        negative_changes = sum(1 for change in price_changes if change < 0)
        
        total_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        
        if positive_changes >= 3:
            trend = 'bullish'
        elif negative_changes >= 3:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'trend': trend,
            'strength': abs(total_change),
            'change_percent': total_change
        }
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(prices))
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def analyze_coin(self, prices: List[float], current_volume: float, volume_history: List[float]) -> Dict[str, any]:
        rsi = self.calculate_rsi(prices)
        macd = self.calculate_macd(prices)
        bb = self.calculate_bollinger_bands(prices)
        volume = self.detect_volume_surge(current_volume, volume_history)
        momentum = self.detect_price_momentum(prices)
        
        return {
            'rsi': rsi,
            'macd': macd,
            'bollinger_bands': bb,
            'volume': volume,
            'momentum': momentum,
            'has_data': all([rsi is not None, macd is not None, bb is not None])
        }

