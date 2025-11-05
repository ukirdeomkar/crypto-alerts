# Testing & Backtesting Framework

Comprehensive testing suite and backtesting framework for the crypto alerts trading system.

## 📁 Structure

```
tests/
├── __init__.py                  # Package init
├── test_indicators.py           # Unit tests for technical indicators
├── test_signal_generator.py     # Unit tests for signal generation
├── backtesting.py              # Backtesting engine & optimizer
├── run_backtest_example.py     # Example backtest scripts
└── README.md                   # This file
```

## 🧪 Running Unit Tests

### Run All Tests
```bash
python -m pytest tests/
```

### Run Specific Test File
```bash
python -m pytest tests/test_indicators.py
python -m pytest tests/test_signal_generator.py
```

### Run with Coverage
```bash
python -m pytest --cov=app tests/
```

### Run with Verbose Output
```bash
python -m pytest -v tests/
```

## 📊 Unit Tests Coverage

### test_indicators.py
Tests for all technical indicators:
- ✅ RSI calculation (with Wilder's smoothing)
- ✅ ATR calculation
- ✅ MACD calculation and crossovers
- ✅ Bollinger Bands
- ✅ Trend EMAs (bullish/bearish detection)
- ✅ Divergence detection
- ✅ OBV (On-Balance Volume)
- ✅ Volume surge detection
- ✅ Support/Resistance levels
- ✅ Price momentum
- ✅ Complete coin analysis

### test_signal_generator.py
Tests for signal generation logic:
- ✅ Signal generation with insufficient data
- ✅ Neutral signal detection
- ✅ Bullish signal generation
- ✅ Bearish signal generation
- ✅ Cooldown period enforcement
- ✅ Divergence bonus
- ✅ Signal ranking
- ✅ Top signal filtering
- ✅ ATR-based stops
- ✅ Trend alignment bonus

## 🔬 Backtesting Framework

### BacktestEngine

Complete backtesting engine that simulates trading on historical data.

**Features:**
- Historical data replay
- Position management (open/close)
- Stop loss and take profit execution
- Time-based exits
- Transaction cost simulation
- Equity curve tracking
- Comprehensive performance metrics

**Usage Example:**
```python
from tests.backtesting import BacktestEngine
from app.indicators import TechnicalIndicators
from app.signal_generator import SignalGenerator
from app.risk_manager import RiskManager
from app.utils import load_config

config = load_config()
indicators = TechnicalIndicators(config)
risk_manager = RiskManager(config)
signal_generator = SignalGenerator(config, indicators, risk_manager)

backtest = BacktestEngine(config, indicators, signal_generator, risk_manager)

historical_data = backtest.load_historical_data('data/historical_prices.csv')
metrics = backtest.run_backtest(historical_data)

backtest.print_summary(metrics)
backtest.export_trades('results/trades.csv')
backtest.export_equity_curve('results/equity_curve.csv')
```

### Performance Metrics Calculated

- **Total Trades**: Number of trades executed
- **Win Rate**: Percentage of winning trades
- **Total PnL**: Net profit/loss
- **Total Return %**: Percentage return on capital
- **Average Win/Loss**: Mean profit/loss per trade
- **Profit Factor**: Ratio of gross profit to gross loss
- **Max Drawdown**: Maximum peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return metric
- **Average Hold Time**: Mean position duration

### ParameterOptimizer

Systematically test different parameter combinations to find optimal settings.

**Features:**
- RSI period optimization
- Confidence threshold optimization
- Easy to extend for other parameters
- Automatic best parameter selection

**Usage Example:**
```python
from tests.backtesting import ParameterOptimizer

optimizer = ParameterOptimizer(
    config,
    TechnicalIndicators,
    SignalGenerator,
    RiskManager
)

# Optimize RSI periods
optimizer.optimize_rsi_periods(historical_data, periods=[7, 10, 14, 21])

# Optimize confidence thresholds
optimizer.optimize_confidence_threshold(historical_data, thresholds=[50, 60, 70, 80])

# Get best parameters
best = optimizer.get_best_parameters(metric='total_return_percent')
print(f"Best: {best['parameter']} = {best['value']}")
```

## 🚀 Quick Start Examples

### 1. Verify Installation
```bash
python scripts/verify_installation.py
```

This will verify all components are working correctly.

### 2. Verify Calculations
```bash
python scripts/verify_calculations.py
```

This will verify all technical indicators match industry standards.

### 3. Run Simple Backtest
```bash
python scripts/run_backtest_example.py --mode backtest
```

This will:
- Generate sample historical data
- Run backtest with current config
- Print performance summary
- Export trades and equity curve to CSV

### 4. Run Parameter Optimization
```bash
python scripts/run_backtest_example.py --mode optimize
```

This will:
- Test multiple RSI periods
- Test multiple confidence thresholds
- Show results for each combination
- Report best parameters

## 📈 Historical Data Format

### CSV Format
```csv
timestamp,symbol,price,high,low,volume
2024-01-01 09:00:00,BTC,100.0,101.0,99.0,1000.0
2024-01-01 09:05:00,BTC,101.5,102.0,100.5,1100.0
```

### JSON Format
```json
[
  {
    "timestamp": "2024-01-01T09:00:00",
    "symbol": "BTC",
    "price": 100.0,
    "high": 101.0,
    "low": 99.0,
    "volume": 1000.0
  }
]
```

## 🎯 Creating Custom Tests

### Add New Indicator Test
```python
def test_new_indicator(self):
    prices = [100, 102, 101, 103, 102]
    
    result = self.indicators.calculate_new_indicator(prices)
    
    self.assertIsNotNone(result)
    self.assertGreater(result, 0)
```

### Add New Backtest Scenario
```python
def run_custom_scenario():
    config = load_config()
    config['signals']['min_confidence'] = 90  # Very conservative
    
    backtest = BacktestEngine(config, indicators, signal_generator, risk_manager)
    metrics = backtest.run_backtest(historical_data)
    
    assert metrics['win_rate'] > 70  # Expect high win rate
```

## 📊 Interpreting Results

### Good Backtest Results
- **Win Rate**: > 55%
- **Profit Factor**: > 1.5
- **Sharpe Ratio**: > 1.0
- **Max Drawdown**: < 20%
- **Total Return**: Positive and meaningful

### Warning Signs
- Win rate < 45% → Strategy may not work
- Profit Factor < 1.0 → Losing strategy
- Max Drawdown > 30% → Too risky
- Very few trades → Not enough data/too conservative

### Optimization Tips
1. **Don't Overfit**: Test on out-of-sample data
2. **Consider Transaction Costs**: Already included in backtest
3. **Check Different Market Conditions**: Bull, bear, sideways
4. **Validate Win Rate vs Return**: High win rate with small wins might underperform
5. **Monitor Max Drawdown**: Can you handle the worst case?

## 🔧 Advanced Usage

### Custom Metric Optimization
```python
# Optimize for Sharpe ratio instead of return
best = optimizer.get_best_parameters(metric='sharpe_ratio')
```

### Date Range Backtesting
```python
from datetime import datetime

metrics = backtest.run_backtest(
    historical_data,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 6, 30)
)
```

### Walk-Forward Optimization
```python
# Train on first 70% of data, test on last 30%
train_size = int(len(historical_data) * 0.7)
train_data = historical_data[:train_size]
test_data = historical_data[train_size:]

# Optimize on training data
optimizer.optimize_rsi_periods(train_data)
best = optimizer.get_best_parameters()

# Apply to test data with best parameters
config['signals']['indicators']['rsi_period'] = best['value']
backtest = BacktestEngine(config, indicators, signal_generator, risk_manager)
test_metrics = backtest.run_backtest(test_data)
```

## 🐛 Troubleshooting

### Import Errors
```bash
# Ensure you're in the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Insufficient Data
- Need at least 50 data points per symbol
- Ensure historical data has OHLCV (Open, High, Low, Close, Volume)

### Low Performance
- Try different parameter combinations
- Check if market conditions match your strategy
- Validate data quality (no gaps, outliers)

## 📦 Requirements

Additional packages for testing:
```bash
pip install pytest pytest-cov
```

## 🔗 Integration with CI/CD

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ --cov=app
```

## 📝 Notes

- **Sample Data**: `run_backtest_example.py` generates random data for demonstration
- **Real Data**: Use CoinDCX API or export your own historical data
- **Performance**: Backtests with 10,000+ data points may take a few minutes
- **Memory**: Large datasets may require optimization for memory usage

## 🎓 Next Steps

1. **Run Unit Tests**: Validate all components work correctly
2. **Generate Historical Data**: Export real price data from CoinDCX
3. **Run Backtest**: Test strategy on historical data
4. **Optimize Parameters**: Find best configuration for your strategy
5. **Paper Trade**: Test in real-time before going live
6. **Live Trading**: Deploy with optimized parameters

---

**Happy Testing! 📊🚀**

