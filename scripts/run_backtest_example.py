import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.insert(0, project_root)

from datetime import datetime
from app.utils import load_config, setup_logging
from app.indicators import TechnicalIndicators
from app.signal_generator import SignalGenerator
from app.risk_manager import RiskManager
from tests.backtesting import BacktestEngine, ParameterOptimizer

def generate_sample_data():
    import random
    from datetime import timedelta
    
    data = []
    start_date = datetime(2024, 1, 1)
    price = 100.0
    
    for i in range(10000):
        change = random.uniform(-0.02, 0.02)
        price = price * (1 + change)
        
        high = price * (1 + random.uniform(0, 0.01))
        low = price * (1 - random.uniform(0, 0.01))
        volume = random.uniform(800, 1200)
        
        data.append({
            'timestamp': start_date + timedelta(minutes=i*5),
            'symbol': 'BTC',
            'price': price,
            'high': high,
            'low': low,
            'volume': volume
        })
    
    return data

def run_simple_backtest():
    print("Loading configuration...")
    config = load_config()
    
    print("Generating sample historical data...")
    historical_data = generate_sample_data()
    
    print("Initializing components...")
    indicators = TechnicalIndicators(config)
    risk_manager = RiskManager(config)
    signal_generator = SignalGenerator(config, indicators, risk_manager)
    
    print("Running backtest...")
    backtest = BacktestEngine(config, indicators, signal_generator, risk_manager)
    
    metrics = backtest.run_backtest(historical_data)
    
    backtest.print_summary(metrics)
    
    backtest.export_trades('backtest_trades.csv')
    backtest.export_equity_curve('backtest_equity_curve.csv')
    
    print("Backtest complete! Check backtest_trades.csv and backtest_equity_curve.csv for details.")

def run_parameter_optimization():
    print("Loading configuration...")
    config = load_config()
    
    print("Generating sample historical data...")
    historical_data = generate_sample_data()
    
    print("Running parameter optimization...")
    optimizer = ParameterOptimizer(
        config,
        TechnicalIndicators,
        SignalGenerator,
        RiskManager
    )
    
    print("\nOptimizing RSI periods...")
    optimizer.optimize_rsi_periods(historical_data, periods=[7, 10, 14, 21])
    
    print("\nOptimizing confidence thresholds...")
    optimizer.optimize_confidence_threshold(historical_data, thresholds=[50, 60, 70, 80])
    
    best_rsi = optimizer.get_best_parameters()
    print(f"\nBest configuration: {best_rsi['parameter']} = {best_rsi['value']}")
    print(f"Return: {best_rsi['metrics']['total_return_percent']:.2f}%")
    print(f"Win Rate: {best_rsi['metrics']['win_rate']:.2f}%")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run backtesting on trading strategy')
    parser.add_argument('--mode', choices=['backtest', 'optimize'], default='backtest',
                       help='Run mode: backtest or optimize')
    
    args = parser.parse_args()
    
    if args.mode == 'backtest':
        run_simple_backtest()
    else:
        run_parameter_optimization()

