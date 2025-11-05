import requests
import logging
from typing import Dict, Optional
from datetime import datetime
from app.utils import format_inr, format_percentage, format_price, get_env_var

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
        periods = trading_hours.get('periods')
        
        message = f"✅ **SYSTEM STARTED SUCCESSFULLY**\n\n"
        message += f"🕒 Time: {ist_time}\n"
        message += f"📊 Monitoring: {total_coins} futures pairs\n"
        
        if periods:
            message += f"⏰ **Trading Periods:**\n"
            for period in periods:
                message += f"  • {period['name'].upper()}: {period['start_time']} - {period['end_time']} IST\n"
                message += f"    (min conf: {period['min_confidence']}%, max alerts: {period['max_alerts_per_scan']})\n"
        else:
            start_time = trading_hours.get('start_time', '11:00')
            end_time = trading_hours.get('end_time', '17:00')
            message += f"⏰ Trading Hours: {start_time} - {end_time} IST\n"
            message += f"🎯 Min Confidence: {self.config['signals']['min_confidence']}%\n"
        
        message += f"\n📈 Scan Interval: {self.config['scanner']['interval_seconds']} seconds\n"
        message += f"Ready to send trading signals! 🚀"
        
        self._send_alert(message, "startup")
    
    def send_session_start_alert(self, total_coins: int, account_info: Optional[Dict] = None):
        ist_time = datetime.now().strftime('%I:%M:%S %p IST')
        
        trading_hours = self.config.get('trading_hours', {})
        periods = trading_hours.get('periods')
        
        message = f"🟢 **TRADING SESSION STARTED**\n\n"
        message += f"🕒 Time: {ist_time}\n"
        message += f"📊 Monitoring: {total_coins} futures pairs\n"
        message += f"🔍 Scan Frequency: Every {self.config['scanner']['interval_seconds']}s\n"
        
        if periods:
            message += f"\n⏰ **Active Periods Today:**\n"
            for period in periods:
                message += f"  • {period['name'].upper()}: {period['start_time']}-{period['end_time']} (conf: {period['min_confidence']}%+, alerts: {period['max_alerts_per_scan']})\n"
        else:
            message += f"📈 Signal Threshold: {self.config['signals']['min_confidence']}%+\n"
            message += f"🎯 Max Alerts per Scan: {self.config['signals']['max_alerts_per_scan']}\n"
        
        message += "\n"
        
        if account_info:
            message += f"💰 **YOUR ACCOUNT:**\n"
            message += f"Total Balance: {format_inr(account_info['total_balance'])}\n"
            message += f"Available Margin: {format_inr(account_info['available_margin'])}\n"
            message += f"Open Positions: {account_info['open_positions_count']}\n\n"
        
        message += f"Watching for high-probability setups... 👀"
        
        self._send_alert(message, "session_start")
    
    def send_session_end_alert(self, summary: Dict):
        ist_time = datetime.now().strftime('%I:%M:%S %p IST')
        
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
        periods = trading_hours.get('periods')
        if periods:
            start_time = periods[0]['start_time']
        else:
            start_time = trading_hours.get('start_time', '11:00')
        
        message += f"\n✅ Session complete. See you tomorrow at {start_time} IST!"
        
        self._send_alert(message, "session_end")
    
    def send_period_change_alert(self, old_period: Dict, new_period: Dict):
        ist_time = datetime.now().strftime('%I:%M:%S %p IST')
        
        old_name = old_period.get('name', 'unknown').upper()
        new_name = new_period.get('name', 'unknown').upper()
        
        emoji = "🌅" if new_name == "ACTIVE" else "🌙"
        
        message = f"{emoji} **PERIOD CHANGE**\n\n"
        message += f"🕒 Time: {ist_time}\n"
        message += f"📊 Switching: {old_name} → {new_name}\n\n"
        
        message += f"**{new_name} Period Settings:**\n"
        message += f"⏰ Duration: {new_period['start_time']} - {new_period['end_time']} IST\n"
        message += f"🎯 Min Confidence: {new_period['min_confidence']}%\n"
        message += f"📈 Max Alerts/Scan: {new_period['max_alerts_per_scan']}\n\n"
        
        if new_name == "PASSIVE":
            message += f"🌙 Now in selective mode - only high-quality signals (80%+)"
        else:
            message += f"🌅 Now in active mode - more frequent signals (60%+)"
        
        self._send_alert(message, "period_change")
    
    def _format_entry_signal(self, signal: Dict, account_info: Optional[Dict]) -> str:
        direction_emoji = "🟢" if signal['direction'] == "LONG" else "🔴"
        direction_arrow = "↗️" if signal['direction'] == "LONG" else "↘️"
        
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
        
        roe_t1 = (target_1_profit / position_size) * 100
        roe_t2 = (target_2_profit / position_size) * 100 if len(targets) > 1 else 0
        roe_sl = -(max_loss / position_size) * 100
        
        from datetime import timedelta
        entry_time = datetime.now()
        
        target_distance = targets[1]['profit_percent'] if len(targets) > 1 else targets[0]['profit_percent']
        
        momentum = signal.get('analysis', {}).get('momentum', {})
        recent_change = abs(momentum.get('change_percent', 0.5))
        
        if recent_change > 0:
            estimated_minutes = (target_distance / recent_change) * 2
        else:
            estimated_minutes = target_distance / 0.4
        
        strategy_min_minutes = self.config['risk'].get('min_hold_minutes', 2)
        
        hold_minutes = max(strategy_min_minutes, round(estimated_minutes))
        
        exit_time = entry_time + timedelta(minutes=hold_minutes)
        
        separator = "─" * 20
        
        message = f"{separator}\n"
        message += f"{direction_emoji} **{signal['symbol']}** {signal['direction']} {direction_arrow} • {signal['confidence']:.2f}%\n"
        message += f"⏰ **IN:** {entry_time.strftime('%I:%M:%S %p')} | **OUT:** {exit_time.strftime('%I:%M:%S %p')}\n"
        message += f"⏱️ **Hold:** {hold_minutes}min\n\n"
        
        message += f"**ENTRY:** {format_price(entry_price)}\n"
        message += f"**SIZE:** {format_inr(position_size)} @ {leverage}x\n\n"
        
        message += f"🎯 **TP1:** ROE +{roe_t1:.1f}% → {format_inr(target_1_profit * 0.5)}\n"
        message += f"🎯 **TP2:** ROE +{roe_t2:.1f}% → {format_inr(target_2_profit * 0.5)}\n"
        message += f"🛡️ **SL:** ROE {roe_sl:.1f}% → {format_inr(max_loss)}\n\n"
        
        message += f"📊 **SIGNALS:**\n"
        for reason in signal['reasons']:
            message += f"✓ {reason}\n"
        
        message += f"{separator}"
        
        return message
    
    def _format_exit_signal(self, symbol: str, exit_price: float, pnl: float, 
                           pnl_percent: float, reason: str) -> str:
        emoji = "🟢" if pnl >= 0 else "🔴"
        status = "✅ PROFIT" if pnl >= 0 else "❌ STOP LOSS"
        
        message = f"🪙 **{symbol}INR PERPETUAL**\n"
        message += f"{emoji} **EXIT** • {reason.upper()}\n\n"
        message += f"Exit Price: {format_inr(exit_price)}\n"
        message += f"P&L: {format_inr(pnl)} ({format_percentage(pnl_percent)})\n"
        message += f"Time: {datetime.now().strftime('%I:%M:%S %p')} IST\n"
        
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
    
    def send_custom_message(self, title: str, description: str, fields: list, color: int = 0x3498db):
        """Send a custom embedded message (Discord rich embed)"""
        sent = False
        
        if self.discord_enabled:
            if self._send_discord_embed(title, description, fields, color):
                sent = True
        
        if self.telegram_enabled:
            # Fallback to simple message for Telegram
            message = f"**{title}**\n\n{description}\n\n"
            for field in fields:
                message += f"{field['name']}: {field['value']}\n"
            if self._send_telegram(message):
                sent = True
        
        if not sent:
            logger.warning(f"Custom message not sent (no channels configured): {title}")
            print(f"\n{'='*60}")
            print(f"{title}\n{description}")
            for field in fields:
                print(f"{field['name']}: {field['value']}")
            print('='*60)
    
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
            payload = {"content": message}
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
    
    def _send_discord_embed(self, title: str, description: str, fields: list, color: int) -> bool:
        """Send a rich embedded message to Discord"""
        try:
            embed = {
                "title": title,
                "description": description,
                "color": color,
                "fields": fields,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            payload = {"embeds": [embed]}
            response = requests.post(
                self.discord_webhook,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.debug("Discord embed sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Discord embed: {e}")
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

