
################################################################################
import logging 
import asyncio
from .SPARK_Manager import spark_mgr
from .globals import db_handler, db_handler_cat3, KEEP_POLLING
from .config import EventManagerConfig


cfg = EventManagerConfig()

# Create a global alert queue
alert_queue = asyncio.Queue()



async def add_event(event):
    #Add Event to Queue
    
    await alert_queue.put(event)
    logger.info(f"Event added: {event}")

async def data_polling_processing():
    #Process to look for new events being stored
    

    logger.info(f'Starting Data Polling Processing for given sources '
                f'{cfg.CAT3_POLL_LIST} polling for new events every '
                f'{cfg.CAT3_POLL_RATE} seconds')

    while KEEP_POLLING:
        for src in cfg.CAT3_POLL_LIST:
            new_events = db_handler_cat3.find_new_events(src)
            
            for event in new_events:
                logger.info(f'New CAT3 event from {src}: {event.__dict__}')
                #Format New Event Message to send to SPARK
                new_event_msg = {'scid': event.scid, 
                                'start_time': event.event_time,  
                                'metric': event.event_name, 
                                'source': event.event_src, 
                                'job_id': event.unique_index*-1, 
                                'endpoint': SPARK_ENDPOINT}

                #Send Job to SPARK
                try:
                    #Update SPARK Report ID with temporary value
                    db_handler_cat3.update_column_by_id(event.unique_index,
                                                        'spark_report_id',
                                                        event.unique_index*-1)
                    spark_mgr(cfg.SPARK_URI,new_event_msg)
                except Exception as e:
                    logger.error(f'Issue with SPARK Manager: {e}')

        await asyncio.sleep(cfg.CAT3_POLL_RATE)

#Function to process data in the queue 
async def data_ingestion_processing():
    #Constant Loop to check the queue for new events

    logger.info(f'Starting Data Ingestion Processing')
    while True:    
        data_2_insert = await alert_queue.get()
        if data_2_insert is None : 
            
            logger.info('Application is closing, shutting down thread')
            break
        elif data_2_insert.event_name.lower() == "heartbeat":
            logger.info(f'Storing {data_2_insert.source} '
                        f'Heartbeat Data for SCID {data_2_insert.scid}')

            try:
                db_handler.store_heartbeat(data_2_insert)
            except Exception as e:
                logger.error(
                    f'Issues storing {data_2_insert.event_src} '
                    f'Heartbeat Data for SCID {data_2_insert.scid} due to {e}')
        else:
            #Store Data into database and send jobs to SPARK
            try:
                logger.info(f'Storing {data_2_insert}')
                
                #Store new event in Database
                unique_index = db_handler.store_data(data_2_insert)

                #Format New Event Message to send to SPARK
                new_event_msg = {'scid': data_2_insert.scid, 
                                'start_time': data_2_insert.event_time,  
                                'metric': data_2_insert.event_name, 
                                'source': data_2_insert.event_src, 
                                'job_id': unique_index, 
                                'endpoint': SPARK_ENDPOINT}
                #Send Job to SPARK
                spark_mgr(cfg.SPARK_URI,new_event_msg)

        
            except Exception as e:
                logger.error(
                    f'Issues with Storing {data_2_insert} : {e}')


        
def start_tasks():

    #Create Logging Capability
    global logger, SPARK_ENDPOINT

    logger = logging.getLogger(__name__)   

    SPARK_ENDPOINT = rf'http://{cfg.IP}:{cfg.PORT}/spark_endpoint'
    
    try:
        db_handler.initialize_database(create_flg=True, cat3db_flg=False)
        db_handler_cat3.initialize_database(create_flg=False, cat3db_flg=True)

    except Exception as e:
        logger.error(f"Issues with initializing databases: {e}")
        exit()
    
    #Start background tasks
    asyncio.create_task(data_ingestion_processing())
    asyncio.create_task(data_polling_processing())
    



