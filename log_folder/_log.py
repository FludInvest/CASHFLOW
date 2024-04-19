import logging
import datetime

def add_log(code):
    logging.basicConfig(filename='log_folder/LOG.log',format="%(asctime)s %(levelname)s %(message)s")
    logging.warning(code)

def start_log(code):
    logging.basicConfig(filename='log_folder/LOG.log',level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
    logging.info(code)

