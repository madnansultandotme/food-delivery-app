import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger(app):
    """Setup application logging"""
    
    # Create logs directory
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Remove default handler
    app.logger.handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/courier_app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/courier_app_errors.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Add handlers
    app.logger.addHandler(console_handler)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.setLevel(logging.DEBUG)
    
    return app.logger

def get_logger(name):
    """Get logger instance"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    return logger
