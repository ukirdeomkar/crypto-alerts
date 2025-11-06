import sys
sys.path.insert(0, '.')

indicator_weights = {
    'rsi': 1.0,
    'macd': 1.1,
    'trend': 1.2,
    'volume': 1.3,
    'momentum': 1.0,
    'divergence': 1.2,
    'support_resistance': 1.1
}

def calculate_calibrated_confidence(raw_score):
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

print("=" * 80)
print("TRADING-CALIBRATED CONFIDENCE SCALE")
print("=" * 80)
print("\nCalibration Curve (designed for scalping reality):")
print("  0-50 pts   -> 0-30%   (Weak: 1-2 indicators)")
print("  50-100 pts -> 30-70%  (Good: 3-4 indicators)")
print("  100-150 pts-> 70-90%  (Strong: 4-5 indicators)")
print("  150-200 pts-> 90-97%  (Exceptional: 6+ indicators)")
print("  200+ pts   -> 97-100% (Unicorn: all indicators max strength)")
print("\n" + "-" * 80)

scenarios = [
    {
        "name": "SCALPING BREAD & BUTTER (4 indicators)",
        "contributions": [
            ("MACD Crossover", 25 * 1.1),
            ("Trend Crossover", 30 * 1.2),
            ("Volume Surge", 30 * 1.3),
            ("Momentum", 15 * 1.0)
        ],
        "conflicting": 0
    },
    {
        "name": "STRONG CONFLUENCE (5 indicators)",
        "contributions": [
            ("RSI Oversold", 20 * 1.0),
            ("MACD Histogram", 15 * 1.1),
            ("Trend Strength", 20 * 1.2),
            ("Volume Surge", 25 * 1.3),
            ("Support Level", 15 * 1.1)
        ],
        "conflicting": 1
    },
    {
        "name": "EXCEPTIONAL SETUP (7 indicators)",
        "contributions": [
            ("RSI Oversold", 25 * 1.0),
            ("MACD Crossover", 25 * 1.1),
            ("Trend Crossover", 30 * 1.2),
            ("Volume Surge", 30 * 1.3),
            ("Divergence", 30 * 1.2),
            ("Support Level", 15 * 1.1),
            ("Momentum", 15 * 1.0)
        ],
        "conflicting": 0
    },
    {
        "name": "WEAK SIGNAL (2 indicators)",
        "contributions": [
            ("RSI Oversold", 15 * 1.0),
            ("BB Lower Band", 15)
        ],
        "conflicting": 0
    },
    {
        "name": "DECENT SETUP (3 indicators with conflict)",
        "contributions": [
            ("MACD Positive", 10 * 1.1),
            ("Trend Strength", 15 * 1.2),
            ("Volume", 20 * 1.3)
        ],
        "conflicting": 2
    },
    {
        "name": "EARLY MOMENTUM CATCH (3 strong indicators)",
        "contributions": [
            ("MACD Crossover", 25 * 1.1),
            ("Volume Surge", 30 * 1.3),
            ("Momentum", 15 * 1.0)
        ],
        "conflicting": 0
    }
]

print("\nSIGNAL SCENARIOS:\n")

for scenario in scenarios:
    raw_score = sum(contrib[1] for contrib in scenario['contributions'])
    penalty = scenario['conflicting'] * 5
    adjusted_score = max(0, raw_score - penalty)
    
    old_confidence = min(100, adjusted_score)
    new_confidence = calculate_calibrated_confidence(adjusted_score)
    new_confidence_with_bonus = min(100, new_confidence + 8)
    
    print(f"{scenario['name']}:")
    print(f"  Indicators:")
    for name, contrib in scenario['contributions']:
        print(f"    - {name}: {contrib:.1f} pts")
    print(f"  Raw score: {raw_score:.1f}")
    print(f"  Conflicting signals: {scenario['conflicting']} (penalty: -{penalty} pts)")
    print(f"  Adjusted score: {adjusted_score:.1f}")
    print(f"  OLD (broken): {old_confidence:.1f}%")
    print(f"  NEW (calibrated): {new_confidence:.1f}%")
    print(f"  With trend alignment: {new_confidence_with_bonus:.1f}%")
    
    if new_confidence >= 70:
        quality = "STRONG - Take this"
    elif new_confidence >= 55:
        quality = "GOOD - Valid for scalping"
    elif new_confidence >= 40:
        quality = "DECENT - Aggressive only"
    else:
        quality = "WEAK - Skip"
    print(f"  VERDICT: {quality}")
    print()

print("=" * 80)
print("TRADING IMPACT")
print("=" * 80)
print("""
CONFIDENCE THRESHOLDS (recommended after fix):
- Conservative: 55-60% (5+ indicators, high quality)
- Balanced: 45-50% (4-5 indicators, good quality)
- Volatile Scalper: 35-40% (3-4 indicators, catch early moves)
- Ultra Scalper: 25-30% (2-3 indicators, aggressive entries)

KEY INSIGHT:
4-5 solid indicators = 60-75% confidence (professional setup)
This is where scalpers make money - NOT waiting for 100% perfection

REAL TRADING LOGIC:
- 70%+ confidence: Max position size, this is your bread & butter
- 55-70%: Standard position size, take every one
- 40-55%: Reduced size, scalping strategies only
- <40%: Pass unless ultra-aggressive strategy
""")
print("=" * 80)
