
import logging
import logging.handlers

from settings import *

def create_log():
    
    handler = logging.handlers.RotatingFileHandler(LOG_FILENAME, \
                    maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
    # create console handler and set level to debug
    handler.setLevel(logging.DEBUG)
    # create and set formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # create logger
    main_logger = logging.getLogger("main_logger")
    main_logger.setLevel(logging.DEBUG)
    main_logger.addHandler(handler)
    
    
    analyser_logger = logging.getLogger("analyser_logger")
    analyser_logger.setLevel(logging.DEBUG)
    analyser_logger.addHandler(handler)

