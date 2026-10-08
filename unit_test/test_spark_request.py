
import unittest
from requests import get as get_request
from requests import post as post_request
from requests import codes 
from Event_Emulator.event_sim import send_event_request
from time import sleep
from unittest_logger import logger

class Test_SparkRequest(unittest.TestCase):

    def setUp(self):
        #Test Configuration

        #Application Endpoints
        self.fastapi_test_endpoint = "http://localhost:8001/event/submit"
        self.spark_test_endpoint = "http://localhost:8001/spark_endpoint"
        self.db_endpoint = "http://localhost:8001/get_event_data"

    

        self.test_case4 = {'scid': 24,
        'event_name' : 'SPARK_TEST',
        'event_src' : 'SPARK_UNITTEST',
        'spark_script' : 'spark_input_unittest'}

        self.spark_id = 24

    def test_spark_request(self):
        #Verify the EventManager interface with SPARK

        #Send Test Case Post Request to Event Manager API
        response = send_event_request(self.fastapi_test_endpoint, 
                                        manual_request = self.test_case4)
        sleep(10)

        #Verify Expected Response Status Code
        result = self.assertEqual(response.status_code, codes.ok)
        logger.info(f"TestCase4 Event Request Status Code Failure : {result}")
        
        #Verify Expected Response Message
        result = self.assertEqual(response.json(), 
                         {"message": (f"Received item with scid: " 
                                      f"{self.test_case4['scid']} and metric: "
                                      f"{self.test_case4['event_name']}")})
        logger.info(
            f"TestCase4 Event Request Status Message Failure : {result}") 
        
        
        #Make a get request to EventManager to get the latest database entry 
        # which should be test case 4
        response = get_request(
            f"{self.db_endpoint}?event_name={self.test_case4['event_name']}")
        
        #Verify Expected Response Status Code
        result = self.assertEqual(response.status_code, codes.ok)
        logger.info(
            f"TestCase4 Event DB Query Status Message Failure : {result}")  

        #Extract data from response, and get report id
        data = response.json()
        job_id = data['data'][-1]['unique_index']

        #Send Post Request to EventManager to update SPARK ReportID
        response = post_request(self.spark_test_endpoint, 
                                json={'job_id': job_id, 
                                      'url': "spark_unittest", 
                                      'spark_id': self.spark_id})
        
        #Verify Expected Response Status Code
        result = self.assertEqual(response.status_code, codes.ok)
        logger.info(f"TestCase4 SPARK Request Status Code Failure : {result}")

        #Check database value to see if spark report ID matches as expected
        #Make a get request to EventManager to get the latest database entry 
        # which should be test case 4
        response = get_request(
            f"{self.db_endpoint}?event_name={self.test_case4['event_name']}")
        
        #Verify Expected Response Status Code
        result = self.assertEqual(response.status_code, codes.ok)
        logger.info(
            f"TestCase4 Event DB Query Status Message Failure : {result}")  

        #Extract data from response, and get report id
        data = response.json()
        
        #Verify spark id matches as expected
        result = self.assertEqual(
            self.spark_id,data['data'][-1]['spark_report_id'])
        logger.info(
            f"TestCase4 SPARK ID verification failure : {result}")  

if __name__ == "__main__":
    unittest.main()



