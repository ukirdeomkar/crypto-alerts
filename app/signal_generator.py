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
        
        self.indicator_weights = config['signals'].get('indicator_weights', {
            'rsi': 1.0,
            'macd': 1.2,
            'trend': 1.5,
            'volume': 1.0,
            'momentum': 0.8,
            'divergence': 1.3,
            'support_resistance': 1.1
        })
        
    def generate_signal(self, coin_symbol: str, price_data: Dict, analysis: Dict, min_confidence: int = None) -> Optional[Dict]:
        if not analysis.get('has_data'):
            logger.debug(f"{coin_symbol}: Insufficient data for analysis")
            return None
        
        direction, confidence, reasons, signal_details = self._evaluate_signal_advanced(analysis, price_data)
        
        if direction == "NEUTRAL":
            return None
        
        if not self._can_send_alert(coin_symbol, direction):
            logger.debug(f"{coin_symbol}: {direction} signal in cooldown period")
            return None
        
        confidence_threshold = min_confidence if min_confidence is not None else self.config['signals']['min_confidence']
        if confidence < confidence_threshold:
            if not hasattr(self, '_confidence_rejection_count'):
                self._confidence_rejection_count = 0
            if self._confidence_rejection_count < 5:
                logger.info(f"   ⚠️  {coin_symbol}: Confidence {confidence:.1f}% < threshold {confidence_threshold}%")
                self._confidence_rejection_count += 1
            return None
        
        entry_price = price_data['price']
        
        use_atr_stops = self.config['risk'].get('use_atr_stops', False)
        if use_atr_stops and analysis.get('atr'):
            atr = analysis['atr']
            atr_multiplier = self.config['risk'].get('atr_stop_multiplier', 2.0)
            stop_distance = (atr * atr_multiplier) / entry_price * 100
            stop_loss = calculate_stop_loss(entry_price, stop_distance, direction)
            
            # Debug ATR vs fixed stops (first 3 only)
            if not hasattr(self, '_atr_debug_count'):
                self._atr_debug_count = 0
            if self._atr_debug_count < 3:
                fixed_stop = self.config['risk']['stop_loss_percent']
                logger.info(f"   📏 {coin_symbol}: ATR stop={stop_distance:.2f}% (vs fixed {fixed_stop}%)")
                self._atr_debug_count += 1
        else:
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
            'signal_details': signal_details,
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
            if not hasattr(self, '_validation_rejection_count'):
                self._validation_rejection_count = 0
            if self._validation_rejection_count < 5:
                logger.info(f"   ❌ {coin_symbol}: REJECTED - {reason}")
                self._validation_rejection_count += 1
            return None
        
        self.last_alert_time[coin_symbol][direction] = datetime.now()
        
        return signal
    
    def _evaluate_signal_advanced(self, analysis: Dict, price_data: Dict) -> tuple[str, float, List[str], Dict]:
        rsi = analysis.get('rsi')
        macd = analysis.get('macd')
        bb = analysis.get('bollinger_bands')
        trend = analysis.get('trend')
        volume = analysis.get('volume')
        momentum = analysis.get('momentum')
        support_resistance = analysis.get('support_resistance', {})
        rsi_divergence = analysis.get('rsi_divergence', {})
        
        buy_signals = []
        sell_signals = []
        weighted_buy_confidence = []
        weighted_sell_confidence = []
        
        signal_details = {
            'rsi_value': rsi,
            'macd_histogram': macd.get('histogram') if macd else None,
            'trend_direction': trend.get('trend') if trend else None,
            'volume_multiplier': volume.get('multiplier'),
            'divergence_detected': False
        }
        
        rsi_oversold = self.config['signals']['indicators']['rsi_oversold']
        rsi_overbought = self.config['signals']['indicators']['rsi_overbought']
        
        if rsi is not None:
            if rsi < rsi_oversold:
                strength = (rsi_oversold - rsi) / rsi_oversold * 25
                buy_signals.append(f"RSI({rsi:.1f}) Oversold")
                weighted_buy_confidence.append(strength * self.indicator_weights['rsi'])
            elif rsi > rsi_overbought:
                strength = (rsi - rsi_overbought) / (100 - rsi_overbought) * 25
                sell_signals.append(f"RSI({rsi:.1f}) Overbought")
                weighted_sell_confidence.append(strength * self.indicator_weights['rsi'])
        
        if macd:
            if macd['bullish_crossover']:
                buy_signals.append("MACD Bullish Crossover")
                weighted_buy_confidence.append(25 * self.indicator_weights['macd'])
            elif macd['bearish_crossover']:
                sell_signals.append("MACD Bearish Crossover")
                weighted_sell_confidence.append(25 * self.indicator_weights['macd'])
            elif macd['histogram'] > 0:
                histogram_strength = min(15, abs(macd['histogram']) * 10)
                buy_signals.append("MACD Positive")
                weighted_buy_confidence.append(histogram_strength * self.indicator_weights['macd'])
            elif macd['histogram'] < 0:
                histogram_strength = min(15, abs(macd['histogram']) * 10)
                sell_signals.append("MACD Negative")
                weighted_sell_confidence.append(histogram_strength * self.indicator_weights['macd'])
        
        if trend:
            if trend.get('bullish_trend'):
                trend_str = trend.get('trend_strength', 0)
                strength = min(25, trend_str * 2)
                buy_signals.append(f"Bullish Trend (EMA)")
                weighted_buy_confidence.append(strength * self.indicator_weights['trend'])
            elif trend.get('bearish_trend'):
                trend_str = trend.get('trend_strength', 0)
                strength = min(25, trend_str * 2)
                sell_signals.append(f"Bearish Trend (EMA)")
                weighted_sell_confidence.append(strength * self.indicator_weights['trend'])
            
            if trend.get('bullish_crossover'):
                buy_signals.append("EMA Bullish Crossover")
                weighted_buy_confidence.append(30 * self.indicator_weights['trend'])
            elif trend.get('bearish_crossover'):
                sell_signals.append("EMA Bearish Crossover")
                weighted_sell_confidence.append(30 * self.indicator_weights['trend'])
        
        if bb:
            if bb['at_lower']:
                buy_signals.append("BB Lower Band Bounce")
                weighted_buy_confidence.append(15)
            elif bb['at_upper']:
                sell_signals.append("BB Upper Band Rejection")
                weighted_sell_confidence.append(15)
        
        if rsi_divergence.get('bullish_divergence'):
            buy_signals.append("Bullish Divergence (RSI)")
            strength = min(30, rsi_divergence.get('divergence_strength', 20))
            weighted_buy_confidence.append(strength * self.indicator_weights['divergence'])
            signal_details['divergence_detected'] = True
        
        if rsi_divergence.get('bearish_divergence'):
            sell_signals.append("Bearish Divergence (RSI)")
            strength = min(30, rsi_divergence.get('divergence_strength', 20))
            weighted_sell_confidence.append(strength * self.indicator_weights['divergence'])
            signal_details['divergence_detected'] = True
        
        if support_resistance.get('near_support'):
            buy_signals.append("Near Support Level")
            weighted_buy_confidence.append(15 * self.indicator_weights['support_resistance'])
        
        if support_resistance.get('near_resistance'):
            sell_signals.append("Near Resistance Level")
            weighted_sell_confidence.append(15 * self.indicator_weights['support_resistance'])
        
        if volume['is_surge']:
            multiplier = volume['multiplier']
            surge_strength = min(30, multiplier * 10)
            
            if len(buy_signals) > len(sell_signals):
                buy_signals.append(f"Volume Surge ({multiplier:.1f}x)")
                weighted_buy_confidence.append(surge_strength * self.indicator_weights['volume'])
            elif len(sell_signals) > len(buy_signals):
                sell_signals.append(f"Volume Surge ({multiplier:.1f}x)")
                weighted_sell_confidence.append(surge_strength * self.indicator_weights['volume'])
        
        if momentum['trend'] == 'bullish' and momentum['strength'] > 0.5:
            buy_signals.append(f"Bullish Momentum ({momentum['change_percent']:.2f}%)")
            weighted_buy_confidence.append(15 * self.indicator_weights['momentum'])
        elif momentum['trend'] == 'bearish' and momentum['strength'] > 0.5:
            sell_signals.append(f"Bearish Momentum ({momentum['change_percent']:.2f}%)")
            weighted_sell_confidence.append(15 * self.indicator_weights['momentum'])
        
        min_signals_required = self.config['signals'].get('min_signals_required', 0)
        
        # Debug: Log signal counts for troubleshooting (first 10 only)
        if len(buy_signals) > 0 or len(sell_signals) > 0:
            if not hasattr(self, '_debug_count'):
                self._debug_count = 0
            if self._debug_count < 10:
                logger.info(f"   📊 Signals detected - Buy:{len(buy_signals)} Sell:{len(sell_signals)} (Need >{min_signals_required})")
                if len(buy_signals) > 0:
                    logger.info(f"      BUY: {', '.join(buy_signals[:3])}")
                if len(sell_signals) > 0:
                    logger.info(f"      SELL: {', '.join(sell_signals[:3])}")
                self._debug_count += 1
        
        if len(buy_signals) > len(sell_signals) and len(buy_signals) > min_signals_required:
            direction = "LONG"
            reasons = buy_signals
            raw_score = sum(weighted_buy_confidence)
            
            conflicting_signals_penalty = len(sell_signals) * 5
            adjusted_score = max(0, raw_score - conflicting_signals_penalty)
            
            confidence = self._calculate_calibrated_confidence(adjusted_score)
            
        elif len(sell_signals) > len(buy_signals) and len(sell_signals) > min_signals_required:
            direction = "SHORT"
            reasons = sell_signals
            raw_score = sum(weighted_sell_confidence)
            
            conflicting_signals_penalty = len(buy_signals) * 5
            adjusted_score = max(0, raw_score - conflicting_signals_penalty)
            
            confidence = self._calculate_calibrated_confidence(adjusted_score)
            
        else:
            return "NEUTRAL", 0, [], signal_details
        
        if trend:
            trend_alignment_bonus = 0
            if direction == "LONG" and trend.get('bullish_trend'):
                trend_alignment_bonus = 8
            elif direction == "SHORT" and trend.get('bearish_trend'):
                trend_alignment_bonus = 8
            
            confidence = min(100, confidence + trend_alignment_bonus)
        
        return direction, confidence, reasons, signal_details
    
    def _calculate_calibrated_confidence(self, raw_score: float) -> float:
        if raw_score <= 0:
            return 0
        
        if raw_score < 50:
            return raw_score * 0.6
        elif raw_score < 100:
            return 30 + (raw_score - 50) * 0.8
        elif raw_score < 150:
            return 70 + (raw_score - 100) * 0.4
        elif raw_score < 200:
            return 90 + (raw_score - 150) * 0.15
        else:
            return min(100, 97.5 + (raw_score - 200) * 0.05)
    
    def _can_send_alert(self, coin_symbol: str, direction: str) -> bool:
        last_alert = self.last_alert_time[coin_symbol][direction]
        cooldown = timedelta(minutes=self.cooldown_minutes)
        return datetime.now() - last_alert >= cooldown
    
    def rank_signals(self, signals: List[Dict]) -> List[Dict]:
        def signal_score(sig):
            confidence = sig['confidence']
            
            has_divergence = sig.get('signal_details', {}).get('divergence_detected', False)
            trend_aligned = False
            
            analysis = sig.get('analysis', {})
            trend = analysis.get('trend', {})
            if trend:
                if sig['direction'] == 'LONG' and trend.get('bullish_trend'):
                    trend_aligned = True
                elif sig['direction'] == 'SHORT' and trend.get('bearish_trend'):
                    trend_aligned = True
            
            score = confidence
            if has_divergence:
                score += 5
            if trend_aligned:
                score += 10
            
            return score
        
        return sorted(signals, key=signal_score, reverse=True)
    
    def filter_top_signals(self, signals: List[Dict], max_alerts: int = None) -> List[Dict]:
        max_alerts_limit = max_alerts if max_alerts is not None else self.config['signals']['max_alerts_per_scan']
        ranked = self.rank_signals(signals)
        return ranked[:max_alerts_limit]
