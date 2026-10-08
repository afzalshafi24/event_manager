import json
import logging


class EventManagerConfig():
    def __init__(self):
        self.cfg_file = 'api_config.json'
    
        self.log_level_mapping = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }

        #Read Config file
        self.read_event_mgr_config()

        #Load Config Params
        self.load_config()

    def read_event_mgr_config(self):
        #Reads in the EventManager config file
        #Open config file and extract params:
    
        #Read in JSON config file
        with open(self.cfg_file, 'r') as file:
            #Load the JSON file
            self.cfg_data = json.load(file)
    
    def load_config(self):
        #Load Config into class attributes 
        for field in self.cfg_data:
            setattr(self, field, self.cfg_data[field])
        
        

    
    