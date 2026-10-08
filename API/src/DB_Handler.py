
from sqlalchemy import create_engine, distinct, inspect
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import sys
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, DateTime, Integer


#Time String Format
TIME_STR_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_STR_FORMAT_A = "%d-%b-%Y %H:%M:%S"

Base  = declarative_base()

# Define the Event Data DB model
class eventData(Base):
    __tablename__ = 'event_alerts'
    unique_index = Column(Integer, primary_key=True, autoincrement=True)
    scid = Column(Integer, nullable=False)
    event_time = Column(DateTime, nullable=False)
    event_rule_id = Column(Integer, nullable=True)
    event_name = Column(String, nullable=False)
    event_rule = Column(String, nullable=False)
    event_src = Column(String, nullable=False)
    spark_script = Column(String, nullable=True)
    spark_report_id = Column(Integer, nullable=True)
    gem_full_path = Column(String, nullable=True)

class eventData_cat3(Base):
    __tablename__ = 'ecql'
    unique_index = Column(Integer, primary_key=True)
    scid = Column(Integer, nullable=False)
    event_time = Column(String(255), nullable=False)
    event_rule_id = Column(Integer, nullable=False)
    event_name = Column(String(255), nullable=False)
    event_rule = Column(String, nullable=False)
    event_src = Column(String(255), nullable=False)
    spark_script = Column(String)  # Nullable
    spark_report_id = Column(Integer)  # Nullable
    gem_full_path = Column(String(255))  # Nullable

class DB_Handler():
    def __init__(self, db_url) :
        #Store db file
        self.db_url = db_url
        
      
    def initialize_database(self, create_flg=False, cat3db_flg=False):
        #Initializes DB
        self.engine = create_engine(self.db_url)

        #Initializes Logging
        self.logger = logging.getLogger(__name__)
        self.logger.info(f'Using DB address : {self.db_url}')

        if cat3db_flg:
            self.db_model = eventData_cat3
        else:
            self.db_model = eventData
        
        if create_flg:
            Base.metadata.create_all(self.engine)

        self.logger.info(f"Database {self.db_url} " 
                         f"initialized with given tables")

    def store_data(self, metric_data):
        #Stores a row of data into database of a given database
    
        #Create Session
        session = self.create_session()

        #Get Datetime Object
        dt_object = self.get_dt_object(metric_data.event_time)

        # Create a new instance of the Metrics model by source
        event_data_insert = eventData(scid= metric_data.scid,
                                       event_time=dt_object,
                                       event_rule_id= metric_data.event_rule_id,
                                       event_name=metric_data.event_name,
                                       event_rule=metric_data.event_rule,
                                       event_src=metric_data.event_src,
                                       spark_script=metric_data.spark_script,
                                       gem_full_path= metric_data.gem_full_path)

        
        # Add the new instance to the session
        session.add(event_data_insert)

        # Commit the session to save the data to the database
        session.commit()

        #Extract unique_index
        unique_index = event_data_insert.unique_index
        
        # Close the session
        session.close()

        #Return unique_index
        return unique_index
    
 
    def get_dt_object(self, start_time):
         # Convert the time string to a datetime object
        try:
            dt_object = datetime.strptime(start_time, TIME_STR_FORMAT)
            self.logger.info(f"Using Time Format {TIME_STR_FORMAT}")
            
        except:
            dt_object = datetime.strptime(start_time, TIME_STR_FORMAT_A)
            self.logger.info(f"Using Time Format {TIME_STR_FORMAT_A}")
             
        return dt_object

    def create_session(self):
        #Create Session from engine 
        Session = sessionmaker(bind=self.engine)
        return Session()
        

    def get_event_data(self, event_name: str, scid: int = None):
        #Get Data for a given scid

        #Create Session
        session = self.create_session()

        if scid is None:
            #Query Data based off event name only
            data = (session.query(self.db_model)
                    .filter(self.db_model.event_name == event_name)
                    .all())
        else:
            #Query Data based off scid as well
            data = (session.query(self.db_model)
                    .filter(self.db_model.scid == scid,
                            self.db_model.event_name == event_name).all())
        
        #Close session
        session.close()

        return self.format_query_results(data)
    
    def get_data_by_time(self, scid:int, metric_name:str,
                         start_time:datetime, end_time:datetime):
        #Query data by time window

        # Convert to datetime for querying
        start_datetime_str = datetime.combine(start_time, datetime.min.time())
        end_datetime_str = datetime.combine(end_time, datetime.max.time())

        #Create Session
        session = self.create_session()

        #Query Data based off scid, metric, and time window
        data = session.query(self.db_model).filter(
        self.db_model.datetime.between(start_datetime_str, end_datetime_str),
        self.db_model.metric_name == metric_name,
        self.db_model.scid == scid).all()

        #Close Session
        session.close()

        return data
    
    def get_latest_id(self):
        #Get the latest job_id 

        #Create Session
        session = self.create_session()

        #Query Table for latest unique index
        last_id = (session.query(self.db_model)
                   .order_by(self.db_model.unique_index.desc()).first())

        if last_id is None:
            return 0

        #Close Session
        session.close()

        return last_id.__dict__

    def get_unique_elements(self, col_name, table_name):
        #Get Unique values in a database
        
        #Create Session
        session = self.create_session()

        # Query for unique elements dynamically
        unique_values = (session
                         .query(distinct(getattr(self.db_model, col_name)))
                         .all())

        return [item[0] for item in unique_values]
    

    def update_column_by_id(self, id, col_name, new_value):
        #Updates the new column for given unique_index with the new value

        #Create Session
        session = self.create_session()

         # Query for the entry with the specified ID
        entry = (session.query(self.db_model)
                 .filter(self.db_model.unique_index == id)
                 .first())

        if entry:
            # Update the specific column
            setattr(entry, col_name, new_value)
            session.commit()  # Commit the changes to the database
            self.logger.info(f"Updated entry ID {id} "
               f"{col_name} column with new value: {new_value}")
        else:
            self.logger.warning(f"No entry found with ID {id}")

        #Close Session
        session.close()

    def get_all_data(self):
        #Get All database values for a given table

        #Create Session 
        session = self.create_session()

        data = session.query(self.db_model).all()
        
        return self.format_query_results(data)

    def format_query_results(self, table_data):
        #Format Query Results
        
        event_dict = [event.__dict__ for event in table_data]        

        # Remove the SQLAlchemy internal state
        for event in event_dict:
            event.pop('_sa_instance_state', None)
        return event_dict

    def find_new_events(self, src_name):
        #Find new events for given src that do not have a spark_ID 
        # associated with it
        
        #Create session
        session = self.create_session()

        #Get data by source
        data = (session.query(self.db_model)
                .filter(self.db_model.event_src == src_name, 
                        self.db_model.spark_report_id == None).all())

        session.close()

        return data

    def get_table_names(self):
        #Get a list of table names in given database
        
        #Create an inspector
        inspector = inspect(self.engine)

        #Get list of table names and return it
        table_names = inspector.get_table_names()

        return table_names



