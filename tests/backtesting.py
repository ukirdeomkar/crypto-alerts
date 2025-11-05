import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, config, indicators, signal_generator, risk_manager):
        self.config = config
        self.indicators = indicators
        self.signal_generator = signal_generator
        self.risk_manager = risk_manager
        
        self.trades = []
        self.open_positions = {}
        self.equity_curve = []
        self.initial_capital = config['risk']['total_capital']
        self.current_capital = self.initial_capital
        
    def load_historical_data(self, filepath: str) -> List[Dict]:
        data = []
        with open(filepath, 'r') as f:
            if filepath.endswith('.json'):
                data = json.load(f)
            elif filepath.endswith('.csv'):
                reader = csv.DictReader(f)
                for row in reader:
                    data.append({
                        'timestamp': datetime.fromisoformat(row['timestamp']),
                        'symbol': row['symbol'],
                        'price': float(row['price']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'volume': float(row['volume'])
                    })
        
        return sorted(data, key=lambda x: x['timestamp'])
    
    def run_backtest(self, historical_data: List[Dict], 
                     start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> Dict:
        
        if start_date:
            historical_data = [d for d in historical_data if d['timestamp'] >= start_date]
        if end_date:
            historical_data = [d for d in historical_data if d['timestamp'] <= end_date]
        
        symbol_data = defaultdict(lambda: {
            'prices': [],
            'highs': [],
            'lows': [],
            'volumes': [],
            'timestamps': []
        })
        
        for data_point in historical_data:
            symbol = data_point['symbol']
            symbol_data[symbol]['prices'].append(data_point['price'])
            symbol_data[symbol]['highs'].append(data_point['high'])
            symbol_data[symbol]['lows'].append(data_point['low'])
            symbol_data[symbol]['volumes'].append(data_point['volume'])
            symbol_data[symbol]['timestamps'].append(data_point['timestamp'])
            
            if len(symbol_data[symbol]['prices']) < 50:
                continue
            
            self._check_open_positions(symbol, data_point)
            
            analysis = self.indicators.analyze_coin(
                symbol_data[symbol]['prices'],
                symbol_data[symbol]['highs'],
                symbol_data[symbol]['lows'],
                data_point['volume'],
                symbol_data[symbol]['volumes']
            )
            
            if not analysis.get('has_data'):
                continue
            
            price_data = {
                'price': data_point['price'],
                'market': f"{symbol}INR",
                'volume': data_point['volume'],
                'high': data_point['high'],
                'low': data_point['low']
            }
            
            signal = self.signal_generator.generate_signal(
                symbol,
                price_data,
                analysis
            )
            
            if signal:
                self._execute_signal(signal, data_point['timestamp'])
            
            self.equity_curve.append({
                'timestamp': data_point['timestamp'],
                'equity': self.current_capital
            })
        
        self._close_all_positions(historical_data[-1]['timestamp'])
        
        return self._calculate_performance_metrics()
    
    def _execute_signal(self, signal: Dict, timestamp: datetime):
        symbol = signal['symbol']
        
        if symbol in self.open_positions:
            return
        
        if len(self.open_positions) >= self.config['risk']['max_concurrent_positions']:
            return
        
        position_size = signal['position_size']
        if position_size > self.current_capital:
            return
        
        self.open_positions[symbol] = {
            'entry_time': timestamp,
            'entry_price': signal['entry_price'],
            'direction': signal['direction'],
            'stop_loss': signal['stop_loss'],
            'targets': signal['targets'],
            'position_size': position_size,
            'leverage': signal['leverage'],
            'confidence': signal['confidence']
        }
        
        logger.info(f"[BACKTEST] Opened {signal['direction']} position on {symbol} at {signal['entry_price']}")
    
    def _check_open_positions(self, symbol: str, data_point: Dict):
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        current_price = data_point['price']
        high = data_point['high']
        low = data_point['low']
        
        exit_reason = None
        exit_price = None
        
        if position['direction'] == 'LONG':
            if low <= position['stop_loss']:
                exit_price = position['stop_loss']
                exit_reason = 'stop_loss'
            elif high >= position['targets'][0]['price']:
                exit_price = position['targets'][0]['price']
                exit_reason = 'target_1'
            elif high >= position['targets'][1]['price'] if len(position['targets']) > 1 else False:
                exit_price = position['targets'][1]['price']
                exit_reason = 'target_2'
        else:
            if high >= position['stop_loss']:
                exit_price = position['stop_loss']
                exit_reason = 'stop_loss'
            elif low <= position['targets'][0]['price']:
                exit_price = position['targets'][0]['price']
                exit_reason = 'target_1'
            elif low <= position['targets'][1]['price'] if len(position['targets']) > 1 else False:
                exit_price = position['targets'][1]['price']
                exit_reason = 'target_2'
        
        hold_time = (data_point['timestamp'] - position['entry_time']).total_seconds() / 60
        max_hold = self.config['risk'].get('position_expiry_minutes', 10)
        
        if hold_time >= max_hold:
            exit_price = current_price
            exit_reason = 'time_exit'
        
        if exit_price and exit_reason:
            self._close_position(symbol, exit_price, exit_reason, data_point['timestamp'])
    
    def _close_position(self, symbol: str, exit_price: float, exit_reason: str, timestamp: datetime):
        position = self.open_positions[symbol]
        
        entry_price = position['entry_price']
        direction = position['direction']
        leverage = position['leverage']
        position_size = position['position_size']
        
        if direction == 'LONG':
            price_change_percent = (exit_price - entry_price) / entry_price
        else:
            price_change_percent = (entry_price - exit_price) / entry_price
        
        gross_pnl = position_size * leverage * price_change_percent
        
        transaction_cost = position_size * (self.config['risk']['transaction_cost_percent'] / 100) * 2
        
        net_pnl = gross_pnl - transaction_cost
        
        self.current_capital += net_pnl
        
        hold_time = (timestamp - position['entry_time']).total_seconds() / 60
        
        trade_record = {
            'symbol': symbol,
            'direction': direction,
            'entry_time': position['entry_time'],
            'exit_time': timestamp,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'position_size': position_size,
            'leverage': leverage,
            'confidence': position['confidence'],
            'pnl': net_pnl,
            'pnl_percent': net_pnl / position_size * 100,
            'exit_reason': exit_reason,
            'hold_time_minutes': hold_time,
            'is_winner': net_pnl > 0
        }
        
        self.trades.append(trade_record)
        del self.open_positions[symbol]
        
        logger.info(f"[BACKTEST] Closed {direction} position on {symbol} at {exit_price} ({exit_reason}) | PnL: {net_pnl:.2f}")
    
    def _close_all_positions(self, timestamp: datetime):
        for symbol in list(self.open_positions.keys()):
            position = self.open_positions[symbol]
            current_price = position['entry_price']
            self._close_position(symbol, current_price, 'end_of_data', timestamp)
    
    def _calculate_performance_metrics(self) -> Dict:
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_return_percent': 0
            }
        
        winning_trades = [t for t in self.trades if t['is_winner']]
        losing_trades = [t for t in self.trades if not t['is_winner']]
        
        total_pnl = sum(t['pnl'] for t in self.trades)
        total_return_percent = (self.current_capital - self.initial_capital) / self.initial_capital * 100
        
        avg_win = statistics.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = statistics.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        profit_factor = abs(sum(t['pnl'] for t in winning_trades) / sum(t['pnl'] for t in losing_trades)) if losing_trades and sum(t['pnl'] for t in losing_trades) != 0 else float('inf')
        
        equity_values = [point['equity'] for point in self.equity_curve]
        peak = equity_values[0]
        max_drawdown = 0
        
        for value in equity_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak * 100 if peak > 0 else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        returns = []
        for i in range(1, len(equity_values)):
            ret = (equity_values[i] - equity_values[i-1]) / equity_values[i-1] * 100
            returns.append(ret)
        
        if returns and statistics.stdev(returns) > 0:
            sharpe_ratio = (statistics.mean(returns) / statistics.stdev(returns)) * (252 ** 0.5)
        else:
            sharpe_ratio = 0
        
        avg_hold_time = statistics.mean([t['hold_time_minutes'] for t in self.trades])
        
        metrics = {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.trades) * 100,
            'total_pnl': total_pnl,
            'total_return_percent': total_return_percent,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown_percent': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'avg_hold_time_minutes': avg_hold_time,
            'initial_capital': self.initial_capital,
            'final_capital': self.current_capital,
            'best_trade': max(self.trades, key=lambda t: t['pnl'])['pnl'],
            'worst_trade': min(self.trades, key=lambda t: t['pnl'])['pnl']
        }
        
        return metrics
    
    def export_trades(self, filepath: str):
        with open(filepath, 'w', newline='') as f:
            if not self.trades:
                return
            
            writer = csv.DictWriter(f, fieldnames=self.trades[0].keys())
            writer.writeheader()
            writer.writerows(self.trades)
        
        logger.info(f"Exported {len(self.trades)} trades to {filepath}")
    
    def export_equity_curve(self, filepath: str):
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'equity'])
            writer.writeheader()
            writer.writerows(self.equity_curve)
        
        logger.info(f"Exported equity curve to {filepath}")
    
    def print_summary(self, metrics: Dict):
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Capital: ₹{metrics['initial_capital']:,.2f}")
        print(f"Final Capital: ₹{metrics['final_capital']:,.2f}")
        print(f"Total Return: {metrics['total_return_percent']:.2f}%")
        print(f"Total PnL: ₹{metrics['total_pnl']:,.2f}")
        print("-"*60)
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Winning Trades: {metrics['winning_trades']}")
        print(f"Losing Trades: {metrics['losing_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print("-"*60)
        print(f"Average Win: ₹{metrics['avg_win']:,.2f}")
        print(f"Average Loss: ₹{metrics['avg_loss']:,.2f}")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Best Trade: ₹{metrics['best_trade']:,.2f}")
        print(f"Worst Trade: ₹{metrics['worst_trade']:,.2f}")
        print("-"*60)
        print(f"Max Drawdown: {metrics['max_drawdown_percent']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Avg Hold Time: {metrics['avg_hold_time_minutes']:.1f} minutes")
        print("="*60 + "\n")


class ParameterOptimizer:
    def __init__(self, config_template, indicators_class, signal_generator_class, 
                 risk_manager_class):
        self.config_template = config_template
        self.indicators_class = indicators_class
        self.signal_generator_class = signal_generator_class
        self.risk_manager_class = risk_manager_class
        self.results = []
    
    def optimize_rsi_periods(self, historical_data: List[Dict], 
                            periods: List[int] = [7, 10, 14, 21]) -> List[Dict]:
        
        for period in periods:
            config = self.config_template.copy()
            config['signals']['indicators']['rsi_period'] = period
            
            indicators = self.indicators_class(config)
            risk_manager = self.risk_manager_class(config)
            signal_generator = self.signal_generator_class(config, indicators, risk_manager)
            
            backtest = BacktestEngine(config, indicators, signal_generator, risk_manager)
            metrics = backtest.run_backtest(historical_data)
            
            self.results.append({
                'parameter': 'rsi_period',
                'value': period,
                'metrics': metrics
            })
            
            print(f"RSI Period {period}: Return {metrics['total_return_percent']:.2f}%, Win Rate {metrics['win_rate']:.2f}%")
        
        return self.results
    
    def optimize_confidence_threshold(self, historical_data: List[Dict],
                                     thresholds: List[int] = [50, 60, 70, 80]) -> List[Dict]:
        
        for threshold in thresholds:
            config = self.config_template.copy()
            config['signals']['min_confidence'] = threshold
            
            indicators = self.indicators_class(config)
            risk_manager = self.risk_manager_class(config)
            signal_generator = self.signal_generator_class(config, indicators, risk_manager)
            
            backtest = BacktestEngine(config, indicators, signal_generator, risk_manager)
            metrics = backtest.run_backtest(historical_data)
            
            self.results.append({
                'parameter': 'min_confidence',
                'value': threshold,
                'metrics': metrics
            })
            
            print(f"Confidence {threshold}%: Return {metrics['total_return_percent']:.2f}%, Win Rate {metrics['win_rate']:.2f}%")
        
        return self.results
    
    def get_best_parameters(self, metric: str = 'total_return_percent') -> Dict:
        if not self.results:
            return {}
        
        best = max(self.results, key=lambda x: x['metrics'].get(metric, 0))
        return best

