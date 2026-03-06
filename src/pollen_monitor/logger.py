import logging
import sys

def setup_logger(name="pollen_monitor"):
    logger = logging.getLogger(name)
    
    # Avoid duplicate logs if setup_logger is called multiple times
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 1. File Handler (Debug/History)
    file_handler = logging.FileHandler("pollen_system.log")
    file_handler.setFormatter(formatter)
    
    # 2. Console Handler (Standard Output)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create a singleton instance for easy import
logger = setup_logger()