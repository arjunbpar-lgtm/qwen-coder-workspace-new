"""
Logger utility for the Sales Ledger Generator.

Provides centralized logging with file and console handlers,
plus UI integration for displaying logs in the application.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class AppLogger:
    """
    Centralized logging system for the application.
    
    Features:
    - File logging with daily rotation
    - Console logging
    - In-memory log buffer for UI display
    - Thread-safe operations
    """
    
    _instance: Optional['AppLogger'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.logger = logging.getLogger('SalesLedgerApp')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create logs directory
        logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # File handler with date-based naming
        log_file = os.path.join(
            logs_dir, 
            f'app_log_{datetime.now().strftime("%Y%m%d")}.txt'
        )
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # In-memory buffer for UI (last 1000 messages)
        self.log_buffer = []
        self.max_buffer_size = 1000
        
        # Add custom handler for UI buffer
        self.ui_handler = logging.Handler()
        self.ui_handler.setLevel(logging.DEBUG)
        self.ui_handler.emit = self._add_to_buffer
        self.ui_handler.setFormatter(formatter)
        self.logger.addHandler(self.ui_handler)
        
        self.info("Application logger initialized")
    
    def _add_to_buffer(self, record):
        """Add log record to UI buffer."""
        message = self.ui_handler.format(record)
        self.log_buffer.append(message)
        
        # Trim buffer if too large
        if len(self.log_buffer) > self.max_buffer_size:
            self.log_buffer = self.log_buffer[-self.max_buffer_size:]
    
    def get_logs(self, limit: int = 100) -> list:
        """Get recent log entries."""
        return self.log_buffer[-limit:]
    
    def clear_logs(self):
        """Clear the UI log buffer."""
        self.log_buffer.clear()
        self.info("Log buffer cleared")
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
    
    def export_logs(self, filepath: str):
        """Export all logs to a file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.log_buffer))
            self.info(f"Logs exported to {filepath}")
            return True
        except Exception as e:
            self.error(f"Failed to export logs: {e}")
            return False


# Global logger instance
def get_logger() -> AppLogger:
    """Get the global logger instance."""
    return AppLogger()
