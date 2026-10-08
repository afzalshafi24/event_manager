

#ECQL emulator to process batch scripts 
import pandas as pd
import subprocess
from time import sleep
from datetime import datetime
import sys
import random 
from numpy import isnan
import os
import json
import logging 
from pathlib import Path
from logging.handlers import RotatingFileHandler
import datetime
from pydantic import BaseModel
from typing import Optional
from .oracle_db_params import USERNAME, PASSWORD, HOST, PORT, SERVICE_NAME


from .src.db_driver import DB_Handler



LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
LOG_FILENAME = "ecql_emulator.log"
DB_URL = (f'oracle+cx_oracle://{USERNAME}:{PASSWORD}@{HOST}:{PORT}'
          f'/?service_name={SERVICE_NAME}')

SLEEP_RANGE = [10,60]

#Check to see if logging path exist , if not make one
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_name = Path(os.path.join(LOG_DIR, LOG_FILENAME))

# Configure logging
log_handler = RotatingFileHandler(log_name.as_posix(), maxBytes=10*1024*1024,
                                   backupCount=5)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - '
                                           '%(levelname)s - %(message)s'))

logging.basicConfig(level=logging.INFO,
                     handlers=[log_handler, logging.StreamHandler()])
logger = logging.getLogger(__name__)



#Config and initialize Database
logger.info(f'Using Database: {DB_URL}')
db_handler = DB_Handler(DB_URL)
    
# Define a Pydantic model for the request body for Event Alerts
class Event_Request(BaseModel):
    unique_index: int
    scid: int
    event_time: str
    event_rule_id: int
    event_name: str
    event_rule: str
    event_src: str
    spark_script: Optional[str]
    gem_full_path: Optional[str]
    
def add_ecql_event(scid, event_idx, event_name, event_rule):

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the date and time
    event_time = now.strftime("%Y-%m-%d %H:%M:%S")
    #Module to add event data to database
    latest_entry = db_handler.get_latest_entry()
    #Check if there are entries, but not set latest_id to 0
    
    if not latest_entry is None:
        latest_id = latest_entry.unique_index
    else:
        latest_id = 1
    
    new_event = Event_Request(unique_index= latest_id+1,
                                scid=scid,
                                event_time=event_time,
                                event_rule_id=event_idx,
                                event_name=event_name,
                                event_rule = event_rule,
                                event_src='ecql',
                                spark_script='',
                                gem_full_path='C:\\vcid.pgem')
    
    logger.info(f'Adding ECQL New Event {new_event}')
    
    #Store data in database
    db_handler.store_data(new_event)

def main(ecql_cfg, scid): 
    #Extract data from cfg_data
    cfg_data = pd.read_csv(ecql_cfg, delimiter=';')
    num_of_events = len(cfg_data['#Event_Name'])    
    
    while True:
        #Generate random sleep time
        sleep_time = random.randint(SLEEP_RANGE[0],SLEEP_RANGE[1])
        
        #Get Random Batch Script to run
        event_idx = random.randint(0, num_of_events-1)
        event_name=cfg_data['#Event_Name'][event_idx]
        event_rule = cfg_data['#EventRule'][event_idx]

        add_ecql_event(scid, event_idx, event_name, event_rule)

        sleep(sleep_time)


if __name__ == "__main__":
    
    #get inputs
    ecql_cfg = sys.argv[1]
    scid = sys.argv[2]

    #Start ECQL Emulator
    main(ecql_cfg, scid)




