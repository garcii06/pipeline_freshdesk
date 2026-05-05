import logging
import os
from datetime import datetime

def get_logger(name):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        if not os.getenv('AIRFLOW_HOME'):
            os.makedirs('logs', exist_ok=True)
            log_filename = f"logs/pipeline_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_filename)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger