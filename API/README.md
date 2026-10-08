  # API Directory Structure

  - **main.py**: Main Application for EventManager_API, source that gets compiled with Pyinstaller
  - **api_config.json**: Input Config for main.py
  - **src**: Directory of support source code for EventManager_API
    - **DB_Handler**: Class for interacting with database
    - **models.py**: FastAPI model definitions
    - **routes.py**: Endpoint definitions
    - **Spark_Manager.py**: Module to handle sending jobs to Spark
    - **utils.py**: Support utility functions used by EventManager_API

# Config File Parameter Description 
EventManager_API must be ran with an api_config.json file located in the same directory or child directory from where the main.exe file is located

### Config File Params
 - **LOG_DIR**: Directory path of where to dump logs
 - **DB_URL**: Database url for event alert storage (PostGreSQL, Oracle, SQLite)
 - **IP**: IP address to use for EventManager_API application
 - **PORT**: Port number to use for EventManager_API application
 - **SPARK_URI**: URL address to send jobs to SPARK application
 - **ORGINS**: List of addresses to provide to CORS Middleware for data querying from EventManager_API
 - **DB_POLL_LIST**: List of applications to use for the DB polling processing thread
 - **DB_POLL_RATE**: Time in seconds on how often to poll for new events in the DB polling processing thread
 - **DATA_QUEUE_POLL_RATE**: Time in seconds on how often to check for new events in queue in the data ingestion processing thread
 - **EUREKA_FLG**: Flag to whether register EventManger_API with Eureka server (0 = Not Register, 1 = Register)
 - **EUREKA_SERVER**: URL address to Eureka Server to register EventManager_API with
 - **APP_NAME**: Application Name to register with Eureka
 - **INSTANCE_ID**: Instance ID for Eureka
 - **HEARTBEAT_INTERVAL**: How often to send heartbeat to Eureka server in seconds

 ### Sample api_config.json file
 ```
 {"LOG_DIR": "logs",
 "DB_URL": "postgresql+psycopg2://event_mgr:event_mgr@localhost/events_db",
 "IP": "ITE00647722",
 "PORT": 8001,
 "SPARK_URI": "http://localhost:8002/api/analysis",
 "ORGINS": "http://ITE05019054:4000",
 "DB_POLL_LIST": ["ecql"],
 "DB_POLL_RATE": 10,
 "DATA_QUEUE_POLL_RATE": 3, 
 "EUREKA_FLG": 1,
 "EUREKA_SERVER": "http://localhost:8761",
 "APP_NAME": "event-mgr",
 "INSTANCE_ID": "event-mgr", 
 "HEARTBEAT_INTERVAL": 30.0
}
 ```
