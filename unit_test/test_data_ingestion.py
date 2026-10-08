
import unittest
from Event_Emulator.event_sim import send_event_request
from requests import codes
from unittest_logger import logger

class Test_DataIngestion(unittest.TestCase):

    def setUp(self):
        #Test Configuration SetUp

        #Application Endpoints
        self.fastapi_test_endpoint = "http://localhost:8001/event/submit"

        #Test Cases
        self.test_case1 = {'scid': 1,
        'event_name' : 'VoltageFault',
        'event_src' : 'ConstellationTracker',
        'spark_script' : 'EE_wrapper2'}

        
        self.test_case2 = {'scid': "hello",
        'event_name' : 'BadCollect',
        'event_src' : 'ASTRA',
        'spark_script' : 'plot_collects'}


    def test_a_nominal_data_ingestion(self):
        #Send Test Case Post Request to Event Manager API
        response = send_event_request(self.fastapi_test_endpoint, 
                                      manual_request = self.test_case1)
        
        #Verify Expected Response Status Code
        result = self.assertEqual(response.status_code, codes.ok)
        logger.info(f"TestCase1 Event Request Status Code Failure : {result}")

        #Verify Expected Response Message
        result = self.assertEqual(response.json(), 
                         {"message": (f"Received item with scid: "
                                      f"{self.test_case1['scid']} and " 
                                      f"metric: "
                                      f"{self.test_case1['event_name']}")})
        
        logger.info(
            f"TestCase1 Event Request Status Message Failure : {result}")  

    def test_b_bad_data_ingestion(self):
        #Send Bad Data to see if we get a json response code = 422
        response = send_event_request(self.fastapi_test_endpoint, 
                                        manual_request = self.test_case2)
        
        #Verify Expected Response Status Code
        result = self.assertEqual(
            response.status_code, codes.unprocessable_entity)
        
        logger.info(
            f"TestCase1 Failed Event Request Status Code Failure : {result}")  
   
if __name__ == "__main__":
    unittest.main()



