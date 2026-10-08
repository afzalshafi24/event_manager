################################################################################
##
##         Copyright 2026 Northrop Grumman Systems Corporation
##
## DISTRIBUTION STATEMENT D: Distribution authorized to Department of Defense
## (DoD) and United States (U.S.) DoD contractors only. Reason: Critical
## Technology. Date of Determination: 7 December 98. Other requests shall be
## referred to SMC/RSL.
##
## WARNING: This data is subject to the controls of the Arms Export Control
## Act (Title 22 U.S.C. Sec. 2751 et seq.). The implementing regulation for
## this statute is the International Traffic in Arms Regulations (ITAR)
## (22 C.F.R. 120-130). It may not be transferred, either in its original form,
## derivative documents, or after being incorporated into other data, without
## first obtaining approval from the U.S. government or as otherwise authorized
## by U.S. law and regulations.
##
## DESTRUCTION NOTICE: For classified documents, follow the procedures in DoD
## 5220.22-M, National Industrial Security Program Operating Manual (NISPOM),
## Section 7, or DoD 5200.1R, Information Security Program Regulations,
## Chapter 6, Section 7. For unclassified, limited distribution documents,
## destroy by any method that will prevent disclosure of contents or
## reconstruction of the document.
##
## EXPORT CONTROLLED: This document contains data whose export/transfer/
## disclosure is restricted by U.S. law. Dissemination to non-U.S. persons
## whether in the United States or abroad requires an export license or other
## authorization. This data may not be transferred, either in its original
## form, derivative documents, or after being incorporated into other data,
## without first obtaining approval from the U.S. Government or as otherwise
## authorized by U.S. law and regulations.
##
################################################################################
##
## Revision:
## Date         Author          CR/DR               Comment
## 2026/03/02   Afzal Shafi     SEITSRB-570         Initial Release
################################################################################
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import sys
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


#Time String Format
TIME_STR_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_STR_FORMAT_A = "%d-%b-%Y %H:%M:%S"

Base  = declarative_base()


class eventData(Base):
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
        self.logger = logging.getLogger(__name__)
        self.logger.info(f'Using DB address : {self.db_url}')
        self.engine = create_engine(self.db_url)

    def create_session(self):
        #Create Session from engine 
        Session = sessionmaker(bind=self.engine)
        return Session()
    
    def store_data(self, metric_data):
        #Stores a row of data into database of a given database
    
        #Create Session
        session = self.create_session()

        # Create database model with metric_data
        event_data_insert = eventData(unique_index = metric_data.unique_index,
                                    scid= metric_data.scid,
                                    event_time=metric_data.event_time,
                                    event_rule_id= metric_data.event_rule_id,
                                    event_name=metric_data.event_name,
                                    event_rule=metric_data.event_rule,
                                    event_src=metric_data.event_src,
                                    spark_script=metric_data.spark_script,
                                    spark_report_id= None,
                                    gem_full_path= metric_data.gem_full_path)
        

        
        # Add the new instance to the session
        session.add(event_data_insert)

        # Commit the session to save the data to the database
        session.commit()

        # Close the session
        session.close()

    def get_latest_entry(self):
        #Create Session
        session = self.create_session()
        latest_entry = (session.query(eventData)
                        .order_by(eventData.unique_index.desc()).first())

        session.close()
        return latest_entry
################################################################################
##
##         Copyright 2026 Northrop Grumman Systems Corporation
##
##                  Contract Number:  FA8823-21-C-0001
##                   Subcontract Number:  4105055110
##
################################################################################

