import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
import pytz

from app.utils import load_config, setup_logging, load_futures_coins, is_trading_hours, get_current_trading_period, get_env_var
from app.scanner import PriceScanner
from app.indicators import TechnicalIndicators
from app.signal_generator import SignalGenerator
from app.risk_manager import RiskManager
from app.account_manager import AccountManager
from app.alerter import Alerter

logger = None
config = None
scanner = None
indicators = None
signal_generator = None
risk_manager = None
account_manager = None
alerter = None

trading_active = False
current_period_name = None
daily_stats = {
    'total_signals': 0,
    'trades_executed': 0,
    'winning_trades': 0,
    'losing_trades': 0,
    'total_pnl': 0,
    'best_trade': 0,
    'worst_trade': 0
}

def initialize_system():
    global logger, config, scanner, indicators, signal_generator, risk_manager, account_manager, alerter
    
    try:
        config = load_config()
        logger = setup_logging(config)
        
        logger.info("="*60)
        logger.info("CoinDCX Futures Trading Signal System")
        logger.info("="*60)
        logger.info(f"Mode: {config['mode'].upper()}")
        
        trading_hours = config.get('trading_hours', {})
        periods = trading_hours.get('periods')
        if periods:
            logger.info("Trading Periods:")
            for period in periods:
                logger.info(f"  - {period['name'].upper()}: {period['start_time']} - {period['end_time']} IST (min conf: {period['min_confidence']}%, max alerts: {period['max_alerts_per_scan']})")
        else:
            logger.info(f"Trading Hours: {trading_hours.get('start_time', 'N/A')} - {trading_hours.get('end_time', 'N/A')} IST")
        
        scanner = PriceScanner(config)
        indicators = TechnicalIndicators(config)
        risk_manager = RiskManager(config)
        signal_generator = SignalGenerator(config, indicators, risk_manager)
        alerter = Alerter(config, risk_manager)
        
        if config['mode'] == 'personalized' and config['personalized']['enabled']:
            api_key = get_env_var('COINDCX_API_KEY', required=False)
            api_secret = get_env_var('COINDCX_API_SECRET', required=False)
            
            if api_key and api_secret:
                account_manager = AccountManager(config, api_key, api_secret)
                logger.info("Personalized mode enabled with API integration")
            else:
                logger.warning("Personalized mode requested but API keys not found, using generic mode")
        
        logger.info("System initialized successfully")
        logger.info("="*60)
        
        try:
            coins = load_futures_coins(config['scanner']['coins_file'])
            alerter.send_startup_alert(len(coins))
        except Exception as e:
            logger.warning(f"Could not send startup alert: {e}")
        
        return True
        
    except Exception as e:
        if logger:
            logger.error(f"Failed to initialize system: {e}")
        else:
            print(f"Failed to initialize system: {e}")
        return False

def start_trading_session():
    global trading_active, daily_stats, current_period_name
    
    logger.info("Starting trading session...")
    trading_active = True
    current_period_name = None
    daily_stats = {
        'total_signals': 0,
        'trades_executed': 0,
        'winning_trades': 0,
        'losing_trades': 0,
        'total_pnl': 0,
        'best_trade': 0,
        'worst_trade': 0
    }
    
    try:
        coins = load_futures_coins(config['scanner']['coins_file'])
        logger.info(f"Loaded {len(coins)} futures coins to monitor")
        
        account_info = None
        if account_manager:
            account_manager.refresh_account_data()
            account_info = account_manager.get_account_summary()
            logger.info(f"Account Balance: ₹{account_info['total_balance']:.2f}")
            logger.info(f"Available Margin: ₹{account_info['available_margin']:.2f}")
        
        alerter.send_session_start_alert(len(coins), account_info)
        
    except Exception as e:
        logger.error(f"Error starting trading session: {e}")
        alerter.send_error_alert(f"Failed to start trading session: {e}")

def stop_trading_session():
    global trading_active
    
    logger.info("Stopping trading session...")
    trading_active = False
    
    try:
        alerter.send_session_end_alert(daily_stats)
        logger.info(f"Daily Summary - Signals: {daily_stats['total_signals']}, Trades: {daily_stats['trades_executed']}")
        
    except Exception as e:
        logger.error(f"Error stopping trading session: {e}")
    
    logger.info("Trading session stopped. System idle until next trading day.")

