
import logging 
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

#EventManager_API Local Imports
from src.config import EventManagerConfig


#Load Config
config = EventManagerConfig()

#Initialize Logging
#Check to see if logging path exist, if not make one
if not os.path.exists('logs'):
    os.makedirs('logs')

log_name = Path(os.path.join('logs', 'event_mgr_api.log'))

# Configure logging
log_handler = RotatingFileHandler(log_name.as_posix(), maxBytes=10*1024*1024, 
                                  backupCount=5)
log_handler.setFormatter(logging
                         .Formatter('%(asctime)s - '
                                    '%(name)s - '
                                    '%(levelname)s - '
                                    '%(funcName)s - '
                                    '%(message)s'))



#Set Log Level
try:
    logging.basicConfig(
                        level=config.log_level_mapping[config.LOG_LEVEL], 
                        handlers=[log_handler, 
                                logging.StreamHandler()])
except:
    logging.basicConfig(level=logging.INFO, 
                        handlers=[log_handler, 
                                logging.StreamHandler()])


logger = logging.getLogger(__name__)
logger.info(f'Using Config File {config.cfg_file}')

