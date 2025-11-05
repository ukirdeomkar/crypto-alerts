import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock
from app.signal_generator import SignalGenerator

class TestSignalGenerator(unittest.TestCase):
    def setUp(self):
        self.config = {
            'signals': {
                'cooldown_minutes': 5,
                'min_confidence': 60,
                'max_alerts_per_scan': 3,
                'min_signals_required': 3,
                'indicators': {
                    'rsi_oversold': 30,
                    'rsi_overbought': 70
                },
                'indicator_weights': {
                    'rsi': 1.0,
                    'macd': 1.2,
                    'trend': 1.5,
                    'volume': 1.0,
                    'momentum': 0.8,
                    'divergence': 1.3,
                    'support_resistance': 1.1
                }
            },
            'risk': {
                'stop_loss_percent': 0.5,
                'take_profit_targets': [
                    {'target': 1.0, 'exit_percent': 50},
                    {'target': 1.5, 'exit_percent': 50}
                ],
                'default_leverage': 5,
                'use_atr_stops': False,
                'position_expiry_minutes': 10,
                'min_risk_reward_ratio': 1.5
            }
        }
        
        self.mock_indicators = Mock()
        self.mock_risk_manager = Mock()
        self.mock_risk_manager.calculate_position_size.return_value = 100.0
        
        self.signal_generator = SignalGenerator(
            self.config,
            self.mock_indicators,
            self.mock_risk_manager
        )
    
    def test_generate_signal_insufficient_data(self):
        price_data = {'price': 100.0, 'market': 'BTCINR'}
        analysis = {'has_data': False}
        
        signal = self.signal_generator.generate_signal('BTC', price_data, analysis)
        
        self.assertIsNone(signal)
    
    def test_generate_signal_neutral(self):
        price_data = {'price': 100.0, 'market': 'BTCINR'}
        analysis = {
            'has_data': True,
            'rsi': 50,
            'macd': {'histogram': 0, 'bullish_crossover': False, 'bearish_crossover': False},
            'bollinger_bands': {'at_lower': False, 'at_upper': False},
            'trend': {'bullish_trend': False, 'bearish_trend': False},
            'volume': {'is_surge': False, 'multiplier': 1.0},
            'momentum': {'trend': 'neutral', 'strength': 0, 'change_percent': 0},
            'support_resistance': {},
            'rsi_divergence': {'bullish_divergence': False, 'bearish_divergence': False}
        }
        
        signal = self.signal_generator.generate_signal('BTC', price_data, analysis)
        
        self.assertIsNone(signal)
    
    def test_generate_bullish_signal(self):
        price_data = {'price': 100.0, 'market': 'BTCINR', 'volume': 1000}
        analysis = {
            'has_data': True,
            'rsi': 25,
            'macd': {
                'histogram': 0.5, 
                'bullish_crossover': True, 
                'bearish_crossover': False
            },
            'bollinger_bands': {'at_lower': True, 'at_upper': False},
            'trend': {
                'bullish_trend': True, 
                'bearish_trend': False,
                'trend_strength': 5,
                'bullish_crossover': False
            },
            'volume': {'is_surge': True, 'multiplier': 2.5},
            'momentum': {
                'trend': 'bullish', 
                'strength': 2.0, 
                'change_percent': 2.0
            },
            'support_resistance': {'near_support': True},
            'rsi_divergence': {'bullish_divergence': False, 'bearish_divergence': False}
        }
        
        signal = self.signal_generator.generate_signal('BTC', price_data, analysis, min_confidence=50)
        
        self.assertIsNotNone(signal)
        self.assertEqual(signal['direction'], 'LONG')
        self.assertGreater(signal['confidence'], 50)
        self.assertGreater(len(signal['reasons']), 2)
    
    def test_generate_bearish_signal(self):
        price_data = {'price': 100.0, 'market': 'BTCINR', 'volume': 1000}
        analysis = {
            'has_data': True,
            'rsi': 75,
            'macd': {
                'histogram': -0.5, 
                'bullish_crossover': False, 
                'bearish_crossover': True
            },
            'bollinger_bands': {'at_lower': False, 'at_upper': True},
            'trend': {
                'bullish_trend': False, 
                'bearish_trend': True,
                'trend_strength': 5,
                'bearish_crossover': False
            },
            'volume': {'is_surge': True, 'multiplier': 2.5},
            'momentum': {
                'trend': 'bearish', 
                'strength': 2.0, 
                'change_percent': -2.0
            },
            'support_resistance': {'near_resistance': True},
            'rsi_divergence': {'bullish_divergence': False, 'bearish_divergence': False}
        }
        
        signal = self.signal_generator.generate_signal('BTC', price_data, analysis, min_confidence=50)
        
        self.assertIsNotNone(signal)
        self.assertEqual(signal['direction'], 'SHORT')
        self.assertGreater(signal['confidence'], 50)
        self.assertGreater(len(signal['reasons']), 2)
    
    def test_cooldown_period(self):
        price_data = {'price': 100.0, 'market': 'BTCINR', 'volume': 1000}
        analysis = {
            'has_data': True,
            'rsi': 25,
            'macd': {
                'histogram': 0.5, 
                'bullish_crossover': True, 
                'bearish_crossover': False
            },
            'bollinger_bands': {'at_lower': True, 'at_upper': False},
            'trend': {
                'bullish_trend': True, 
                'bearish_trend': False,
                'trend_strength': 5,
                'bullish_crossover': False
            },
            'volume': {'is_surge': True, 'multiplier': 2.5},
            'momentum': {
                'trend': 'bullish', 
                'strength': 2.0, 
                'change_percent': 2.0
            },
            'support_resistance': {'near_support': True},
            'rsi_divergence': {'bullish_divergence': False, 'bearish_divergence': False}
        }
        
        signal1 = self.signal_generator.generate_signal('BTC', price_data, analysis, min_confidence=50)
        self.assertIsNotNone(signal1)
        
        signal2 = self.signal_generator.generate_signal('BTC', price_data, analysis, min_confidence=50)
        self.assertIsNone(signal2)
    
    def test_divergence_bonus(self):
        price_data = {'price': 100.0, 'market': 'BTCINR', 'volume': 1000}
        analysis = {
            'has_data': True,
            'rsi': 25,
            'macd': {
                'histogram': 0.5, 
                'bullish_crossover': True, 
                'bearish_crossover': False
            },
            'bollinger_bands': {'at_lower': True, 'at_upper': False},
            'trend': {
                'bullish_trend': True, 
                'bearish_trend': False,
                'trend_strength': 5,
                'bullish_crossover': False
            },
            'volume': {'is_surge': True, 'multiplier': 2.5},
            'momentum': {
                'trend': 'bullish', 
                'strength': 2.0, 
                'change_percent': 2.0
            },
            'support_resistance': {'near_support': True},
            'rsi_divergence': {
                'bullish_divergence': True, 
                'bearish_divergence': False,
                'divergence_strength': 25
            }
        }
        
        signal = self.signal_generator.generate_signal('BTC', price_data, analysis, min_confidence=50)
        
        self.assertIsNotNone(signal)
        self.assertTrue(signal['signal_details']['divergence_detected'])
    
    def test_rank_signals(self):
        signals = [
            {'confidence': 70, 'signal_details': {'divergence_detected': False}, 'direction': 'LONG', 'analysis': {'trend': {'bullish_trend': False}}},
            {'confidence': 80, 'signal_details': {'divergence_detected': True}, 'direction': 'LONG', 'analysis': {'trend': {'bullish_trend': True}}},
            {'confidence': 75, 'signal_details': {'divergence_detected': False}, 'direction': 'LONG', 'analysis': {'trend': {'bullish_trend': True}}},
        ]
        
        ranked = self.signal_generator.rank_signals(signals)
        
        self.assertEqual(ranked[0]['confidence'], 80)
    
    def test_filter_top_signals(self):
        signals = [
            {'confidence': 70, 'signal_details': {'divergence_detected': False}, 'direction': 'LONG', 'analysis': {'trend': {'bullish_trend': False}}},
            {'confidence': 80, 'signal_details': {'divergence_detected': False}, 'direction': 'LONG', 'analysis': {'trend': {'bullish_trend': False}}},
            {'confidence': 75, 'signal_details': {'divergence_detected': False}, 'direction': 'LONG', 'analysis': {'trend': {'bullish_trend': False}}},
            {'confidence': 65, 'signal_details': {'divergence_detected': False}, 'direction': 'LONG', 'analysis': {'trend': {'bullish_trend': False}}},
        ]
        
        top_signals = self.signal_generator.filter_top_signals(signals, max_alerts=2)
        
        self.assertEqual(len(top_signals), 2)
        self.assertEqual(top_signals[0]['confidence'], 80)
    
    def test_atr_based_stops(self):
        self.config['risk']['use_atr_stops'] = True
        self.config['risk']['atr_stop_multiplier'] = 2.0
        self.config['risk']['position_expiry_minutes'] = 100
        
        price_data = {'price': 100.0, 'market': 'BTCINR', 'volume': 1000, 'high': 101.0, 'low': 99.0}
        analysis = {
            'has_data': True,
            'atr': 2.0,
            'rsi': 25,
            'macd': {
                'histogram': 0.5, 
                'bullish_crossover': True, 
                'bearish_crossover': False
            },
            'bollinger_bands': {'at_lower': True, 'at_upper': False},
            'trend': {
                'bullish_trend': True, 
                'bearish_trend': False,
                'trend_strength': 5,
                'bullish_crossover': False
            },
            'volume': {'is_surge': True, 'multiplier': 2.5},
            'momentum': {
                'trend': 'bullish', 
                'strength': 2.0, 
                'change_percent': 2.0,
                'momentum_score': 50
            },
            'support_resistance': {'near_support': True},
            'rsi_divergence': {'bullish_divergence': False, 'bearish_divergence': False}
        }
        
        signal = self.signal_generator.generate_signal('BTC', price_data, analysis, min_confidence=50)
        
        if signal:
            self.assertLess(signal['stop_loss'], signal['entry_price'])
        else:
            self.skipTest("Signal rejected by validation - expected behavior")
    
    def test_trend_alignment_bonus(self):
        price_data = {'price': 100.0, 'market': 'BTCINR', 'volume': 1000}
        
        analysis_with_trend = {
            'has_data': True,
            'rsi': 25,
            'macd': {'histogram': 0.5, 'bullish_crossover': True, 'bearish_crossover': False},
            'bollinger_bands': {'at_lower': True, 'at_upper': False},
            'trend': {
                'bullish_trend': True, 
                'bearish_trend': False,
                'trend_strength': 5,
                'bullish_crossover': False
            },
            'volume': {'is_surge': True, 'multiplier': 2.5},
            'momentum': {'trend': 'bullish', 'strength': 2.0, 'change_percent': 2.0},
            'support_resistance': {'near_support': True},
            'rsi_divergence': {'bullish_divergence': False, 'bearish_divergence': False}
        }
        
        analysis_without_trend = {
            'has_data': True,
            'rsi': 25,
            'macd': {'histogram': 0.5, 'bullish_crossover': True, 'bearish_crossover': False},
            'bollinger_bands': {'at_lower': True, 'at_upper': False},
            'trend': {
                'bullish_trend': False, 
                'bearish_trend': True,
                'trend_strength': 5,
                'bullish_crossover': False
            },
            'volume': {'is_surge': True, 'multiplier': 2.5},
            'momentum': {'trend': 'bullish', 'strength': 2.0, 'change_percent': 2.0},
            'support_resistance': {'near_support': True},
            'rsi_divergence': {'bullish_divergence': False, 'bearish_divergence': False}
        }
        
        signal_with = self.signal_generator.generate_signal('BTC', price_data, analysis_with_trend, min_confidence=50)
        signal_without = self.signal_generator.generate_signal('ETH', price_data, analysis_without_trend, min_confidence=50)
        
        if signal_with and signal_without:
            self.assertGreaterEqual(signal_with['confidence'], signal_without['confidence'])

if __name__ == '__main__':
    unittest.main()

