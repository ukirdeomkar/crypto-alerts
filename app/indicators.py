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
        
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])
        
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    def calculate_atr(self, highs: List[float], lows: List[float], closes: List[float], 
                      period: Optional[int] = None) -> Optional[float]:
        if period is None:
            period = self.config.get('atr_period', 14)
        
        if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
            return None
        
        high_arr = np.array(highs)
        low_arr = np.array(lows)
        close_arr = np.array(closes)
        
        tr1 = high_arr[1:] - low_arr[1:]
        tr2 = np.abs(high_arr[1:] - close_arr[:-1])
        tr3 = np.abs(low_arr[1:] - close_arr[:-1])
        
        true_range = np.maximum(tr1, np.maximum(tr2, tr3))
        
        atr = np.mean(true_range[:period])
        
        for i in range(period, len(true_range)):
            atr = (atr * (period - 1) + true_range[i]) / period
        
        return float(atr)
    
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
        
        prev_histogram = macd_line[-2] - signal_line[-2] if len(macd_line) > 1 else 0
        
        return {
            'macd': float(macd_line[-1]),
            'signal': float(signal_line[-1]),
            'histogram': float(histogram),
            'prev_histogram': float(prev_histogram),
            'bullish_crossover': histogram > 0 and prev_histogram < 0,
            'bearish_crossover': histogram < 0 and prev_histogram > 0
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
            'bandwidth': float((upper_band - lower_band) / sma * 100) if sma > 0 else 0
        }
    
    def calculate_trend_emas(self, prices: List[float]) -> Optional[Dict[str, any]]:
        fast_period = self.config.get('trend_ema_fast', 20)
        slow_period = self.config.get('trend_ema_slow', 50)
        
        if len(prices) < slow_period:
            return None
        
        prices_array = np.array(prices)
        ema_fast = self._calculate_ema(prices_array, fast_period)
        ema_slow = self._calculate_ema(prices_array, slow_period)
        
        current_fast = ema_fast[-1]
        current_slow = ema_slow[-1]
        prev_fast = ema_fast[-2] if len(ema_fast) > 1 else current_fast
        prev_slow = ema_slow[-2] if len(ema_slow) > 1 else current_slow
        
        bullish_trend = current_fast > current_slow
        bearish_trend = current_fast < current_slow
        
        bullish_crossover = current_fast > current_slow and prev_fast <= prev_slow
        bearish_crossover = current_fast < current_slow and prev_fast >= prev_slow
        
        trend_strength = abs(current_fast - current_slow) / current_slow * 100 if current_slow > 0 else 0
        
        return {
            'ema_fast': float(current_fast),
            'ema_slow': float(current_slow),
            'bullish_trend': bullish_trend,
            'bearish_trend': bearish_trend,
            'bullish_crossover': bullish_crossover,
            'bearish_crossover': bearish_crossover,
            'trend_strength': float(trend_strength),
            'trend': 'bullish' if bullish_trend else 'bearish'
        }
    
    def detect_divergence(self, prices: List[float], indicator_values: List[float], 
                         lookback: int = 10) -> Dict[str, bool]:
        if len(prices) < lookback or len(indicator_values) < lookback:
            return {
                'bullish_divergence': False,
                'bearish_divergence': False,
                'divergence_strength': 0
            }
        
        recent_prices = np.array(prices[-lookback:])
        recent_indicators = np.array(indicator_values[-lookback:])
        
        price_lows = []
        price_highs = []
        indicator_lows = []
        indicator_highs = []
        
        for i in range(1, len(recent_prices) - 1):
            if recent_prices[i] < recent_prices[i-1] and recent_prices[i] < recent_prices[i+1]:
                price_lows.append((i, recent_prices[i]))
                indicator_lows.append((i, recent_indicators[i]))
            
            if recent_prices[i] > recent_prices[i-1] and recent_prices[i] > recent_prices[i+1]:
                price_highs.append((i, recent_prices[i]))
                indicator_highs.append((i, recent_indicators[i]))
        
        bullish_div = False
        bearish_div = False
        strength = 0
        
        if len(price_lows) >= 2 and len(indicator_lows) >= 2:
            last_two_price_lows = sorted(price_lows, key=lambda x: x[0])[-2:]
            last_two_ind_lows = sorted(indicator_lows, key=lambda x: x[0])[-2:]
            
            if last_two_price_lows[1][1] < last_two_price_lows[0][1]:
                if last_two_ind_lows[1][1] > last_two_ind_lows[0][1]:
                    bullish_div = True
                    strength = 25
        
        if len(price_highs) >= 2 and len(indicator_highs) >= 2:
            last_two_price_highs = sorted(price_highs, key=lambda x: x[0])[-2:]
            last_two_ind_highs = sorted(indicator_highs, key=lambda x: x[0])[-2:]
            
            if last_two_price_highs[1][1] > last_two_price_highs[0][1]:
                if last_two_ind_highs[1][1] < last_two_ind_highs[0][1]:
                    bearish_div = True
                    strength = 25
        
        return {
            'bullish_divergence': bullish_div,
            'bearish_divergence': bearish_div,
            'divergence_strength': float(strength)
        }
    
    def calculate_obv(self, prices: List[float], volumes: List[float]) -> Optional[float]:
        if len(prices) < 2 or len(volumes) < 2:
            return None
        
        obv = 0
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                obv += volumes[i]
            elif prices[i] < prices[i-1]:
                obv -= volumes[i]
        
        return float(obv)
    
    def detect_volume_surge(self, current_volume: float, volume_history: List[float]) -> Dict[str, any]:
        multiplier = self.config['volume_surge_multiplier']
        
        if len(volume_history) < 10:
            return {
                'is_surge': False,
                'multiplier': 1.0,
                'average': current_volume,
                'relative_volume': 1.0,
                'volume_trend': 'neutral'
            }
        
        avg_volume = np.mean(volume_history[:-1])
        recent_avg = np.mean(volume_history[-5:-1]) if len(volume_history) >= 5 else avg_volume
        
        if avg_volume == 0:
            return {
                'is_surge': False,
                'multiplier': 1.0,
                'average': 0,
                'relative_volume': 1.0,
                'volume_trend': 'neutral'
            }
        
        volume_multiplier = current_volume / avg_volume
        relative_volume = current_volume / recent_avg if recent_avg > 0 else 1.0
        is_surge = volume_multiplier >= multiplier
        
        volume_trend = 'increasing' if recent_avg > avg_volume * 1.2 else 'decreasing' if recent_avg < avg_volume * 0.8 else 'neutral'
        
        return {
            'is_surge': is_surge,
            'multiplier': float(volume_multiplier),
            'average': float(avg_volume),
            'relative_volume': float(relative_volume),
            'volume_trend': volume_trend
        }
    
    def detect_support_resistance(self, prices: List[float], threshold: float = 0.02) -> Dict[str, any]:
        if len(prices) < 20:
            return {
                'support_levels': [],
                'resistance_levels': [],
                'near_support': False,
                'near_resistance': False
            }
        
        prices_array = np.array(prices)
        current_price = prices[-1]
        
        local_maxima = []
        local_minima = []
        
        for i in range(2, len(prices) - 2):
            if prices[i] > prices[i-1] and prices[i] > prices[i-2] and prices[i] > prices[i+1] and prices[i] > prices[i+2]:
                local_maxima.append(prices[i])
            if prices[i] < prices[i-1] and prices[i] < prices[i-2] and prices[i] < prices[i+1] and prices[i] < prices[i+2]:
                local_minima.append(prices[i])
        
        resistance_levels = self._cluster_levels(local_maxima, threshold) if local_maxima else []
        support_levels = self._cluster_levels(local_minima, threshold) if local_minima else []
        
        near_support = any(abs(current_price - level) / level < threshold for level in support_levels)
        near_resistance = any(abs(current_price - level) / level < threshold for level in resistance_levels)
        
        return {
            'support_levels': [float(l) for l in support_levels],
            'resistance_levels': [float(l) for l in resistance_levels],
            'near_support': near_support,
            'near_resistance': near_resistance,
            'distance_to_nearest_support': self._nearest_level_distance(current_price, support_levels),
            'distance_to_nearest_resistance': self._nearest_level_distance(current_price, resistance_levels)
        }
    
    def _cluster_levels(self, levels: List[float], threshold: float) -> List[float]:
        if not levels:
            return []
        
        sorted_levels = sorted(levels)
        clustered = []
        current_cluster = [sorted_levels[0]]
        
        for level in sorted_levels[1:]:
            if abs(level - current_cluster[-1]) / current_cluster[-1] < threshold:
                current_cluster.append(level)
            else:
                clustered.append(np.mean(current_cluster))
                current_cluster = [level]
        
        if current_cluster:
            clustered.append(np.mean(current_cluster))
        
        return clustered
    
    def _nearest_level_distance(self, price: float, levels: List[float]) -> Optional[float]:
        if not levels:
            return None
        
        distances = [abs(price - level) / price for level in levels]
        return float(min(distances)) if distances else None
    
    def detect_price_momentum(self, prices: List[float]) -> Dict[str, any]:
        if len(prices) < 5:
            return {
                'trend': 'neutral',
                'strength': 0,
                'change_percent': 0,
                'momentum_score': 0
            }
        
        recent_prices = prices[-5:]
        price_changes = [recent_prices[i] - recent_prices[i-1] for i in range(1, len(recent_prices))]
        
        positive_changes = sum(1 for change in price_changes if change > 0)
        negative_changes = sum(1 for change in price_changes if change < 0)
        
        total_change = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        
        momentum_score = (positive_changes - negative_changes) / len(price_changes) * 100
        
        if positive_changes >= 3:
            trend = 'bullish'
        elif negative_changes >= 3:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'trend': trend,
            'strength': abs(total_change),
            'change_percent': total_change,
            'momentum_score': momentum_score
        }
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(prices))
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def analyze_coin(self, prices: List[float], highs: List[float], lows: List[float],
                    current_volume: float, volume_history: List[float]) -> Dict[str, any]:
        rsi = self.calculate_rsi(prices)
        atr = self.calculate_atr(highs, lows, prices)
        macd = self.calculate_macd(prices)
        bb = self.calculate_bollinger_bands(prices)
        trend = self.calculate_trend_emas(prices)
        volume = self.detect_volume_surge(current_volume, volume_history)
        momentum = self.detect_price_momentum(prices)
        support_resistance = self.detect_support_resistance(prices)
        obv = self.calculate_obv(prices, volume_history)
        
        rsi_values = []
        if len(prices) >= self.config.get('rsi_period', 14):
            for i in range(max(5, self.config.get('rsi_period', 14)), len(prices) + 1):
                rsi_val = self.calculate_rsi(prices[:i])
                if rsi_val is not None:
                    rsi_values.append(rsi_val)
        
        rsi_divergence = self.detect_divergence(prices[-10:], rsi_values[-10:]) if len(rsi_values) >= 10 else {
            'bullish_divergence': False,
            'bearish_divergence': False,
            'divergence_strength': 0
        }
        
        return {
            'rsi': rsi,
            'atr': atr,
            'macd': macd,
            'bollinger_bands': bb,
            'trend': trend,
            'volume': volume,
            'momentum': momentum,
            'support_resistance': support_resistance,
            'obv': obv,
            'rsi_divergence': rsi_divergence,
            'has_data': all([
                rsi is not None, 
                macd is not None, 
                bb is not None,
                atr is not None
                # Trend is optional - will activate after 50 periods
            ])
        }
