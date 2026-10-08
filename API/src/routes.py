
import logging
from fastapi import APIRouter
import asyncio
from .globals import db_handler, db_handler_cat3
from .models import EventRequest, SparkRequest
from .config import EventManagerConfig
from .utils import add_event, start_tasks


cfg = EventManagerConfig()
EUREKA_FLG = cfg.EUREKA_FLG

event_mgr_router = APIRouter()

@event_mgr_router.on_event("startup")
async def startup_event():
    #Create Logging Capability
    global logger

    logger = logging.getLogger(__name__)

    

    # Start the event processing tasks in the background
    start_tasks()
    logger.info('Startup Complete')

#Create a root endpoint EventManager
@event_mgr_router.get("/api")
async def read_root() -> dict:
    return {"message": "Welcome to the Event_Manager_API"}

# Define a POST endpoint for Event Submission
@event_mgr_router.post("/event/submit")
async def store_metric_alert(metric_data: EventRequest) -> dict: 
    '''
    Post Request to insert event into database
    Inputs:
        Post Request Message in JSON with the following fields:
        scid: int
        event_time: str
        event_rule_id: int
        event_name: str
        event_rule: str
        event_src: str
        spark_script: Optional[str]
        gem_full_path: Optional[str]
    Outputs:
        Dictionary with return message
    '''

    logger.info(f"POST Request for "
                f"{metric_data.event_src} Event received with SCID:" 
                f"{metric_data.scid} and metric: {metric_data.event_name}")
    
    #Append alert queue with metric data
    await add_event(metric_data)

    return {"message": f"Received item with scid: {metric_data.scid} "
            f"and metric: {metric_data.event_name}"}

        
@event_mgr_router.get("/get_all_data")
async def get_all_data() -> dict:
    '''
    Get Request to get all data from all tables in database
    Inputs:
        N/A
    Outputs:
        Dictionary of Query Results or Errors
    '''

    try:
        #Method to get all data from DB Handler
        data = db_handler.get_all_data()
        return {"data" : data}
    
    except Exception as e:
        logger.error(f"No Data Availible due to {e}")
        return {"data": f"No Data Availible due to {e}"}
    
@event_mgr_router.get("/get_latest_entry")
async def get_latest_entry():
    #Get Latest Entry in Database from Nominal Database
    

    try:

        data = db_handler.get_latest_id()
        return {"data": data}
    except Exception as e:
        logger.error(f"No Data Availible due to {e}")
        return {"data": f"No Data Availible due to {e}"}


@event_mgr_router.get("/get_event_data")
async def get_event_data(event_name : str,scid:int = None, 
                         cat3flg:bool = False) -> dict:
    '''
    Endpoint to get scid and event specific data
    Inputs:
        scid(integer) - payload id of interest to query
        event_name(string) - specific event name to query
    Outputs:
        Dictionary of Query Results or Errors
    '''

    try:
        if cat3flg:
            data = db_handler_cat3.get_event_data(event_name, scid)
        else:
            data = db_handler.get_event_data(event_name, scid)
        return {"data" : data}
    
    except Exception as e:
        logger.error(f"No Data Availible due to {e}")
        return {"data": f"No Data Availible due to {e}"}
    
#Endpoint Analysis from SPARK
@event_mgr_router.post("/spark_endpoint")
async def get_spark_request(spark_request: SparkRequest) -> None:
    '''
    Post Request from SPARK to update event entry for given ID
    Inputs:
        Post Request Message in JSON with the following fields:
        job_id: int
        url: str
        spark_id: int
    Outputs:
        N/A
    '''
 
    logger.info(f'Recieved Request from SPARK {spark_request}')

    #Check if returned job is is negative, to determine which database to update
    try:
        if spark_request.job_id < 0:
            db_handler_cat3.update_column_by_id(spark_request.job_id*-1, 
                                                'spark_report_id', 
                                                spark_request.spark_id)
        else:
            db_handler.update_column_by_id(spark_request.job_id,
                                           'spark_report_id', 
                                           spark_request.spark_id)
        
        job_success_msg = (f'Updated Unique Index {spark_request.job_id} '
                           f'to SPARK ReportID {spark_request.spark_id}')
        logger.info(job_success_msg)
        return {"message" : job_success_msg}
    
    except Exception as e:
        job_fail_msg = (f'Issues with updating Unique Index '
                        f'{spark_request.job_id} '
                        f'to SPARK ReportID {spark_request.spark_id}')
        logger.error(job_fail_msg)
        return {'message': job_fail_msg}
    

@event_mgr_router.on_event("shutdown")
async def shutdown_event() -> None:
    '''
    Endpoint to shutdown EventManager_API and to stop the threads gracefully
    Inputs:
        Keyboard Interrupt (Ctrl+C)
    Outputs:
        N/A
    '''
    global KEEP_POLLING, EUREKA_FLG
    logger.info(f'EventManager_API Shut down event triggered, exiting threads')
    # Signal the thread to exit
    await add_event(None)  
    KEEP_POLLING = False
    
    logger.info("Application Shut Down")
         



