import requests
import logging
from typing import Dict, Optional
from datetime import datetime
from app.utils import format_inr, format_percentage, get_env_var

logger = logging.getLogger(__name__)

class Alerter:
    def __init__(self, config, risk_manager=None):
        self.config = config
        self.alert_config = config['alerts']
        self.risk_manager = risk_manager
        
        self.discord_enabled = self.alert_config['discord']['enabled']
        self.telegram_enabled = self.alert_config['telegram']['enabled']
        
        if self.discord_enabled:
            webhook_var = self.alert_config['discord']['webhook_env_var']
            self.discord_webhook = get_env_var(webhook_var, required=False)
            if not self.discord_webhook:
                logger.warning(f"Discord enabled but {webhook_var} not set")
                self.discord_enabled = False
        
        if self.telegram_enabled:
            token_var = self.alert_config['telegram']['bot_token_env_var']
            chat_var = self.alert_config['telegram']['chat_id_env_var']
            self.telegram_token = get_env_var(token_var, required=False)
            self.telegram_chat_id = get_env_var(chat_var, required=False)
            if not self.telegram_token or not self.telegram_chat_id:
                logger.warning("Telegram enabled but credentials not set")
                self.telegram_enabled = False
    
    def send_entry_signal(self, signal: Dict, account_info: Optional[Dict] = None):
        if not self.alert_config['send_entry_signals']:
            return
        
        message = self._format_entry_signal(signal, account_info)
        self._send_alert(message, "signal")
    
    def send_exit_signal(self, symbol: str, exit_price: float, pnl: float, 
                        pnl_percent: float, reason: str):
        if not self.alert_config['send_exit_signals']:
            return
        
        message = self._format_exit_signal(symbol, exit_price, pnl, pnl_percent, reason)
        self._send_alert(message, "exit")
    
    def send_position_update(self, position: Dict, current_price: float, pnl: Dict):
        if not self.alert_config['send_position_updates']:
            return
        
        message = self._format_position_update(position, current_price, pnl)
        self._send_alert(message, "update")
    
    def send_daily_summary(self, summary: Dict):
        if not self.alert_config['send_daily_summary']:
            return
        
        message = self._format_daily_summary(summary)
        self._send_alert(message, "summary")
    
    def send_error_alert(self, error_message: str):
        message = f"⚠️ **SYSTEM ERROR**\n\n{error_message}"
        self._send_alert(message, "error")
    
    def send_startup_alert(self, total_coins: int):
        ist_time = datetime.now().strftime('%d %b %Y, %H:%M:%S IST')
        
        trading_hours = self.config.get('trading_hours', {})
        start_time = trading_hours.get('start_time', '11:00')
        end_time = trading_hours.get('end_time', '17:00')
        
        message = f"✅ **SYSTEM STARTED SUCCESSFULLY**\n\n"
        message += f"🕒 Time: {ist_time}\n"
        message += f"📊 Monitoring: {total_coins} futures pairs\n"
        message += f"⏰ Trading Hours: {start_time} - {end_time} IST\n"
        message += f"📈 Scan Interval: {self.config['scanner']['interval_seconds']} seconds\n"
        message += f"🎯 Min Confidence: {self.config['signals']['min_confidence']}%\n\n"
        message += f"Ready to send trading signals! 🚀"
        
        self._send_alert(message, "startup")
    
    def send_session_start_alert(self, total_coins: int, account_info: Optional[Dict] = None):
        ist_time = datetime.now().strftime('%H:%M:%S IST')
        
        message = f"🟢 **TRADING SESSION STARTED**\n\n"
        message += f"🕒 Time: {ist_time}\n"
        message += f"📊 Monitoring: {total_coins} futures pairs\n"
        message += f"🔍 Scan Frequency: Every {self.config['scanner']['interval_seconds']}s\n"
        message += f"📈 Signal Threshold: {self.config['signals']['min_confidence']}%+\n"
        message += f"🎯 Max Alerts per Scan: {self.config['signals']['max_alerts_per_scan']}\n\n"
        
        if account_info:
            message += f"💰 **YOUR ACCOUNT:**\n"
            message += f"Total Balance: {format_inr(account_info['total_balance'])}\n"
            message += f"Available Margin: {format_inr(account_info['available_margin'])}\n"
            message += f"Open Positions: {account_info['open_positions_count']}\n\n"
        
        message += f"Watching for high-probability setups... 👀"
        
        self._send_alert(message, "session_start")
    
    def send_session_end_alert(self, summary: Dict):
        ist_time = datetime.now().strftime('%H:%M:%S IST')
        
        message = f"🔴 **TRADING SESSION ENDED**\n\n"
        message += f"🕒 End Time: {ist_time}\n\n"
        
        message += f"📊 **Today's Summary:**\n"
        message += f"Signals Generated: {summary.get('total_signals', 0)}\n"
        
        if summary.get('total_signals', 0) > 0:
            message += f"Trades: {summary.get('trades_executed', 0)}\n"
            
            if summary.get('trades_executed', 0) > 0:
                win_rate = (summary.get('winning_trades', 0) / summary['trades_executed']) * 100
                message += f"Winners: {summary.get('winning_trades', 0)} | Losers: {summary.get('losing_trades', 0)}\n"
                message += f"Win Rate: {win_rate:.1f}%\n"
                message += f"P&L: {format_inr(summary.get('total_pnl', 0))}\n"
        else:
            message += f"No signals generated today.\n"
        
        trading_hours = self.config.get('trading_hours', {})
        start_time = trading_hours.get('start_time', '11:00')
        
        message += f"\n✅ Session complete. See you tomorrow at {start_time} IST!"
        
        self._send_alert(message, "session_end")
    
    def _format_entry_signal(self, signal: Dict, account_info: Optional[Dict]) -> str:
        direction_emoji = "🟢" if signal['direction'] == "LONG" else "🔴"
        direction_arrow = "↗️" if signal['direction'] == "LONG" else "↘️"
        
        if signal['confidence'] >= 90:
            confidence_level = "STRONG"
        elif signal['confidence'] >= 40:
            confidence_level = "MODERATE"
        else:
            confidence_level = "WEAK"
        
        entry_price = signal['entry_price']
        stop_loss = signal['stop_loss']
        targets = signal['targets']
        position_size = signal['position_size']
        leverage = signal['leverage']
        
        stop_loss_distance = abs(entry_price - stop_loss) / entry_price * 100
        
        if self.risk_manager:
            max_loss = self.risk_manager.calculate_max_loss(position_size, leverage, stop_loss_distance)
            target_1_profit = self.risk_manager.calculate_potential_profit(position_size, leverage, targets[0]['profit_percent'])
            target_2_profit = self.risk_manager.calculate_potential_profit(position_size, leverage, targets[1]['profit_percent']) if len(targets) > 1 else 0
        else:
            max_loss = position_size * leverage * (stop_loss_distance / 100)
            target_1_profit = position_size * leverage * (targets[0]['profit_percent'] / 100)
            target_2_profit = position_size * leverage * (targets[1]['profit_percent'] / 100) if len(targets) > 1 else 0
        
        risk_reward = targets[0]['profit_percent'] / stop_loss_distance if stop_loss_distance > 0 else 0
        
        message = f"🪙 **{signal['symbol']}INR PERPETUAL**\n"
        message += f"{direction_emoji} **{signal['direction']}** {direction_arrow} • {confidence_level} ({signal['confidence']}%)\n\n"
        
        message += f"📊 **ENTRY DETAILS:**\n"
        message += f"Entry Price: {format_inr(entry_price)}\n"
        message += f"Position Size: {format_inr(position_size)}\n"
        message += f"Leverage: {leverage}x → Exposure: {format_inr(position_size * leverage)}\n"
        message += f"Direction: **{signal['direction']}**\n\n"
        
        message += f"🎯 **TARGETS:**\n"
        net_t1_profit = target_1_profit * targets[0]['exit_percent'] / 100
        message += f"Target 1 ({targets[0]['exit_percent']}%): {format_inr(targets[0]['price'])} "
        message += f"({format_percentage(targets[0]['profit_percent'])} = {format_inr(net_t1_profit)} net)\n"
        if len(targets) > 1:
            net_t2_profit = target_2_profit * targets[1]['exit_percent'] / 100
            message += f"Target 2 ({targets[1]['exit_percent']}%): {format_inr(targets[1]['price'])} "
            message += f"({format_percentage(targets[1]['profit_percent'])} = {format_inr(net_t2_profit)} net)\n"
        
        if self.risk_manager and self.risk_manager.transaction_cost > 0:
            message += f"⚠️ _Fees ({self.risk_manager.transaction_cost}% GST) already deducted above_\n"
        message += "\n"
        
        message += f"🛡️ **PROTECTION:**\n"
        message += f"Stop Loss: {format_inr(stop_loss)} ({format_percentage(-stop_loss_distance)} = {format_inr(max_loss)} loss)\n"
        message += f"Risk:Reward = 1:{risk_reward:.1f} {'✓' if risk_reward >= 1.5 else '⚠️'}\n\n"
        
        message += f"📈 **SIGNALS:**\n"
        for reason in signal['reasons']:
            message += f"✓ {reason}\n"
        message += "\n"
        
        message += f"⏰ Valid for: 2 minutes | Time: {datetime.now().strftime('%H:%M:%S')} IST\n"
        
        if account_info:
            message += f"\n💰 **YOUR ACCOUNT:**\n"
            message += f"Available Margin: {format_inr(account_info['available_margin'])}\n"
            message += f"Current Positions: {account_info['open_positions_count']}/{self.config['risk']['max_concurrent_positions']}\n"
            if 'total_pnl' in account_info:
                message += f"Net P&L Today: {format_inr(account_info['total_pnl'])} ({format_percentage(account_info.get('pnl_percent', 0))})\n"
        
        return message
    
    def _format_exit_signal(self, symbol: str, exit_price: float, pnl: float, 
                           pnl_percent: float, reason: str) -> str:
        emoji = "🟢" if pnl >= 0 else "🔴"
        status = "✅ PROFIT" if pnl >= 0 else "❌ STOP LOSS"
        
        message = f"🪙 **{symbol}INR PERPETUAL**\n"
        message += f"{emoji} **EXIT** • {reason.upper()}\n\n"
        message += f"Exit Price: {format_inr(exit_price)}\n"
        message += f"P&L: {format_inr(pnl)} ({format_percentage(pnl_percent)})\n"
        message += f"Time: {datetime.now().strftime('%H:%M:%S')} IST\n"
        
        if pnl >= 0:
            message += "\n🎉 Profit secured!"
        else:
            message += "\n⚠️ Loss limited by stop loss"
        
        return message
    
    def _format_position_update(self, position: Dict, current_price: float, pnl: Dict) -> str:
        symbol = position['symbol']
        entry_price = position['entry_price']
        
        price_change = ((current_price - entry_price) / entry_price) * 100
        
        message = f"📊 **{symbol}INR - Position Update**\n\n"
        message += f"Entry: {format_inr(entry_price)}\n"
        message += f"Current: {format_inr(current_price)} ({format_percentage(price_change)})\n"
        message += f"Unrealized P&L: {format_inr(pnl['pnl_amount'])} ({format_percentage(pnl['pnl_percent'])})\n"
        
        return message
    
    def _format_daily_summary(self, summary: Dict) -> str:
        message = f"📊 **Daily Trading Summary - {datetime.now().strftime('%d %b %Y')}**\n\n"
        
        message += f"Signals Generated: {summary.get('total_signals', 0)}\n"
        message += f"Trades Executed: {summary.get('trades_executed', 0)}\n"
        
        if summary.get('trades_executed', 0) > 0:
            win_rate = (summary.get('winning_trades', 0) / summary['trades_executed']) * 100
            message += f"Winning Trades: {summary.get('winning_trades', 0)}\n"
            message += f"Losing Trades: {summary.get('losing_trades', 0)}\n"
            message += f"Win Rate: {win_rate:.1f}%\n\n"
            
            message += f"Total P&L: {format_inr(summary.get('total_pnl', 0))}\n"
            message += f"Best Trade: {format_inr(summary.get('best_trade', 0))}\n"
            message += f"Worst Trade: {format_inr(summary.get('worst_trade', 0))}\n"
        else:
            message += "\nNo trades executed today.\n"
        
        message += f"\n✅ Trading session complete.\n"
        message += f"See you tomorrow at 11:00 AM IST!"
        
        return message
    
    def _send_alert(self, message: str, alert_type: str = "general"):
        sent = False
        
        if self.discord_enabled:
            if self._send_discord(message):
                sent = True
        
        if self.telegram_enabled:
            if self._send_telegram(message):
                sent = True
        
        if not sent:
            logger.warning(f"Alert not sent (no channels configured): {alert_type}")
            print(f"\n{'='*60}")
            print(message)
            print('='*60)
    
    def _send_discord(self, message: str) -> bool:
        try:
            separator = "─" * 50
            formatted_message = f"{separator}\n{message}\n{separator}"
            
            payload = {"content": formatted_message}
            response = requests.post(
                self.discord_webhook, 
                json=payload, 
                timeout=10
            )
            response.raise_for_status()
            logger.debug("Discord alert sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False
    
    def _send_telegram(self, message: str) -> bool:
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.debug("Telegram alert sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

