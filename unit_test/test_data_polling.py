
import os
import logging
from logging.handlers import RotatingFileHandler 
from pathlib import Path
import unittest
from ECQL_Emulator.ECQL_emulator import add_ecql_event
from requests import get as get_request
from time import sleep
from requests import codes
from unittest_logger import logger

class Test_DataPolling(unittest.TestCase):

    def setUp(self):
        #Test Configuration

        #Application Endpoints
        self.fastapi_test_endpoint = "http://localhost:8001/event/submit"
        self.db_endpoint = "http://localhost:8001/get_event_data"
       
        #Test Cases
        self.test_case5 = {'scid': 34,
                           'event_idx' : 22,
                           'event_name' : 'DATAPOLLING',
                           'event_rule' : 'datapolling'}

    def test_data_polling(self):
        #Verify that EventManager can detect new events being flagged by CAT3 
        # applications using data polling processing which independently store 
        # data into databases.

        #Have ECQL Emulator store data into CAT3 database 
        add_ecql_event(self.test_case5['scid'], 
                       self.test_case5['event_idx'], 
                       event_name= self.test_case5['event_name'], 
                       event_rule= self.test_case5['event_rule'])


        #Give EventManager some buffer to find new database entry        
        sleep(15)
        
        #Make a get request to EventManager to get the latest database entry which should be test case 5
        response = get_request(
            (f"{self.db_endpoint}?event_name={self.test_case5['event_name']}"
             f"&cat3flg=1"))

        #Extract data from response
        data = response.json()
        data = data['data'][-1]
       
        #Verify Expected Response Status Code
        result = self.assertEqual(response.status_code, codes.ok)
        logger.info(
            f"TestCase5 Event DB Query Status Message Failure : {result}")  

        #Verify that EventManager was able to detect the entry provided by CAT3 
        # application and set spark_report_id to a negative number

        result = self.assertLess(data['spark_report_id'], 0) 
        logger.info(f"TestCase5 negative SPARK ID entry Failure : {result}")  
            

if __name__ == "__main__":
    unittest.main()


