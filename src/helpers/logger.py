import logging
import os
from pathlib import Path
import yaml


# Ensure the logs directory exists
logs_dir = Path.cwd() / 'logs'
if not logs_dir.exists():
    logs_dir.mkdir(parents=True)
    
# Load logging configuration from YAML file
# Define the path to the logging configuration file
config_path = Path.cwd() / 'src' / 'config' / 'logging_config.yaml'
# Load logging configuration from the YAML file
with config_path.open('r') as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

# Create logger instance
logger = logging.getLogger('app')

def init():
    # Set the log level from environment variable
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(log_level)
