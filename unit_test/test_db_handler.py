
import os
import logging
from logging.handlers import RotatingFileHandler 
from pathlib import Path
import unittest
from Event_Emulator.event_sim import send_event_request
from requests import get as get_request
from time import sleep
from requests import codes
from unittest_logger import logger

class Test_DataHandler(unittest.TestCase):

    def setUp(self):
        #Test Configuration

        #Application Endpoint
        self.fastapi_test_endpoint = "http://localhost:8001/event/submit"
        self.db_endpoint = "http://localhost:8001/get_event_data"
       

        self.test_case3 = {'scid': 50,
        'event_name' : 'DBHANDLER_UNITTEST',
        'event_src' : 'DBHANDLER',
        'spark_script' : 'db_handler'}

    def test_db_handler(self):
        #Verify the database handler stored the test case data as expected by
        # sending a post request to EventManager and using the get request to
        # retrieve data from database

        #Send Test Case Post Request to Event Manager API
        response = send_event_request(self.fastapi_test_endpoint, 
                                        manual_request = self.test_case3)

        #Verify Expected Response Status Code
        result = self.assertEqual(response.status_code, codes.ok)
        logger.info(f"TestCase3 Event Request Status Code Failure : {result}")

        #Verify Expected Response Message
        result = self.assertEqual(response.json(), 
                         {"message": (f"Received item with scid: " 
                                      f"{self.test_case3['scid']} and metric: "
                                      f"{self.test_case3['event_name']}")})
        
        logger.info(
            f"TestCase3 Event Request Status Message Failure : {result}") 

        #Give EventManager some buffer time to store data
        sleep(10)

        #Make a get request to EventManager to get the latest database entry which should be test case 3
        response = get_request(
            f"{self.db_endpoint}?event_name={self.test_case3['event_name']}")

        #Extract data from response
        data = response.json()
        data = data['data'][-1]

        #Verify Expected Response Status Code
        result = self.assertEqual(response.status_code, codes.ok)
        logger.info(
            f"TestCase3 Event DB Query Status Message Failure : {result}")  

        #Compare expected keys in test case to results of the EventManager Query
        for field in self.test_case3:
            result = self.assertEqual(self.test_case3[field], 
                             data[field])
            logger.info(
                f"TestCase3 field, {field}, compare failure : {result} ")

if __name__ == "__main__":
    unittest.main()


