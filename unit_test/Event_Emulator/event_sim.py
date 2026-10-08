#ECQL emulator to process batch scripts 
import datetime
import requests
import sys
from random import choice as pick_rand
from time import sleep
import logging
from .event_sim_cfg import scids, event_names, event_srcs, spark_scripts   


logger = logging.getLogger(__name__)


def send_event_request(uri, manual_request = None):
    # Get the current date and time
    now = datetime.datetime.now()
    event_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # Format the date and time
    if manual_request is None:
        scid = pick_rand(scids)
        event_name = pick_rand(event_names)
        event_src = pick_rand(event_srcs)
        spark_script = pick_rand(spark_scripts)
    else:
        scid = manual_request['scid']
        event_name = manual_request['event_name']
        event_src = manual_request['event_src']
        spark_script = manual_request['spark_script']

    logger.info(f'Sending POST Request with scid = {scid},' 
                f'event_time = {event_time},'
                f'event_name = {event_name}, event_src = {event_src},'
                f'spark_script = {spark_script}')
    
    response = requests.post(uri, 
                                json={'scid': scid,
                                      'event_time': event_time,  
                                      'event_rule_id': 1,
                                      'event_name': event_name,
                                      'event_rule': '3 > threshold',
                                      'event_src': event_src,
                                      'spark_script': spark_script,
                                      'spark_report_id': None,
                                      'gem_full_path': r'C:/vcid.pgem'})
    
    return response
def main(uri):
    #Body of Event Simulator

    while True:
        #Send POST Request to EventManager_API
        send_event_request(uri)    
        sleep(30)

if __name__ == "__main__":

    uri = sys.argv[1]
    main(uri)




