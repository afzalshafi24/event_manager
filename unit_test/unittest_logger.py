
import os
import os
import logging
from logging.handlers import RotatingFileHandler 
from pathlib import Path
from datetime import datetime
#Initialize Logging
#Check to see if logging path exist , if not make one
if not os.path.exists('logs'):
    os.makedirs('logs')

date_tag = datetime.now().strftime('%Y%m%d%H%M%S')
log_name = Path(os.path.join('logs', 
                             f'unit_test{date_tag}.log'))


# Configure logging
log_handler = RotatingFileHandler(log_name.as_posix(), 
                                  maxBytes=10*1024*1024, 
                                  backupCount=5)
(log_handler
 .setFormatter(logging.
               Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s ' 
                         '- %(message)s')))

logging.basicConfig(level=logging.INFO, handlers=[log_handler, 
                                                  logging.StreamHandler()])


logger = logging.getLogger(__name__)


