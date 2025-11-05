import unittest
import numpy as np
from app.indicators import TechnicalIndicators

class TestTechnicalIndicators(unittest.TestCase):
    def setUp(self):
        self.config = {
            'signals': {
                'indicators': {
                    'rsi_period': 14,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70,
                    'macd_fast': 12,
                    'macd_slow': 26,
                    'macd_signal': 9,
                    'bb_period': 20,
                    'bb_std': 2,
                    'atr_period': 14,
                    'trend_ema_fast': 20,
                    'trend_ema_slow': 50,
                    'volume_surge_multiplier': 2.0
                }
            }
        }
        self.indicators = TechnicalIndicators(self.config)
    
    def test_rsi_calculation(self):
        prices = [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, 
                 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00, 46.03, 
                 46.41, 46.22, 45.64]
        
        rsi = self.indicators.calculate_rsi(prices)
        
        self.assertIsNotNone(rsi)
        self.assertGreaterEqual(rsi, 0)
        self.assertLessEqual(rsi, 100)
    
    def test_rsi_insufficient_data(self):
        prices = [100, 101, 102]
        rsi = self.indicators.calculate_rsi(prices)
        self.assertIsNone(rsi)
    
    def test_atr_calculation(self):
        highs = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62]
        lows = [46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
        closes = [47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61]
        
        atr = self.indicators.calculate_atr(highs, lows, closes)
        
        self.assertIsNotNone(atr)
        self.assertGreater(atr, 0)
    
    def test_atr_insufficient_data(self):
        highs = [48, 49, 50]
        lows = [46, 47, 48]
        closes = [47, 48, 49]
        
        atr = self.indicators.calculate_atr(highs, lows, closes)
        self.assertIsNone(atr)
    
    def test_macd_calculation(self):
        prices = list(range(100, 150))
        
        macd = self.indicators.calculate_macd(prices)
        
        self.assertIsNotNone(macd)
        self.assertIn('macd', macd)
        self.assertIn('signal', macd)
        self.assertIn('histogram', macd)
        self.assertIn('bullish_crossover', macd)
        self.assertIn('bearish_crossover', macd)
    
    def test_macd_bullish_crossover(self):
        prices = [100] * 30 + list(range(100, 120))
        
        macd = self.indicators.calculate_macd(prices)
        
        self.assertIsNotNone(macd)
        self.assertGreater(macd['histogram'], 0)
    
    def test_bollinger_bands(self):
        prices = [100, 102, 101, 103, 102, 104, 103, 105, 104, 106, 
                 105, 107, 106, 108, 107, 109, 108, 110, 109, 111, 110]
        
        bb = self.indicators.calculate_bollinger_bands(prices)
        
        self.assertIsNotNone(bb)
        self.assertIn('upper', bb)
        self.assertIn('middle', bb)
        self.assertIn('lower', bb)
        self.assertGreater(bb['upper'], bb['middle'])
        self.assertGreater(bb['middle'], bb['lower'])
    
    def test_trend_emas(self):
        prices = list(range(100, 200))
        
        trend = self.indicators.calculate_trend_emas(prices)
        
        self.assertIsNotNone(trend)
        self.assertIn('ema_fast', trend)
        self.assertIn('ema_slow', trend)
        self.assertIn('bullish_trend', trend)
        self.assertIn('bearish_trend', trend)
        self.assertIn('trend', trend)
    
    def test_bullish_trend_detection(self):
        prices = list(range(100, 200))
        
        trend = self.indicators.calculate_trend_emas(prices)
        
        self.assertTrue(trend['bullish_trend'])
        self.assertFalse(trend['bearish_trend'])
        self.assertEqual(trend['trend'], 'bullish')
    
    def test_bearish_trend_detection(self):
        prices = list(range(200, 100, -1))
        
        trend = self.indicators.calculate_trend_emas(prices)
        
        self.assertFalse(trend['bullish_trend'])
        self.assertTrue(trend['bearish_trend'])
        self.assertEqual(trend['trend'], 'bearish')
    
    def test_divergence_detection(self):
        prices = [100, 95, 90, 85, 80, 78, 76, 75, 74, 73]
        indicators = [50, 48, 47, 49, 51, 52, 54, 55, 56, 58]
        
        divergence = self.indicators.detect_divergence(prices, indicators, lookback=5)
        
        self.assertIn('bullish_divergence', divergence)
        self.assertIn('bearish_divergence', divergence)
        self.assertIn('divergence_strength', divergence)
    
    def test_obv_calculation(self):
        prices = [100, 102, 101, 103, 102, 104]
        volumes = [1000, 1100, 900, 1200, 800, 1300]
        
        obv = self.indicators.calculate_obv(prices, volumes)
        
        self.assertIsNotNone(obv)
        self.assertIsInstance(obv, float)
    
    def test_volume_surge_detection(self):
        volume_history = [1000, 1100, 900, 1000, 1050, 980, 1020, 990, 1010, 1000]
        current_volume = 2500
        
        volume_analysis = self.indicators.detect_volume_surge(current_volume, volume_history)
        
        self.assertTrue(volume_analysis['is_surge'])
        self.assertGreater(volume_analysis['multiplier'], 2.0)
    
    def test_no_volume_surge(self):
        volume_history = [1000, 1100, 900, 1000, 1050, 980, 1020, 990, 1010, 1000]
        current_volume = 1050
        
        volume_analysis = self.indicators.detect_volume_surge(current_volume, volume_history)
        
        self.assertFalse(volume_analysis['is_surge'])
    
    def test_support_resistance_detection(self):
        prices = [100, 102, 98, 101, 99, 103, 97, 102, 98, 104, 
                 96, 103, 99, 105, 98, 104, 100, 106, 99, 105, 101]
        
        sr = self.indicators.detect_support_resistance(prices)
        
        self.assertIn('support_levels', sr)
        self.assertIn('resistance_levels', sr)
        self.assertIsInstance(sr['support_levels'], list)
        self.assertIsInstance(sr['resistance_levels'], list)
    
    def test_momentum_detection_bullish(self):
        prices = [100, 101, 102, 103, 104]
        
        momentum = self.indicators.detect_price_momentum(prices)
        
        self.assertEqual(momentum['trend'], 'bullish')
        self.assertGreater(momentum['change_percent'], 0)
    
    def test_momentum_detection_bearish(self):
        prices = [104, 103, 102, 101, 100]
        
        momentum = self.indicators.detect_price_momentum(prices)
        
        self.assertEqual(momentum['trend'], 'bearish')
        self.assertLess(momentum['change_percent'], 0)
    
    def test_analyze_coin_complete(self):
        prices = list(range(100, 200))
        highs = [p + 2 for p in prices]
        lows = [p - 2 for p in prices]
        volumes = [1000 + i * 10 for i in range(len(prices))]
        current_volume = 2000
        
        analysis = self.indicators.analyze_coin(prices, highs, lows, current_volume, volumes)
        
        self.assertIn('rsi', analysis)
        self.assertIn('atr', analysis)
        self.assertIn('macd', analysis)
        self.assertIn('bollinger_bands', analysis)
        self.assertIn('trend', analysis)
        self.assertIn('volume', analysis)
        self.assertIn('momentum', analysis)
        self.assertIn('support_resistance', analysis)
        self.assertIn('obv', analysis)
        self.assertIn('has_data', analysis)
        self.assertTrue(analysis['has_data'])
    
    def test_ema_calculation(self):
        prices = np.array([100, 102, 101, 103, 102, 104, 103, 105, 104, 106])
        period = 5
        
        ema = self.indicators._calculate_ema(prices, period)
        
        self.assertEqual(len(ema), len(prices))
        self.assertGreater(ema[-1], ema[0])

if __name__ == '__main__':
    unittest.main()

