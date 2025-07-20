import logging
import os
from datetime import datetime

LOG_FILE= os.getcwd()+os.getenv("LOG_FILE", ".\\app.log")+"_"+datetime.now().strftime("%Y_%m_%d") + ".log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(level=logging.INFO,filemode="a" ,filename=LOG_FILE,format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s")