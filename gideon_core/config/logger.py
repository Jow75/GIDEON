import logging
import sys

def setup_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Creates and configures a structured logger.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
    return logger

# Create a root logger for the application
root_logger = setup_logger("gideon", "INFO")
