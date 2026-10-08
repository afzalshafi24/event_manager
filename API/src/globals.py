
from .config import EventManagerConfig
from .DB_Handler import DB_Handler


cfg = EventManagerConfig()


#Initialize DB Handler Class
db_handler = DB_Handler(cfg.DB_URL)

#Initialize DB Handler Class for CAT3 Applications
db_handler_cat3 = DB_Handler(cfg.DB_URL_CAT3)

#Initialize polling flag = True used for data polling processing
KEEP_POLLING = True