def scan_and_signal():
    global current_period_name
    
    if not trading_active:
        return
    
    if config['mode'] == 'generic':
        expiry_minutes = config['risk'].get('position_expiry_minutes', 5)
        risk_manager.cleanup_expired_positions(max_age_minutes=expiry_minutes)
    
    is_trading, current_period = get_current_trading_period(config)
    if not is_trading:
        return
    
    if current_period:
        period_name = current_period.get('name', 'default')
        min_confidence = current_period.get('min_confidence')
        max_alerts = current_period.get('max_alerts_per_scan')
        
        if current_period_name is not None and current_period_name != period_name:
            logger.info(f"Period changed: {current_period_name} → {period_name}")
            trading_hours = config.get('trading_hours', {})
            periods = trading_hours.get('periods', [])
            old_period = next((p for p in periods if p['name'] == current_period_name), None)
            if old_period:
                try:
                    alerter.send_period_change_alert(old_period, current_period)
                except Exception as e:
                    logger.warning(f"Failed to send period change alert: {e}")
        
        current_period_name = period_name
    else:
        period_name = 'default'
        min_confidence = config.get('signals', {}).get('min_confidence', 60)
        max_alerts = config.get('signals', {}).get('max_alerts_per_scan', 3)
    
    try:
        from app.utils import get_ist_time
        current_time_str = get_ist_time().strftime('%H:%M:%S')
        
        logger.info("="*60)
        logger.info(f"[{current_time_str}] Starting scan cycle ({period_name.upper()} period - min confidence: {min_confidence}%, max alerts: {max_alerts})...")
        
        coins = load_futures_coins(config['scanner']['coins_file'])
        logger.info(f"Loaded {len(coins)} futures pairs to scan")
        
        logger.info("Fetching price data from CoinDCX API...")
        price_data_batch = scanner.get_bulk_price_data(coins)
        
        if not price_data_batch:
            logger.warning("No price data received from API - skipping this cycle")
            return
        
        logger.info(f"Received data for {len(price_data_batch)} coins")
        
        coins_with_history = 0
        coins_analyzed = 0
        signals = []
        history_status = {}
        
        for coin_symbol, price_data in price_data_batch.items():
            current_history = len(scanner.get_price_history(coin_symbol))
            
            if current_history < 20:
                if coin_symbol in ['BTC', 'ETH', 'SOL', 'BNB', 'XRP']:
                    history_status[coin_symbol] = current_history
                continue
            
            coins_with_history += 1
            
            price_history = scanner.get_price_history(coin_symbol)
            volume_history = scanner.get_volume_history(coin_symbol)
            
            analysis = indicators.analyze_coin(
                price_history,
                price_data['volume'],
                volume_history
            )
            
            if analysis.get('has_data'):
                coins_analyzed += 1
            
            signal = signal_generator.generate_signal(coin_symbol, price_data, analysis, min_confidence=min_confidence)
            
            if signal:
                signals.append(signal)
                logger.info(f"  ✓ Signal found: {coin_symbol} ({signal['direction']}, {signal['confidence']}% confidence)")
        
        if history_status and coins_with_history == 0:
            status_str = ", ".join([f"{coin}:{count}/20" for coin, count in list(history_status.items())[:5]])
            logger.info(f"Building price history... Sample: {status_str}")
            logger.info(f"⏳ Need 20 data points per coin (currently at scan #{list(history_status.values())[0]}/20)")
            logger.info(f"⏰ Estimated time to first analysis: {(20 - list(history_status.values())[0]) * 5} seconds")
        
        logger.info(f"Analysis complete: {coins_analyzed}/{len(price_data_batch)} coins analyzed, {coins_with_history} with sufficient history")
        
        if signals:
            logger.info(f"Found {len(signals)} potential signals")
            top_signals = signal_generator.filter_top_signals(signals, max_alerts=max_alerts)
            
            logger.info(f"Sending top {len(top_signals)} signals ({period_name.upper()} period):")
            
            for signal in top_signals:
                daily_stats['total_signals'] += 1
                
                logger.info(f"  Processing: {signal['symbol']} - Confidence {signal['confidence']}%")
                
                account_info = None
                if account_manager:
                    logger.info(f"    Checking account margin...")
                    account_manager.refresh_account_data()
                    account_info = account_manager.get_account_summary()
                    
                    adjusted_size = account_manager.calculate_dynamic_position_size(
                        signal['entry_price'],
                        signal['stop_loss'],
                        signal['position_size']
                    )
                    signal['position_size'] = adjusted_size
                    logger.info(f"    Adjusted position size: ₹{adjusted_size:.2f}")
                    
                    can_trade, reason = account_manager.can_open_position(signal['position_size'])
                    if not can_trade:
                        logger.warning(f"    ❌ Blocked: {reason}")
                        continue
                
                can_open, reason = risk_manager.can_open_position()
                if not can_open:
                    logger.warning(f"    ❌ Risk manager blocked: {reason}")
                    continue
                
                logger.info(f"    ✓ Sending alert to Discord...")
                alerter.send_entry_signal(signal, account_info)
                risk_manager.add_position(signal)
                
                logger.info(f"  ✅ Signal sent: {signal['symbol']} {signal['direction']} at ₹{signal['entry_price']:.2f}")
            
            logger.info(f"Scan complete - {len(top_signals)} signals sent")
        else:
            logger.info("No signals generated this cycle (waiting for high-probability setups...)")
        
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Error in scan_and_signal: {e}", exc_info=True)

def main():
    if not initialize_system():
        logger.error("System initialization failed, exiting")
        sys.exit(1)
    
    ist = pytz.timezone(config['trading_hours']['timezone'])
    scheduler = BlockingScheduler(timezone=ist)
    
    trading_hours = config.get('trading_hours', {})
    periods = trading_hours.get('periods')
    
    if periods:
        first_period_start = periods[0]['start_time']
        last_period_end = periods[-1]['end_time']
        start_time_parts = first_period_start.split(':')
        end_time_parts = last_period_end.split(':')
    else:
        start_time_parts = trading_hours['start_time'].split(':')
        end_time_parts = trading_hours['end_time'].split(':')
    
    start_hour = int(start_time_parts[0])
    start_minute = int(start_time_parts[1])
    end_hour = int(end_time_parts[0])
    end_minute = int(end_time_parts[1])
    
    days_list = trading_hours.get('days', ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
    days_map = {'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed', 'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun'}
    days = ','.join([days_map.get(day, day[:3]) for day in days_list])
    
    scheduler.add_job(
        start_trading_session,
        'cron',
        hour=start_hour,
        minute=start_minute,
        day_of_week=days,
        id='start_session'
    )
    
    scheduler.add_job(
        stop_trading_session,
        'cron',
        hour=end_hour,
        minute=end_minute,
        day_of_week=days,
        id='stop_session'
    )
    
    scan_interval = config['scanner']['interval_seconds']
    scheduler.add_job(
        scan_and_signal,
        'interval',
        seconds=scan_interval,
        id='scanner'
    )
    
    logger.info("Scheduler configured:")
    if periods:
        logger.info(f"  - Trading session starts: {periods[0]['start_time']} IST (first period)")
        logger.info(f"  - Trading session ends: {periods[-1]['end_time']} IST (last period)")
    else:
        logger.info(f"  - Trading session starts: {trading_hours['start_time']} IST")
        logger.info(f"  - Trading session ends: {trading_hours['end_time']} IST")
    logger.info(f"  - Scan interval: {scan_interval} seconds")
    logger.info(f"  - Active days: {', '.join([day.capitalize() for day in days_list])}")
    
    if is_trading_hours(config):
        logger.info("Currently in trading hours, starting session now...")
        start_trading_session()
    else:
        logger.info("Outside trading hours, waiting for next session...")
    
    try:
        logger.info("System running... Press Ctrl+C to stop")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down gracefully...")
        if trading_active:
            stop_trading_session()

if __name__ == "__main__":
    main()

